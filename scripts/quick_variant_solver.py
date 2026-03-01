#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


def scenarios() -> list[tuple[str, CorrelationModel]]:
    return [
        ("none", CorrelationModel(mode="none", strength=0.0, pairs=[])),
        ("respect", CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)])),
        ("herd", CorrelationModel(mode="herd", strength=0.30, pairs=[(2, 3)])),
        ("kingmaker", CorrelationModel(mode="kingmaker", strength=0.35, pairs=[(0, 4)])),
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Quick strategy solver for day-of rule variants")
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--rule-overrides-json", default="{}")
    ap.add_argument("--objectives", nargs="+", default=["ev", "first_place", "robustness"])
    ap.add_argument(
        "--strategies",
        nargs="+",
        default=[
            "conservative_plus",
            "equity_evolved_v1",
            "equity_sniper_ultra",
            "pot_fraction",
            "house_hammer",
            "meta_switch",
        ],
    )
    ap.add_argument("--n-matches", type=int, default=80)
    ap.add_argument("--n-games", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    overrides = json.loads(args.rule_overrides_json)
    scenario_rows = []
    aggregate: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    metric_key = {
        "ev": "expected_pnl",
        "first_place": "first_place_rate",
        "robustness": "robustness",
    }

    idx = 0
    for objective in args.objectives:
        for label, corr in scenarios():
            out = run_population_tournament(
                args.strategies,
                n_matches=args.n_matches,
                n_games_per_match=args.n_games,
                rule_profile=args.rule_profile,
                rule_overrides=overrides,
                seed=args.seed + idx,
                objective=objective,
                correlation=corr,
            )
            idx += 1

            board = out["leaderboard"]
            key = metric_key.get(objective, "expected_pnl")
            best = max(board, key=lambda row: row[key])
            scenario_rows.append(
                {
                    "objective": objective,
                    "correlation": label,
                    "winner": best["tag"],
                    "winner_metric": key,
                    "winner_metric_value": best[key],
                    "leaderboard": board,
                }
            )

            for row in board:
                tag = row["tag"]
                aggregate[objective][tag].append(float(row[key]))

    objective_winners: dict[str, dict] = {}
    for objective, by_tag in aggregate.items():
        scored = []
        for tag, vals in by_tag.items():
            scored.append({"tag": tag, "mean_metric_value": sum(vals) / len(vals)})
        scored.sort(key=lambda row: row["mean_metric_value"], reverse=True)
        objective_winners[objective] = {
            "metric": metric_key.get(objective, "expected_pnl"),
            "winner": scored[0]["tag"] if scored else "",
            "ranking": scored,
        }

    result = {
        "rule_profile": args.rule_profile,
        "rule_overrides": overrides,
        "n_matches": args.n_matches,
        "n_games": args.n_games,
        "strategies": args.strategies,
        "objectives": args.objectives,
        "objective_winners": objective_winners,
        "scenarios": scenario_rows,
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
