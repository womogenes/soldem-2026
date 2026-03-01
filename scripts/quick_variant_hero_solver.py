#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_match
from sim.metrics import first_place_rate, robustness_score
from game.rules import resolve_profile


def scenario_models(n_players: int) -> list[tuple[str, CorrelationModel]]:
    def in_bounds(pair: tuple[int, int]) -> bool:
        a, b = pair
        return 0 <= a < n_players and 0 <= b < n_players and a != b

    def pick_or_empty(pref: tuple[int, int]) -> list[tuple[int, int]]:
        if in_bounds(pref):
            return [pref]
        if n_players >= 2:
            return [(0, n_players - 1)]
        return []

    return [
        ("none", CorrelationModel(mode="none", strength=0.0, pairs=[])),
        (
            "respect",
            CorrelationModel(mode="respect", strength=0.35, pairs=pick_or_empty((1, 2))),
        ),
        ("herd", CorrelationModel(mode="herd", strength=0.30, pairs=pick_or_empty((2, 3)))),
        (
            "kingmaker",
            CorrelationModel(mode="kingmaker", strength=0.35, pairs=pick_or_empty((0, n_players - 1))),
        ),
    ]


def hero_eval(
    hero: str,
    opponent_pool: list[str],
    *,
    n_tables: int,
    n_games: int,
    seed: int,
    rule_profile: str,
    rule_overrides: dict,
    objective: str,
    correlation: CorrelationModel,
) -> dict:
    profile = resolve_profile(rule_profile, **rule_overrides)
    n_players = max(2, int(profile.n_players))
    n_opponents = n_players - 1
    rng = random.Random(seed)
    pnls: list[float] = []
    ranks: list[int] = []
    for _ in range(n_tables):
        opponents = [rng.choice(opponent_pool) for _ in range(n_opponents)]
        lineup = [hero, *opponents]
        rng.shuffle(lineup)
        hero_seat = lineup.index(hero)
        out = run_match(
            lineup,
            n_games=n_games,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile=rule_profile,
            rule_overrides=rule_overrides,
            objective=objective,
            correlation=correlation,
        )
        for g in out["games"]:
            pnls.append(float(g["pnl"][hero_seat]))
            ranks.append(int(g["rk"][hero_seat]))

    return {
        "hero": hero,
        "samples": len(pnls),
        "mean_pnl": mean(pnls) if pnls else 0.0,
        "first_place_rate": first_place_rate(ranks),
        "robustness": robustness_score(pnls),
    }


def metric_value(row: dict, objective: str) -> float:
    if objective == "first_place":
        return float(row["first_place_rate"])
    if objective == "robustness":
        return float(row["robustness"])
    return float(row["mean_pnl"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Hero-vs-pool quick solver for day-of variants")
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
            "meta_switch",
            "house_hammer",
        ],
    )
    ap.add_argument(
        "--opponents",
        nargs="+",
        default=[
            "random",
            "bully",
            "seller_profit",
            "adaptive_profile",
            "conservative",
            "conservative_plus",
            "equity_sniper_ultra",
            "equity_sniper",
            "equity_flex",
            "pot_fraction",
            "house_hammer",
        ],
    )
    ap.add_argument("--n-tables", type=int, default=60)
    ap.add_argument("--n-games", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    overrides = json.loads(args.rule_overrides_json)
    all_rows = []
    aggregate: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    idx = 0
    for objective in args.objectives:
        eval_profile = resolve_profile(args.rule_profile, **overrides)
        for label, corr in scenario_models(eval_profile.n_players):
            rows = []
            for hix, hero in enumerate(args.strategies):
                row = hero_eval(
                    hero,
                    args.opponents,
                    n_tables=args.n_tables,
                    n_games=args.n_games,
                    seed=args.seed + idx + (hix * 997),
                    rule_profile=args.rule_profile,
                    rule_overrides=overrides,
                    objective=objective,
                    correlation=corr,
                )
                rows.append(row)
                aggregate[objective][hero].append(metric_value(row, objective))
            idx += 17
            rows.sort(key=lambda r: metric_value(r, objective), reverse=True)
            all_rows.append(
                {
                    "objective": objective,
                    "correlation": label,
                    "rows": rows,
                    "winner": rows[0]["hero"] if rows else "",
                }
            )

    winners = {}
    for objective, by_tag in aggregate.items():
        ranking = []
        for tag, vals in by_tag.items():
            ranking.append({"tag": tag, "mean_metric_value": sum(vals) / len(vals)})
        ranking.sort(key=lambda r: r["mean_metric_value"], reverse=True)
        winners[objective] = {
            "metric": {
                "ev": "mean_pnl",
                "first_place": "first_place_rate",
                "robustness": "robustness",
            }.get(objective, "mean_pnl"),
            "winner": ranking[0]["tag"] if ranking else "",
            "ranking": ranking,
        }

    result = {
        "rule_profile": args.rule_profile,
        "rule_overrides": overrides,
        "n_tables": args.n_tables,
        "n_games": args.n_games,
        "strategies": args.strategies,
        "opponents": args.opponents,
        "objective_winners": winners,
        "scenarios": all_rows,
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
