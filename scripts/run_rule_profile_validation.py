#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


def parse_csv(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_csv_int(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate strategy pool across rule profiles")
    ap.add_argument("strategies", nargs="+", help="Strategy tags or Python paths")
    ap.add_argument(
        "--profiles",
        default="baseline_v1,standard_rankings,seller_self_bid,top2_split,high_low_split,single_card_sell",
    )
    ap.add_argument("--objectives", default="ev,first_place,robustness,tournament_win")
    ap.add_argument("--seeds", default="7001,7002,7003")
    ap.add_argument("--n-matches", type=int, default=400)
    ap.add_argument("--n-games-per-match", type=int, default=10)
    ap.add_argument("--correlation-mode", default="none")
    ap.add_argument("--correlation-strength", type=float, default=0.0)
    ap.add_argument("--correlation-pairs", default="")
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/rule_profile_validation_long.json",
    )
    args = ap.parse_args()

    profiles = parse_csv(args.profiles)
    objectives = parse_csv(args.objectives)
    seeds = parse_csv_int(args.seeds)

    pairs = []
    if args.correlation_pairs:
        for item in args.correlation_pairs.split(","):
            a, b = item.split("-")
            pairs.append((int(a), int(b)))

    corr = CorrelationModel(
        mode=args.correlation_mode,
        strength=args.correlation_strength,
        pairs=pairs,
    )

    rows = []
    total = len(profiles) * len(objectives) * len(seeds)
    done = 0

    for profile in profiles:
        for objective in objectives:
            for seed in seeds:
                done += 1
                print(
                    f"[{done}/{total}] profile={profile} objective={objective} seed={seed}",
                    flush=True,
                )
                out = run_population_tournament(
                    args.strategies,
                    n_matches=args.n_matches,
                    n_games_per_match=args.n_games_per_match,
                    rule_profile=profile,
                    seed=seed,
                    objective=objective,
                    correlation=corr,
                )
                rows.append(
                    {
                        "profile": profile,
                        "objective": objective,
                        "seed": seed,
                        "leaderboard": out["leaderboard"],
                    }
                )

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["profile"], row["objective"])].append(row)

    summary = []
    for (profile, objective), samples in sorted(grouped.items()):
        acc = defaultdict(
            lambda: {"ev": [], "match_ev": [], "first": [], "rob": [], "tour": []}
        )
        for sample in samples:
            for item in sample["leaderboard"]:
                tag = item["tag"]
                acc[tag]["ev"].append(float(item["expected_pnl"]))
                acc[tag]["match_ev"].append(float(item.get("expected_match_pnl", 0.0)))
                acc[tag]["first"].append(float(item["first_place_rate"]))
                acc[tag]["rob"].append(float(item["robustness"]))
                acc[tag]["tour"].append(float(item.get("tournament_win_rate", 0.0)))

        merged = []
        for tag, vals in acc.items():
            merged.append(
                {
                    "tag": tag,
                    "expected_pnl_mean": mean(vals["ev"]),
                    "expected_match_pnl_mean": mean(vals["match_ev"]),
                    "first_place_rate_mean": mean(vals["first"]),
                    "robustness_mean": mean(vals["rob"]),
                    "tournament_win_rate_mean": mean(vals["tour"]),
                    "n_seeds": len(vals["ev"]),
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
        by_tournament = sorted(
            merged,
            key=lambda r: r["tournament_win_rate_mean"],
            reverse=True,
        )

        if objective == "first_place":
            top_objective = by_first[0] if by_first else None
        elif objective == "robustness":
            top_objective = by_rob[0] if by_rob else None
        elif objective == "tournament_win":
            top_objective = by_tournament[0] if by_tournament else None
        else:
            top_objective = by_ev[0] if by_ev else None

        summary.append(
            {
                "profile": profile,
                "objective": objective,
                "top": top_objective,
                "leaderboard_mean_by_ev": by_ev,
                "leaderboard_mean_by_first_place": by_first,
                "leaderboard_mean_by_robustness": by_rob,
                "leaderboard_mean_by_tournament_win": by_tournament,
            }
        )

    out_payload = {
        "meta": {
            "profiles": profiles,
            "objectives": objectives,
            "seeds": seeds,
            "n_matches": args.n_matches,
            "n_games_per_match": args.n_games_per_match,
            "correlation": {
                "mode": corr.mode,
                "strength": corr.strength,
                "pairs": corr.pairs,
            },
            "strategies": args.strategies,
        },
        "runs": rows,
        "summary": summary,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_payload, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
