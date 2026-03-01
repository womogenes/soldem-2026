#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


OBJECTIVES = ["ev", "first_place", "robustness"]
HORIZONS = [5, 10, 20]
CORRELATIONS = [
    CorrelationModel(mode="none", strength=0.0, pairs=[]),
    CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)]),
    CorrelationModel(mode="herd", strength=0.30, pairs=[(3, 4)]),
]

STRATEGIES = [
    "random",
    "pot_fraction",
    "delta_value",
    "conservative",
    "bully",
    "seller_profit",
    "adaptive_profile",
    "level_k",
    "quantal_response",
    "ewa_attraction",
    "safe_exploit",
    "meta_switch",
    "winners_curse_aware",
    "reciprocity_probe",
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run research-backed strategy experiment matrix")
    ap.add_argument("--n-matches", type=int, default=40)
    ap.add_argument("--seed", type=int, default=700)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    champion_counts = Counter()
    run_idx = 0

    for objective in OBJECTIVES:
        for horizon in HORIZONS:
            for corr in CORRELATIONS:
                run_seed = args.seed + run_idx
                run_idx += 1
                out = run_population_tournament(
                    STRATEGIES,
                    n_matches=args.n_matches,
                    n_games_per_match=horizon,
                    rule_profile=args.rule_profile,
                    seed=run_seed,
                    objective=objective,
                    correlation=corr,
                )
                board = out["leaderboard"]
                if objective == "ev":
                    key = "expected_pnl"
                elif objective == "first_place":
                    key = "first_place_rate"
                else:
                    key = "robustness"

                champion = max(board, key=lambda row: row[key])
                champion_counts[champion["tag"]] += 1
                rows.append(
                    {
                        "objective": objective,
                        "horizon": horizon,
                        "correlation": {
                            "mode": corr.mode,
                            "strength": corr.strength,
                            "pairs": corr.pairs,
                        },
                        "seed": run_seed,
                        "metric_key": key,
                        "champion": {
                            "tag": champion["tag"],
                            "metric_value": champion[key],
                            "expected_pnl": champion["expected_pnl"],
                            "first_place_rate": champion["first_place_rate"],
                            "robustness": champion["robustness"],
                            "composites": champion["composites"],
                        },
                        "leaderboard": board,
                    }
                )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"research_backed_matrix_{ts}.json"
    md_path = out_dir / f"research_backed_matrix_{ts}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "config": {
                    "n_matches": args.n_matches,
                    "rule_profile": args.rule_profile,
                    "strategies": STRATEGIES,
                },
                "champion_counts": dict(champion_counts),
                "rows": rows,
            },
            f,
            indent=2,
        )

    lines = []
    lines.append("# Research-backed strategy experiment summary")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Champion counts across scenarios")
    lines.append("")
    for tag, count in champion_counts.most_common():
        lines.append(f"- {tag}: {count}")
    lines.append("")
    lines.append("## Scenario champions")
    lines.append("")
    for row in rows:
        c = row["champion"]
        lines.append(
            f"- objective={row['objective']} horizon={row['horizon']} corr={row['correlation']['mode']} -> "
            f"{c['tag']} ({row['metric_key']}={c['metric_value']:.4f}, ev={c['expected_pnl']:.2f}, "
            f"first={c['first_place_rate']:.3f}, robust={c['robustness']:.2f})"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
