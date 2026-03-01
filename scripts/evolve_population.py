#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_match
from sim.metrics import composite_profiles, composite_score, first_place_rate, robustness_score


@dataclass
class Candidate:
    family: str
    params: dict[str, float | int]

    @property
    def spec(self) -> str:
        if not self.params:
            return self.family
        body = ",".join(f"{k}={self.params[k]}" for k in sorted(self.params))
        return f"{self.family}:{body}"


def _sample_candidate(rng: random.Random) -> Candidate:
    family = rng.choice(["prob_value", "risk_sniper", "seller_extraction"])
    if family == "prob_value":
        params = {
            "bid_scale": round(rng.uniform(0.75, 1.35), 3),
            "sell_count": rng.choice([1, 2]),
            "damage_weight": round(rng.uniform(0.4, 1.4), 3),
            "market_weight": round(rng.uniform(0.5, 1.6), 3),
            "aggression_weight": round(rng.uniform(0.2, 1.1), 3),
            "stack_cap_fraction": round(rng.uniform(0.35, 0.8), 3),
            "min_delta_to_bid": rng.randrange(100, 2001, 100),
        }
    elif family == "risk_sniper":
        params = {
            "bid_scale": round(rng.uniform(0.65, 1.2), 3),
            "trigger_delta": rng.randrange(1000, 4601, 100),
            "late_round_bonus": round(rng.uniform(0.0, 0.9), 3),
            "stack_cap_fraction": round(rng.uniform(0.25, 0.6), 3),
            "sell_count": rng.choice([1, 2]),
        }
    else:
        params = {
            "sell_count": rng.choice([1, 2]),
            "reserve_bid_floor": round(rng.uniform(0.02, 0.22), 3),
            "opportunistic_delta": rng.randrange(1600, 5201, 100),
        }
    return Candidate(family=family, params=params)


def _mutate(parent: Candidate, rng: random.Random) -> Candidate:
    params = dict(parent.params)
    key = rng.choice(list(params.keys()))
    if key in {"sell_count"}:
        params[key] = 1 if int(params[key]) == 2 else 2
    elif key.endswith("_delta") or key == "trigger_delta" or key == "min_delta_to_bid":
        shift = rng.choice([-300, -200, -100, 100, 200, 300])
        params[key] = max(0, int(params[key]) + shift)
    else:
        mult = rng.uniform(0.85, 1.15)
        params[key] = round(float(params[key]) * mult, 3)
    return Candidate(family=parent.family, params=params)


def _objective_key(objective: str) -> str:
    if objective == "first_place":
        return "first_place_rate"
    if objective == "robustness":
        return "robustness"
    return "expected_pnl"


def _evaluate(
    candidate: Candidate,
    *,
    baseline_pool: list[str],
    n_matches: int,
    n_games_per_match: int,
    rule_profile: str,
    seed: int,
    objective: str,
    correlation: CorrelationModel,
) -> dict:
    if len(baseline_pool) < 4:
        raise ValueError("Need at least 4 baseline strategies for candidate evaluation")

    rng = random.Random(seed)
    cand_pnls: list[float] = []
    cand_ranks: list[int] = []

    for _ in range(n_matches):
        opponents = rng.sample(baseline_pool, 4)
        seats = [candidate.spec, *opponents]
        rng.shuffle(seats)
        out = run_match(
            seats,
            n_games=n_games_per_match,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile=rule_profile,
            objective=objective,
            correlation=correlation,
        )
        cand_seat = out["strategy_tags"].index(candidate.spec)
        for game in out["games"]:
            cand_pnls.append(float(game["pnl"][cand_seat]))
            cand_ranks.append(int(game["rk"][cand_seat]))

    expected_pnl = mean(cand_pnls) if cand_pnls else 0.0
    first_place = first_place_rate(cand_ranks)
    robustness = robustness_score(cand_pnls)
    composites = {
        name: composite_score(expected_pnl, first_place, robustness, weights)
        for name, weights in composite_profiles().items()
    }
    return {
        "tag": candidate.spec,
        "samples": len(cand_pnls),
        "expected_pnl": expected_pnl,
        "first_place_rate": first_place,
        "robustness": robustness,
        "composites": composites,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Evolutionary search for Sold 'Em strategy specs")
    ap.add_argument("--generations", type=int, default=4)
    ap.add_argument("--population-size", type=int, default=10)
    ap.add_argument("--survivors", type=int, default=3)
    ap.add_argument("--n-matches", type=int, default=70)
    ap.add_argument("--n-games-per-match", type=int, default=10)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--objective", default="ev")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    ap.add_argument("--correlation-mode", default="none")
    ap.add_argument("--correlation-strength", type=float, default=0.0)
    ap.add_argument("--correlation-pairs", default="")
    ap.add_argument(
        "--baseline-spec",
        action="append",
        default=[],
        help="Additional strategy spec to include in baseline pool (repeatable)",
    )
    ap.add_argument(
        "--baseline-file",
        default="",
        help="Text file with one strategy spec per line to include in baseline pool",
    )
    ap.add_argument(
        "--replace-default-baseline",
        action="store_true",
        help="Use only provided baseline specs (from --baseline-spec/--baseline-file)",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "evolution_runs.jsonl"
    summary_path = out_dir / "evolution_summary.json"

    correlation_pairs: list[tuple[int, int]] = []
    if args.correlation_pairs.strip():
        for part in args.correlation_pairs.split(","):
            a, b = part.split("-")
            correlation_pairs.append((int(a), int(b)))
    correlation = CorrelationModel(
        mode=args.correlation_mode,
        strength=args.correlation_strength,
        pairs=correlation_pairs,
    )

    rng = random.Random(args.seed)
    baseline_pool = [
        "random",
        "pot_fraction",
        "delta_value",
        "conservative",
        "bully",
        "seller_profit",
        "adaptive_profile",
    ]
    if args.replace_default_baseline:
        baseline_pool = []
    if args.baseline_file:
        path = Path(args.baseline_file)
        if not path.exists():
            raise FileNotFoundError(f"Baseline file not found: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            spec = line.strip()
            if not spec or spec.startswith("#"):
                continue
            baseline_pool.append(spec)
    if args.baseline_spec:
        baseline_pool.extend(spec.strip() for spec in args.baseline_spec if spec.strip())
    # Stable de-dup preserving order.
    dedup: list[str] = []
    seen: set[str] = set()
    for spec in baseline_pool:
        if spec in seen:
            continue
        seen.add(spec)
        dedup.append(spec)
    baseline_pool = dedup
    if len(baseline_pool) < 4:
        raise ValueError("Baseline pool must contain at least 4 unique strategy specs")
    key = _objective_key(args.objective)
    all_rows: list[dict] = []
    survivors: list[Candidate] = []

    with open(jsonl_path, "w", encoding="utf-8") as out:
        eval_idx = 0
        for gen in range(args.generations):
            candidates: list[Candidate] = []
            if gen == 0 or not survivors:
                while len(candidates) < args.population_size:
                    candidates.append(_sample_candidate(rng))
            else:
                while len(candidates) < args.population_size:
                    parent = rng.choice(survivors)
                    if rng.random() < 0.2:
                        candidates.append(_sample_candidate(rng))
                    else:
                        candidates.append(_mutate(parent, rng))

            scored: list[tuple[float, Candidate, dict]] = []
            for cand in candidates:
                seed = args.seed + (gen * 10_000) + eval_idx
                eval_idx += 1
                row = _evaluate(
                    cand,
                    baseline_pool=baseline_pool,
                    n_matches=args.n_matches,
                    n_games_per_match=args.n_games_per_match,
                    rule_profile=args.rule_profile,
                    seed=seed,
                    objective=args.objective,
                    correlation=correlation,
                )
                row_record = {
                    "generation": gen,
                    "seed": seed,
                    "objective": args.objective,
                    "rule_profile": args.rule_profile,
                    "candidate": cand.spec,
                    "metrics": row,
                }
                out.write(json.dumps(row_record, separators=(",", ":")) + "\n")
                all_rows.append(row_record)
                scored.append((float(row[key]), cand, row))

            scored.sort(key=lambda t: t[0], reverse=True)
            survivors = [cand for _, cand, _ in scored[: max(1, args.survivors)]]

    top_rows = sorted(all_rows, key=lambda r: float(r["metrics"][key]), reverse=True)[:10]
    summary = {
        "objective": args.objective,
        "metric_key": key,
        "generations": args.generations,
        "population_size": args.population_size,
        "survivors": args.survivors,
        "n_matches": args.n_matches,
        "n_games_per_match": args.n_games_per_match,
        "rule_profile": args.rule_profile,
        "correlation": {
            "mode": correlation.mode,
            "strength": correlation.strength,
            "pairs": correlation.pairs,
        },
        "baseline_pool": baseline_pool,
        "top_candidates": top_rows,
        "jsonl_path": str(jsonl_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
