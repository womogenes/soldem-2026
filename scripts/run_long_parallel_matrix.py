#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


@dataclass(frozen=True)
class Scenario:
    objective: str
    horizon: int
    corr_mode: str
    corr_strength: float
    pairs: tuple[tuple[int, int], ...]
    rule_profile: str
    replicate: int
    seed: int


def run_scenario(s: Scenario, strategies: list[str], n_matches: int) -> dict:
    corr = CorrelationModel(
        mode=s.corr_mode,
        strength=s.corr_strength,
        pairs=list(s.pairs),
    )
    out = run_population_tournament(
        strategies,
        n_matches=n_matches,
        n_games_per_match=s.horizon,
        rule_profile=s.rule_profile,
        seed=s.seed,
        objective=s.objective,
        correlation=corr,
    )
    metric_key = (
        "expected_pnl"
        if s.objective == "ev"
        else ("first_place_rate" if s.objective == "first_place" else "robustness")
    )
    champion = max(out["leaderboard"], key=lambda row: row[metric_key])
    return {
        "scenario": {
            "objective": s.objective,
            "horizon": s.horizon,
            "corr_mode": s.corr_mode,
            "corr_strength": s.corr_strength,
            "pairs": list(s.pairs),
            "rule_profile": s.rule_profile,
            "replicate": s.replicate,
            "seed": s.seed,
            "n_matches": n_matches,
        },
        "metric_key": metric_key,
        "champion": {
            "tag": champion["tag"],
            "metric_value": champion[metric_key],
            "expected_pnl": champion["expected_pnl"],
            "first_place_rate": champion["first_place_rate"],
            "robustness": champion["robustness"],
            "composites": champion["composites"],
        },
        "leaderboard": out["leaderboard"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Long parallel matrix for Sold 'Em strategy research")
    ap.add_argument("--n-matches", type=int, default=180)
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--seed", type=int, default=2400)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    ap.add_argument("--objectives", nargs="*", default=["ev", "first_place", "robustness"])
    ap.add_argument("--horizons", nargs="*", type=int, default=[5, 10, 20])
    ap.add_argument("--corr-modes", nargs="*", default=["none", "respect", "herd", "kingmaker"])
    ap.add_argument("--strategies", nargs="*", default=[])
    ap.add_argument(
        "--rule-profiles",
        nargs="*",
        default=["baseline_v1", "standard_rankings", "seller_self_bid", "single_card_sell"],
    )
    args = ap.parse_args()

    default_strategies = [
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
        "horizon_push",
        "horizon_push_late",
    ]
    strategies = args.strategies or default_strategies

    corr_catalog = [
        ("none", 0.0, ()),
        ("respect", 0.35, ((1, 2),)),
        ("herd", 0.30, ((3, 4),)),
        ("kingmaker", 0.35, ((0, 1), (2, 3))),
    ]
    corrs = [entry for entry in corr_catalog if entry[0] in set(args.corr_modes)]
    if not corrs:
        raise ValueError(f"No valid correlation modes selected from: {args.corr_modes}")

    scenarios: list[Scenario] = []
    seed = args.seed
    for profile in args.rule_profiles:
        for objective in args.objectives:
            for horizon in args.horizons:
                for corr_mode, corr_strength, pairs in corrs:
                    for rep in range(args.replicates):
                        seed += 1
                        scenarios.append(
                            Scenario(
                                objective=objective,
                                horizon=horizon,
                                corr_mode=corr_mode,
                                corr_strength=corr_strength,
                                pairs=tuple(pairs),
                                rule_profile=profile,
                                replicate=rep,
                                seed=seed,
                            )
                        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"long_parallel_matrix_{ts}.json"
    md_path = out_dir / f"long_parallel_matrix_{ts}.md"

    rows = []
    champ_counts = Counter()
    metric_by_tag: dict[str, list[dict[str, float]]] = defaultdict(list)

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        fut_map = {
            ex.submit(run_scenario, s, strategies, args.n_matches): s
            for s in scenarios
        }
        done = 0
        total = len(fut_map)
        for fut in as_completed(fut_map):
            row = fut.result()
            rows.append(row)
            champ = row["champion"]["tag"]
            champ_counts[champ] += 1
            for lb in row["leaderboard"]:
                metric_by_tag[lb["tag"]].append(
                    {
                        "ev": lb["expected_pnl"],
                        "first": lb["first_place_rate"],
                        "robust": lb["robustness"],
                    }
                )
            done += 1
            if done % 8 == 0 or done == total:
                print(f"progress {done}/{total}", flush=True)

    aggregate = []
    for tag, vals in metric_by_tag.items():
        ev = [v["ev"] for v in vals]
        first = [v["first"] for v in vals]
        robust = [v["robust"] for v in vals]
        aggregate.append(
            {
                "tag": tag,
                "samples": len(vals),
                "avg_ev": statistics.mean(ev),
                "std_ev": statistics.pstdev(ev) if len(ev) > 1 else 0.0,
                "avg_first": statistics.mean(first),
                "std_first": statistics.pstdev(first) if len(first) > 1 else 0.0,
                "avg_robust": statistics.mean(robust),
                "std_robust": statistics.pstdev(robust) if len(robust) > 1 else 0.0,
                "champion_count": champ_counts.get(tag, 0),
            }
        )

    aggregate.sort(key=lambda r: r["avg_ev"], reverse=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at": datetime.now().isoformat(),
                "config": {
                    "n_matches": args.n_matches,
                    "replicates": args.replicates,
                    "workers": args.workers,
                    "rule_profiles": args.rule_profiles,
                    "objectives": args.objectives,
                    "horizons": args.horizons,
                    "corr_modes": args.corr_modes,
                    "strategies": strategies,
                },
                "champion_counts": dict(champ_counts),
                "aggregate": aggregate,
                "rows": rows,
            },
            f,
            indent=2,
        )

    lines = []
    lines.append("# Long parallel matrix summary")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Champion counts")
    lines.append("")
    for tag, count in champ_counts.most_common():
        lines.append(f"- {tag}: {count}")
    lines.append("")
    lines.append("## Aggregate top by avg ev")
    lines.append("")
    for row in aggregate[:15]:
        lines.append(
            f"- {row['tag']}: avg_ev={row['avg_ev']:.2f}±{row['std_ev']:.2f}, "
            f"avg_first={row['avg_first']:.3f}, avg_robust={row['avg_robust']:.2f}, "
            f"champions={row['champion_count']}"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
