#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


STRATEGIES = [
    "random",
    "pot_fraction",
    "delta_value",
    "conservative",
    "bully",
    "seller_profit",
    "adaptive_profile",
    "level_k",
    "level_k_l1",
    "level_k_l3",
    "quantal_response",
    "quantal_cold",
    "quantal_hot",
    "ewa_attraction",
    "ewa_slow",
    "ewa_fast",
    "safe_exploit",
    "safe_exploit_robust",
    "safe_exploit_aggro",
    "meta_switch",
    "meta_switch_soft",
    "winners_curse_aware",
    "reciprocity_probe",
]

SCENARIOS = [
    {
        "name": "ev_h10_none",
        "objective": "ev",
        "horizon": 10,
        "correlation": CorrelationModel(mode="none", strength=0.0, pairs=[]),
    },
    {
        "name": "ev_h10_respect",
        "objective": "ev",
        "horizon": 10,
        "correlation": CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)]),
    },
    {
        "name": "robust_h20_herd",
        "objective": "robustness",
        "horizon": 20,
        "correlation": CorrelationModel(mode="herd", strength=0.30, pairs=[(3, 4)]),
    },
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Research strategy variant sweep")
    ap.add_argument("--n-matches", type=int, default=90)
    ap.add_argument("--seed", type=int, default=1500)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    agg = defaultdict(list)
    for i, scenario in enumerate(SCENARIOS):
        out = run_population_tournament(
            STRATEGIES,
            n_matches=args.n_matches,
            n_games_per_match=scenario["horizon"],
            rule_profile=args.rule_profile,
            seed=args.seed + i,
            objective=scenario["objective"],
            correlation=scenario["correlation"],
        )
        board = out["leaderboard"]
        rows.append({"scenario": scenario["name"], "leaderboard": board})
        for r in board:
            agg[r["tag"]].append(
                {
                    "expected_pnl": r["expected_pnl"],
                    "first_place_rate": r["first_place_rate"],
                    "robustness": r["robustness"],
                }
            )

    aggregate = []
    for tag, vals in agg.items():
        n = len(vals)
        aggregate.append(
            {
                "tag": tag,
                "avg_expected_pnl": sum(v["expected_pnl"] for v in vals) / n,
                "avg_first_place_rate": sum(v["first_place_rate"] for v in vals) / n,
                "avg_robustness": sum(v["robustness"] for v in vals) / n,
                "n_scenarios": n,
            }
        )
    aggregate.sort(key=lambda r: r["avg_expected_pnl"], reverse=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"research_variant_sweep_{ts}.json"
    md_path = out_dir / f"research_variant_sweep_{ts}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"scenarios": rows, "aggregate": aggregate}, f, indent=2)

    lines = [
        "# Research strategy variant sweep",
        "",
        f"Generated at: {datetime.now().isoformat()}",
        "",
        "## Aggregate top by average expected pnl",
        "",
    ]
    for row in aggregate[:10]:
        lines.append(
            f"- {row['tag']}: ev={row['avg_expected_pnl']:.2f}, first={row['avg_first_place_rate']:.3f}, robust={row['avg_robustness']:.2f}"
        )

    lines += ["", "## Scenario winners", ""]
    for scenario in rows:
        top = scenario["leaderboard"][0]
        lines.append(
            f"- {scenario['scenario']}: {top['tag']} (ev={top['expected_pnl']:.2f}, first={top['first_place_rate']:.3f}, robust={top['robustness']:.2f})"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
