#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


def build_corr(mode: str) -> CorrelationModel:
    if mode == "none":
        return CorrelationModel(mode="none", strength=0.0, pairs=[])
    return CorrelationModel(mode=mode, strength=0.35, pairs=[(1, 2), (3, 4)])


def parse_csv_ints(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def parse_csv_str(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def summarize(rows: list[dict]) -> dict:
    by_cell: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["objective"], row["horizon"], row["correlation"]["mode"])
        by_cell.setdefault(key, []).append(row)

    summary_rows = []
    for key, samples in sorted(by_cell.items()):
        objective, horizon, corr = key
        # Merge leaderboards by tag across seeds.
        acc: dict[str, dict[str, list[float]]] = {}
        for sample in samples:
            for item in sample["leaderboard"]:
                tag = item["tag"]
                slot = acc.setdefault(
                    tag,
                    {
                        "expected_pnl": [],
                        "first_place_rate": [],
                        "robustness": [],
                    },
                )
                slot["expected_pnl"].append(float(item["expected_pnl"]))
                slot["first_place_rate"].append(float(item["first_place_rate"]))
                slot["robustness"].append(float(item["robustness"]))

        merged = []
        for tag, metrics in acc.items():
            merged.append(
                {
                    "tag": tag,
                    "expected_pnl_mean": mean(metrics["expected_pnl"]),
                    "first_place_rate_mean": mean(metrics["first_place_rate"]),
                    "robustness_mean": mean(metrics["robustness"]),
                    "n_seeds": len(metrics["expected_pnl"]),
                }
            )
        merged.sort(key=lambda r: r["expected_pnl_mean"], reverse=True)
        by_ev = list(merged)
        by_first = sorted(
            merged,
            key=lambda r: r["first_place_rate_mean"],
            reverse=True,
        )
        by_rob = sorted(
            merged,
            key=lambda r: r["robustness_mean"],
            reverse=True,
        )

        if objective == "first_place":
            top_objective = by_first[0] if by_first else None
        elif objective == "robustness":
            top_objective = by_rob[0] if by_rob else None
        else:
            top_objective = by_ev[0] if by_ev else None
        summary_rows.append(
            {
                "objective": objective,
                "horizon": horizon,
                "correlation_mode": corr,
                "top": top_objective,
                "leaderboard_mean_by_ev": by_ev,
                "leaderboard_mean_by_first_place": by_first,
                "leaderboard_mean_by_robustness": by_rob,
            }
        )

    return {"summary_cells": summary_rows}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run long-horizon multi-seed validation matrix")
    ap.add_argument("strategies", nargs="+", help="Strategy tags or Python paths")
    ap.add_argument("--n-matches", type=int, default=600)
    ap.add_argument("--n-games-per-match", default="10", help="CSV horizons, e.g. 5,10,20")
    ap.add_argument("--objectives", default="ev,first_place,robustness")
    ap.add_argument("--correlation-modes", default="none,respect,herd,kingmaker")
    ap.add_argument("--seeds", default="9101,9202,9303")
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--out", default="research_logs/experiment_outputs/long_validation_matrix.json")
    args = ap.parse_args()

    horizons = parse_csv_ints(args.n_games_per_match)
    objectives = parse_csv_str(args.objectives)
    corr_modes = parse_csv_str(args.correlation_modes)
    seeds = parse_csv_ints(args.seeds)

    rows = []
    total = len(horizons) * len(objectives) * len(corr_modes) * len(seeds)
    done = 0

    for objective in objectives:
        for horizon in horizons:
            for corr_mode in corr_modes:
                corr = build_corr(corr_mode)
                for seed in seeds:
                    done += 1
                    print(
                        f"[{done}/{total}] objective={objective} horizon={horizon} corr={corr_mode} seed={seed}",
                        flush=True,
                    )
                    out = run_population_tournament(
                        args.strategies,
                        n_matches=args.n_matches,
                        n_games_per_match=horizon,
                        rule_profile=args.rule_profile,
                        seed=seed,
                        objective=objective,
                        correlation=corr,
                    )
                    rows.append(
                        {
                            "objective": objective,
                            "horizon": horizon,
                            "correlation": {
                                "mode": corr.mode,
                                "strength": corr.strength,
                                "pairs": corr.pairs,
                            },
                            "seed": seed,
                            "leaderboard": out["leaderboard"],
                        }
                    )

    summary = summarize(rows)
    payload = {
        "meta": {
            "n_matches": args.n_matches,
            "horizons": horizons,
            "objectives": objectives,
            "correlation_modes": corr_modes,
            "seeds": seeds,
            "rule_profile": args.rule_profile,
            "strategies": args.strategies,
        },
        "runs": rows,
        "summary": summary,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
