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


def _parse_pairs(raw: str) -> list[tuple[int, int]]:
    if not raw:
        return []
    out: list[tuple[int, int]] = []
    for item in raw.split(","):
        a, b = item.split("-")
        out.append((int(a), int(b)))
    return out


def _pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    idx = max(0, min(len(xs) - 1, int(round((len(xs) - 1) * p))))
    return float(xs[idx])


def _hero_eval(
    hero: str,
    opponent_pool: list[str],
    *,
    n_tables: int,
    n_games: int,
    seed: int,
    rule_profile: str,
    objective: str,
    correlation: CorrelationModel,
) -> dict:
    rng = random.Random(seed)
    hero_pnls: list[float] = []
    hero_ranks: list[int] = []
    seat_counts = [0] * 5

    for tix in range(n_tables):
        opponents = [rng.choice(opponent_pool) for _ in range(4)]
        lineup = [hero, *opponents]
        rng.shuffle(lineup)
        hero_seat = lineup.index(hero)
        seat_counts[hero_seat] += 1

        out = run_match(
            lineup,
            n_games=n_games,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile=rule_profile,
            objective=objective,
            correlation=correlation,
        )
        for g in out["games"]:
            hero_pnls.append(float(g["pnl"][hero_seat]))
            hero_ranks.append(int(g["rk"][hero_seat]))

    first_rate = (
        sum(1 for r in hero_ranks if r == 1) / len(hero_ranks) if hero_ranks else 0.0
    )
    return {
        "hero": hero,
        "samples": len(hero_pnls),
        "tables": n_tables,
        "n_games_per_table": n_games,
        "mean_pnl": mean(hero_pnls) if hero_pnls else 0.0,
        "first_place_rate": first_rate,
        "p10_pnl": _pct(hero_pnls, 0.10),
        "p50_pnl": _pct(hero_pnls, 0.50),
        "p90_pnl": _pct(hero_pnls, 0.90),
        "avg_rank": mean(hero_ranks) if hero_ranks else 0.0,
        "seat_counts": seat_counts,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Benchmark hero strategies against opponent mix")
    ap.add_argument("--heroes", nargs="+", required=True, help="Candidate hero strategies")
    ap.add_argument(
        "--opponents",
        nargs="+",
        required=True,
        help="Opponent strategy pool for random draws",
    )
    ap.add_argument("--n-tables", type=int, default=240)
    ap.add_argument("--n-games", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--objective", default="ev")
    ap.add_argument("--correlation-mode", default="none")
    ap.add_argument("--correlation-strength", type=float, default=0.0)
    ap.add_argument("--correlation-pairs", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    correlation = CorrelationModel(
        mode=args.correlation_mode,
        strength=args.correlation_strength,
        pairs=_parse_pairs(args.correlation_pairs),
    )

    rows = []
    for i, hero in enumerate(args.heroes):
        row = _hero_eval(
            hero,
            args.opponents,
            n_tables=args.n_tables,
            n_games=args.n_games,
            seed=args.seed + (i * 9973),
            rule_profile=args.rule_profile,
            objective=args.objective,
            correlation=correlation,
        )
        rows.append(row)

    rows.sort(key=lambda r: (r["mean_pnl"], r["first_place_rate"]), reverse=True)
    out = {
        "objective": args.objective,
        "n_tables": args.n_tables,
        "n_games": args.n_games,
        "rule_profile": args.rule_profile,
        "correlation": {
            "mode": correlation.mode,
            "strength": correlation.strength,
            "pairs": correlation.pairs,
        },
        "heroes": rows,
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    else:
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
