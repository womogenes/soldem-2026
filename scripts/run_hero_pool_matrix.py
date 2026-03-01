#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.metrics import first_place_rate, robustness_score
from sim.opponent_models import CorrelationModel
from sim.runner import run_match


@dataclass(frozen=True)
class Scenario:
    objective: str
    horizon: int
    corr_mode: str
    corr_strength: float
    pairs: tuple[tuple[int, int], ...]
    replicate: int
    seed: int


def _spec_tag(spec: str) -> str:
    base = spec.split("|")[0]
    for part in spec.split("|")[1:]:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == "tag":
            return v.strip()
    return base


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _std(xs: list[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _sem(xs: list[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    return _std(xs) / (len(xs) ** 0.5)


def _ci95(xs: list[float]) -> tuple[float, float]:
    m = _mean(xs)
    e = 1.96 * _sem(xs)
    return (m - e, m + e)


def _parse_weighted(raw_items: list[str]) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for item in raw_items:
        if ":" in item:
            spec, w = item.rsplit(":", 1)
            try:
                wt = float(w)
            except ValueError:
                wt = 1.0
            out.append((spec, max(0.0, wt)))
        else:
            out.append((item, 1.0))
    return out


def _weighted_sample(
    rng: random.Random, pool: list[tuple[str, float]], k: int, exclude: str
) -> list[str]:
    specs = [s for s, _ in pool if s != exclude]
    weights = [w for s, w in pool if s != exclude]
    if not specs:
        return [exclude] * k
    return rng.choices(specs, weights=weights, k=k)


def run_eval(
    scenario: Scenario,
    hero_spec: str,
    pool: list[tuple[str, float]],
    n_matches: int,
    rule_profile: str,
) -> dict:
    rng = random.Random(scenario.seed + (hash(hero_spec) % 100000))
    corr = CorrelationModel(
        mode=scenario.corr_mode,
        strength=scenario.corr_strength,
        pairs=list(scenario.pairs),
    )

    hero_tag = _spec_tag(hero_spec)
    hero_pnl: list[float] = []
    hero_rank: list[int] = []

    for _ in range(n_matches):
        opponents = _weighted_sample(rng, pool, k=4, exclude=hero_spec)
        lineup = list(opponents) + [hero_spec]
        rng.shuffle(lineup)
        hero_seat = lineup.index(hero_spec)
        out = run_match(
            lineup,
            n_games=scenario.horizon,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile=rule_profile,
            objective=scenario.objective,
            correlation=corr,
        )
        for g in out["games"]:
            hero_pnl.append(float(g["pnl"][hero_seat]))
            hero_rank.append(int(g["rk"][hero_seat]))

    return {
        "scenario": {
            "objective": scenario.objective,
            "horizon": scenario.horizon,
            "corr_mode": scenario.corr_mode,
            "corr_strength": scenario.corr_strength,
            "pairs": list(scenario.pairs),
            "replicate": scenario.replicate,
            "seed": scenario.seed,
            "n_matches": n_matches,
            "rule_profile": rule_profile,
        },
        "hero_spec": hero_spec,
        "hero_tag": hero_tag,
        "expected_pnl": _mean(hero_pnl),
        "first_place_rate": first_place_rate(hero_rank),
        "robustness": robustness_score(hero_pnl),
        "samples": len(hero_pnl),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Hero-vs-human-pool matrix for day-of strategy selection")
    ap.add_argument("--n-matches", type=int, default=140)
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--seed", type=int, default=12000)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    ap.add_argument("--objectives", nargs="*", default=["ev", "first_place", "robustness"])
    ap.add_argument("--horizons", nargs="*", type=int, default=[10])
    ap.add_argument("--corr-modes", nargs="*", default=["none", "respect", "herd", "kingmaker"])
    ap.add_argument(
        "--candidates",
        nargs="*",
        default=[
            "conservative",
            "meta_switch_soft",
            "meta_switch",
            "level_k",
            "level_k_l3",
            "level_k|level=2|l0_fraction=0.28|tag=levelk_base",
            "level_k|level=3|l0_fraction=0.258|tag=levelk_42207",
            "level_k|level=2|l0_fraction=0.309|tag=levelk_207605",
            "level_k|level=3|l0_fraction=0.268|tag=levelk_926417",
            "bully",
            "pot_fraction",
        ],
    )
    ap.add_argument(
        "--pool",
        nargs="*",
        default=[
            "conservative:2.0",
            "adaptive_profile:1.7",
            "level_k:1.6",
            "level_k_l3:1.3",
            "meta_switch_soft:1.2",
            "bully:1.0",
            "pot_fraction:0.9",
            "seller_profit:0.8",
            "quantal_response:0.7",
            "random:0.3",
        ],
    )
    args = ap.parse_args()

    pool = _parse_weighted(args.pool)
    corr_catalog = [
        ("none", 0.0, ()),
        ("respect", 0.35, ((1, 2),)),
        ("herd", 0.30, ((3, 4),)),
        ("kingmaker", 0.35, ((0, 1), (2, 3))),
    ]
    corrs = [x for x in corr_catalog if x[0] in set(args.corr_modes)]
    if not corrs:
        raise ValueError("No valid correlation modes selected")

    scenarios: list[Scenario] = []
    seed = args.seed
    for objective in args.objectives:
        for horizon in args.horizons:
            for mode, strength, pairs in corrs:
                for rep in range(args.replicates):
                    seed += 1
                    scenarios.append(
                        Scenario(
                            objective=objective,
                            horizon=horizon,
                            corr_mode=mode,
                            corr_strength=strength,
                            pairs=tuple(pairs),
                            replicate=rep,
                            seed=seed,
                        )
                    )

    jobs = [(s, c) for s in scenarios for c in args.candidates]

    rows = []
    total = len(jobs)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        fut_map = {
            ex.submit(run_eval, s, c, pool, args.n_matches, args.rule_profile): (s, c)
            for s, c in jobs
        }
        done = 0
        for fut in as_completed(fut_map):
            rows.append(fut.result())
            done += 1
            if done % 16 == 0 or done == total:
                print(f"progress {done}/{total}", flush=True)

    grouped = defaultdict(list)
    for r in rows:
        s = r["scenario"]
        key = (s["objective"], s["horizon"], s["corr_mode"])
        grouped[key].append(r)

    scenario_summaries = []
    for key, vals in sorted(grouped.items(), key=lambda kv: kv[0]):
        objective, horizon, corr_mode = key
        metric_key = (
            "expected_pnl"
            if objective == "ev"
            else ("first_place_rate" if objective == "first_place" else "robustness")
        )
        by_hero = defaultdict(list)
        for v in vals:
            by_hero[v["hero_spec"]].append(v[metric_key])

        table = []
        for hero_spec, metrics in by_hero.items():
            lo, hi = _ci95(metrics)
            table.append(
                {
                    "hero_spec": hero_spec,
                    "hero_tag": _spec_tag(hero_spec),
                    "mean_metric": _mean(metrics),
                    "std_metric": _std(metrics),
                    "sem_metric": _sem(metrics),
                    "ci95_low": lo,
                    "ci95_high": hi,
                    "n": len(metrics),
                }
            )
        table.sort(key=lambda r: r["mean_metric"], reverse=True)
        top_mean = table[0]
        top_lcb = max(table, key=lambda r: r["ci95_low"])
        runner = table[1] if len(table) > 1 else None
        margin = top_mean["mean_metric"] - (runner["mean_metric"] if runner else 0.0)

        scenario_summaries.append(
            {
                "rule_profile": args.rule_profile,
                "objective": objective,
                "horizon": horizon,
                "corr_mode": corr_mode,
                "metric_key": metric_key,
                "winner": top_mean["hero_tag"],
                "winner_spec": top_mean["hero_spec"],
                "winner_mean": top_mean["mean_metric"],
                "winner_ci95_low": top_mean["ci95_low"],
                "winner_ci95_high": top_mean["ci95_high"],
                "winner_lcb": top_lcb["hero_tag"],
                "winner_lcb_spec": top_lcb["hero_spec"],
                "winner_lcb_value": top_lcb["ci95_low"],
                "runner_up": runner["hero_tag"] if runner else None,
                "margin": margin,
                "top3": table[:3],
            }
        )

    winner_counts = defaultdict(int)
    winner_lcb_counts = defaultdict(int)
    for s in scenario_summaries:
        winner_counts[s["winner"]] += 1
        winner_lcb_counts[s["winner_lcb"]] += 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"hero_pool_matrix_{ts}.json"
    md_path = out_dir / f"hero_pool_matrix_{ts}.md"
    policy_mean = out_dir / f"hero_pool_policy_{ts}_mean.json"
    policy_lcb = out_dir / f"hero_pool_policy_{ts}_lcb.json"

    payload = {
        "created_at": datetime.now().isoformat(),
        "config": vars(args),
        "pool": pool,
        "winner_counts": dict(sorted(winner_counts.items(), key=lambda kv: kv[1], reverse=True)),
        "winner_lcb_counts": dict(sorted(winner_lcb_counts.items(), key=lambda kv: kv[1], reverse=True)),
        "scenario_summaries": scenario_summaries,
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Hero pool matrix summary",
        "",
        f"Generated at: {datetime.now().isoformat()}",
        "",
        "## Winner counts",
        "",
    ]
    for tag, count in sorted(winner_counts.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {tag}: {count}")
    lines.extend(["", "## Winner counts by lcb", ""])
    for tag, count in sorted(winner_lcb_counts.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {tag}: {count}")
    lines.extend(["", "## Decision table", ""])
    for s in scenario_summaries:
        lines.append(
            f"- {s['rule_profile']} | {s['objective']} | h={s['horizon']} | {s['corr_mode']} -> "
            f"mean:{s['winner']} ({s['metric_key']}={s['winner_mean']:.4f}), lcb:{s['winner_lcb']}"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _build_policy(mode: str) -> dict:
        policy = {"default": {}, "by_condition": {}, "source": str(json_path)}
        for objective in ["ev", "first_place", "robustness"]:
            cand = [
                s
                for s in scenario_summaries
                if s["objective"] == objective and s["horizon"] == 10 and s["corr_mode"] == "none"
            ]
            if cand:
                if mode == "lcb":
                    best = max(cand, key=lambda r: r["winner_lcb_value"])
                    policy["default"][objective] = best["winner_lcb_spec"]
                else:
                    best = max(cand, key=lambda r: r["winner_mean"])
                    policy["default"][objective] = best["winner_spec"]
        for s in scenario_summaries:
            key = f"{s['rule_profile']}|{s['objective']}|h{s['horizon']}|{s['corr_mode']}"
            if mode == "lcb":
                winner = s["winner_lcb"]
                winner_spec = s["winner_lcb_spec"]
            else:
                winner = s["winner"]
                winner_spec = s["winner_spec"]
            policy["by_condition"][key] = {
                "winner": winner,
                "winner_spec": winner_spec,
                "winner_mean_tag": s["winner"],
                "winner_mean_spec": s["winner_spec"],
                "winner_lcb_tag": s["winner_lcb"],
                "winner_lcb_spec": s["winner_lcb_spec"],
                "metric": s["metric_key"],
                "winner_mean": s["winner_mean"],
                "winner_ci95_low": s["winner_ci95_low"],
                "winner_ci95_high": s["winner_ci95_high"],
                "margin": s["margin"],
                "runner_up": s["runner_up"],
            }
        return policy

    policy_mean.write_text(json.dumps(_build_policy("mean"), indent=2), encoding="utf-8")
    policy_lcb.write_text(json.dumps(_build_policy("lcb"), indent=2), encoding="utf-8")

    print(json_path)
    print(md_path)
    print(policy_mean)
    print(policy_lcb)


if __name__ == "__main__":
    main()
