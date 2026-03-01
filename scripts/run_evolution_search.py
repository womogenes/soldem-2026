#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


def spec_tag(spec: str) -> str:
    base = spec.split("|")[0]
    for part in spec.split("|")[1:]:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == "tag":
            return v.strip()
    return base


def mutate_spec(spec: str, rng: random.Random) -> str:
    base = spec.split("|")[0]
    params = {}
    for part in spec.split("|")[1:]:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        try:
            params[k] = float(v)
        except ValueError:
            params[k] = v

    if base == "level_k":
        level = int(params.get("level", rng.choice([1, 2, 3])))
        l0 = float(params.get("l0_fraction", 0.28))
        if rng.random() < 0.5:
            level = max(1, min(4, level + rng.choice([-1, 1])))
        l0 = max(0.10, min(0.45, l0 + rng.uniform(-0.05, 0.05)))
        return f"level_k|level={level}|l0_fraction={l0:.3f}|tag=levelk_{rng.randint(1000,999999)}"

    if base == "quantal_response":
        lam = float(params.get("lam", 0.06))
        lam = max(0.01, min(0.20, lam + rng.uniform(-0.02, 0.02)))
        return (
            f"quantal_response|lam={lam:.3f}|seed={rng.randint(1,99999)}|"
            f"tag=qre_{rng.randint(1000,999999)}"
        )

    if base == "ewa_attraction":
        phi = float(params.get("phi", 0.10))
        delta = float(params.get("delta", 0.80))
        lam = float(params.get("lam", 0.08))
        phi = max(0.01, min(0.30, phi + rng.uniform(-0.04, 0.04)))
        delta = max(0.40, min(0.98, delta + rng.uniform(-0.08, 0.08)))
        lam = max(0.01, min(0.20, lam + rng.uniform(-0.03, 0.03)))
        return (
            f"ewa_attraction|phi={phi:.3f}|delta={delta:.3f}|lam={lam:.3f}|"
            f"seed={rng.randint(1,99999)}|tag=ewa_{rng.randint(1000,999999)}"
        )

    if base == "safe_exploit":
        w = float(params.get("exploit_weight", 0.65))
        w = max(0.20, min(0.95, w + rng.uniform(-0.10, 0.10)))
        return f"safe_exploit|exploit_weight={w:.3f}|tag=safe_{rng.randint(1000,999999)}"

    if base == "meta_switch":
        t = float(params.get("aggro_threshold", 0.20))
        t = max(0.08, min(0.45, t + rng.uniform(-0.06, 0.06)))
        return f"meta_switch|aggro_threshold={t:.3f}|tag=meta_{rng.randint(1000,999999)}"

    if base == "winners_curse_aware":
        s = float(params.get("base_shade", 0.62))
        s = max(0.35, min(0.92, s + rng.uniform(-0.08, 0.08)))
        return f"winners_curse_aware|base_shade={s:.3f}|tag=wc_{rng.randint(1000,999999)}"

    if base == "reciprocity_probe":
        return f"reciprocity_probe|tag=recip_{rng.randint(1000,999999)}"

    return spec


def evaluate_population(strategy_specs: list[str], seed: int, n_matches: int) -> dict:
    scenarios = [
        ("ev", 10, CorrelationModel(mode="none", strength=0.0, pairs=[]), 1.0),
        ("ev", 10, CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)]), 1.0),
        ("robustness", 20, CorrelationModel(mode="herd", strength=0.30, pairs=[(3, 4)]), 1.2),
    ]

    scores = {}
    details = {}
    for idx, (objective, horizon, corr, weight) in enumerate(scenarios):
        out = run_population_tournament(
            strategy_specs,
            n_matches=n_matches,
            n_games_per_match=horizon,
            rule_profile="baseline_v1",
            seed=seed + idx,
            objective=objective,
            correlation=corr,
        )
        board = out["leaderboard"]
        rank = {row["tag"]: i for i, row in enumerate(board)}
        for row in board:
            tag = row["tag"]
            # Rank-based score with objective-aligned metric bonus.
            rscore = (len(board) - rank[tag]) / len(board)
            if objective == "ev":
                metric = row["expected_pnl"] / 200.0
            elif objective == "robustness":
                metric = row["robustness"] / 200.0
            else:
                metric = row["first_place_rate"]
            scores[tag] = scores.get(tag, 0.0) + weight * (rscore + metric)
        details[f"{objective}_h{horizon}_{corr.mode}"] = board

    return {"scores": scores, "details": details}


def main() -> None:
    ap = argparse.ArgumentParser(description="Evolutionary search over strategy parameterizations")
    ap.add_argument("--generations", type=int, default=6)
    ap.add_argument("--population", type=int, default=16)
    ap.add_argument("--elite", type=int, default=6)
    ap.add_argument("--n-matches", type=int, default=60)
    ap.add_argument("--seed", type=int, default=8100)
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    args = ap.parse_args()

    rng = random.Random(args.seed)

    anchors = [
        "conservative",
        "pot_fraction",
        "level_k",
        "quantal_response",
        "ewa_attraction",
        "safe_exploit",
        "meta_switch",
        "winners_curse_aware",
        "reciprocity_probe",
        "random",
        "bully",
    ]
    searchable = [
        "level_k|level=2|l0_fraction=0.28|tag=levelk_base",
        "quantal_response|lam=0.06|seed=17|tag=qre_base",
        "ewa_attraction|phi=0.10|delta=0.80|lam=0.08|seed=29|tag=ewa_base",
        "safe_exploit|exploit_weight=0.65|tag=safe_base",
        "meta_switch|aggro_threshold=0.20|tag=meta_base",
        "winners_curse_aware|base_shade=0.62|tag=wc_base",
        "reciprocity_probe|tag=recip_base",
    ]

    population = list(searchable)
    while len(population) < args.population:
        population.append(mutate_spec(rng.choice(searchable), rng))

    history = []
    for gen in range(args.generations):
        print(f"generation {gen+1}/{args.generations}", flush=True)
        candidates = sorted(set(population + anchors))
        eval_out = evaluate_population(candidates, seed=args.seed + gen * 100, n_matches=args.n_matches)
        scores = eval_out["scores"]

        ranked = sorted(population, key=lambda s: scores.get(spec_tag(s), -1e9), reverse=True)
        elite = ranked[: args.elite]

        history.append(
            {
                "generation": gen,
                "elite": [
                    {"spec": s, "tag": spec_tag(s), "score": scores.get(spec_tag(s), 0.0)}
                    for s in elite
                ],
            }
        )

        next_pop = list(elite)
        while len(next_pop) < args.population:
            parent = rng.choice(elite)
            next_pop.append(mutate_spec(parent, rng))
        population = next_pop

    # Final evaluation of elites + anchors with larger sample.
    final_specs = sorted(set(population + anchors))
    print("final evaluation", flush=True)
    final = evaluate_population(final_specs, seed=args.seed + 9999, n_matches=max(args.n_matches, 80))
    final_ranked = sorted(final["scores"].items(), key=lambda kv: kv[1], reverse=True)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"evolution_search_{ts}.json"
    md_path = out_dir / f"evolution_search_{ts}.md"

    payload = {
        "config": vars(args),
        "history": history,
        "final_ranked": final_ranked,
        "final_details": final["details"],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Evolution search summary",
        "",
        f"Generated at: {datetime.now().isoformat()}",
        "",
        "## Final top specs",
        "",
    ]
    for spec, score in final_ranked[:20]:
        lines.append(f"- {spec}: {score:.4f}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
