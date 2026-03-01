#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import run_population_tournament


RULE_PROFILES = [
    "baseline_v1",
    "standard_rankings",
    "seller_self_bid",
    "top2_split",
    "high_low_split",
    "single_card_sell",
]
OBJECTIVES = ["ev", "first_place", "robustness"]


def main() -> None:
    out_dir = Path("research_logs/variant_precompute")
    out_dir.mkdir(parents=True, exist_ok=True)

    strategies = [
        "market_maker_tight",
        "regime_switch_robust",
        "market_maker",
        "regime_switch",
        "market_maker_aggr",
        "conservative_ultra",
        "conservative",
        "elastic_conservative",
        "pot_fraction",
        "random",
        "bully",
    ]

    rows = []
    seed = 2200
    for profile in RULE_PROFILES:
        for objective in OBJECTIVES:
            seed += 1
            result = run_population_tournament(
                strategies,
                n_matches=60,
                n_games_per_match=10,
                rule_profile=profile,
                objective=objective,
                seed=seed,
            )
            rows.append(
                {
                    "profile": profile,
                    "objective": objective,
                    "leaderboard": result["leaderboard"],
                }
            )

    out = out_dir / "variant_leaderboards.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(out)


if __name__ == "__main__":
    main()
