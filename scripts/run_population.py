#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_population_tournament


def parse_pairs(raw: str) -> list[tuple[int, int]]:
    if not raw:
        return []
    pairs = []
    for item in raw.split(","):
        a, b = item.split("-")
        pairs.append((int(a), int(b)))
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description="Run population tournament for strategy discovery")
    ap.add_argument("strategies", nargs="+", help="Strategy tags or Python file paths")
    ap.add_argument("--n-matches", type=int, default=120)
    ap.add_argument("--n-games-per-match", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--objective", default="ev")
    ap.add_argument("--correlation-mode", default="none")
    ap.add_argument("--correlation-strength", type=float, default=0.0)
    ap.add_argument("--correlation-pairs", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if len(args.strategies) < 5:
        raise SystemExit("Need at least 5 strategies for population tournament")

    correlation = CorrelationModel(
        mode=args.correlation_mode,
        strength=args.correlation_strength,
        pairs=parse_pairs(args.correlation_pairs),
    )
    result = run_population_tournament(
        args.strategies,
        n_matches=args.n_matches,
        n_games_per_match=args.n_games_per_match,
        rule_profile=args.rule_profile,
        seed=args.seed,
        objective=args.objective,
        correlation=correlation,
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
