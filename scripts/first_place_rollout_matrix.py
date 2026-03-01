#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament
from strategies import built_in_strategy_factories


def scenarios() -> list[tuple[str, CorrelationModel]]:
    return [
        ("none", CorrelationModel(mode="none", strength=0.0, pairs=[])),
        ("respect", CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)])),
        ("herd", CorrelationModel(mode="herd", strength=0.30, pairs=[(2, 3)])),
        ("kingmaker", CorrelationModel(mode="kingmaker", strength=0.35, pairs=[(0, 4)])),
    ]


def default_cases() -> list[dict[str, Any]]:
    return [
        {"name": "baseline_exact", "overrides": {}},
        {
            "name": "sprint_wta",
            "overrides": {
                "n_orbits": 2,
                "start_chips": 140,
                "ante_amt": 30,
                "pot_distribution_policy": "winner_takes_all",
            },
        },
        {
            "name": "high_ante_ratio_trigger",
            "overrides": {
                "n_orbits": 3,
                "start_chips": 160,
                "ante_amt": 42,
                "pot_distribution_policy": "winner_takes_all",
            },
        },
        {
            "name": "high_ante_absolute_trigger",
            "overrides": {
                "n_orbits": 4,
                "start_chips": 200,
                "ante_amt": 50,
                "pot_distribution_policy": "winner_takes_all",
            },
        },
        {
            "name": "low_ante_wta_nontrigger",
            "overrides": {
                "n_orbits": 4,
                "start_chips": 140,
                "ante_amt": 35,
                "pot_distribution_policy": "winner_takes_all",
            },
        },
        {
            "name": "six_player_baseline",
            "overrides": {"n_players": 6},
        },
    ]


def parse_horizons(raw: str) -> list[int]:
    out = []
    for tok in raw.split(","):
        t = tok.strip()
        if not t:
            continue
        out.append(int(t))
    if not out:
        raise ValueError("at least one horizon is required")
    return out


def parse_cases(path_or_empty: str) -> list[dict[str, Any]]:
    if not path_or_empty:
        return default_cases()
    data = json.loads(Path(path_or_empty).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("cases JSON must be a list")
    cases: list[dict[str, Any]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        overrides = row.get("overrides")
        if not name or not isinstance(overrides, dict):
            continue
        cases.append({"name": name, "overrides": overrides})
    if not cases:
        raise ValueError("no valid cases found in cases JSON")
    return cases


def parse_strategies(raw: str) -> list[str]:
    if not raw.strip():
        return sorted(built_in_strategy_factories().keys())
    return [x.strip() for x in raw.split(",") if x.strip()]


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "stdev": 0.0}
    return {
        "mean": float(sum(values) / len(values)),
        "min": float(min(values)),
        "max": float(max(values)),
        "stdev": float(statistics.pstdev(values)) if len(values) > 1 else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run first-place rollout matrix across rule cases, horizons, and correlation scenarios"
    )
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--cases-json", default="")
    ap.add_argument("--horizons", default="8,10,12")
    ap.add_argument("--strategies", default="")
    ap.add_argument("--n-matches", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/first_place_rollout_matrix.json",
    )
    args = ap.parse_args()

    cases = parse_cases(args.cases_json)
    horizons = parse_horizons(args.horizons)
    strategy_tags = parse_strategies(args.strategies)
    if len(strategy_tags) < 5:
        raise SystemExit("need at least 5 strategies")

    rows: list[dict[str, Any]] = []
    idx = 0
    for case in cases:
        for horizon in horizons:
            by_tag: dict[str, list[float]] = defaultdict(list)
            scenario_rows = []
            for scenario_name, corr in scenarios():
                run_seed = args.seed + idx
                idx += 1
                out = run_population_tournament(
                    strategy_tags,
                    n_matches=args.n_matches,
                    n_games_per_match=horizon,
                    rule_profile=args.rule_profile,
                    rule_overrides=case["overrides"],
                    seed=run_seed,
                    objective="first_place",
                    correlation=corr,
                )
                board = out["leaderboard"]
                winner = max(board, key=lambda row: row["first_place_rate"])
                scenario_rows.append(
                    {
                        "scenario": scenario_name,
                        "seed": run_seed,
                        "winner": winner["tag"],
                        "winner_first_place_rate": winner["first_place_rate"],
                        "leaderboard": board,
                    }
                )
                for row in board:
                    by_tag[row["tag"]].append(float(row["first_place_rate"]))

            aggregate = []
            for tag, vals in by_tag.items():
                stat = summarize(vals)
                aggregate.append(
                    {
                        "tag": tag,
                        "scenarios": len(vals),
                        "mean_first_place_rate": stat["mean"],
                        "min_first_place_rate": stat["min"],
                        "max_first_place_rate": stat["max"],
                        "stdev_first_place_rate": stat["stdev"],
                        "risk_adjusted": stat["mean"] - (0.5 * stat["stdev"]),
                    }
                )
            aggregate.sort(
                key=lambda row: (
                    row["mean_first_place_rate"],
                    row["min_first_place_rate"],
                    row["risk_adjusted"],
                ),
                reverse=True,
            )
            maximin = sorted(
                aggregate,
                key=lambda row: (
                    row["min_first_place_rate"],
                    row["mean_first_place_rate"],
                    row["risk_adjusted"],
                ),
                reverse=True,
            )
            rows.append(
                {
                    "case": case["name"],
                    "rule_overrides": case["overrides"],
                    "horizon": horizon,
                    "n_matches": args.n_matches,
                    "strategies": strategy_tags,
                    "scenario_winners": scenario_rows,
                    "aggregate_ranking": aggregate,
                    "aggregate_best_mean": aggregate[0]["tag"] if aggregate else "",
                    "aggregate_best_maximin": maximin[0]["tag"] if maximin else "",
                }
            )

    case_horizon_winners: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        case_horizon_winners[row["case"]][str(row["horizon"])] = row["aggregate_best_mean"]

    out = {
        "rule_profile": args.rule_profile,
        "objective": "first_place",
        "horizons": horizons,
        "n_matches": args.n_matches,
        "rows": rows,
        "case_horizon_best_mean": case_horizon_winners,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "rows": len(rows),
                "cases": len(cases),
                "horizons": horizons,
                "n_matches": args.n_matches,
                "out": str(out_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
