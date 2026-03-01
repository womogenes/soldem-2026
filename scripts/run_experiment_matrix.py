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


OBJECTIVES = ["ev", "first_place", "robustness"]
HORIZONS = [5, 10, 20]
LLM_MODES = ["offline_only", "fallback_live", "primary_live"]
CORR_MODES = [
    CorrelationModel(mode="none", strength=0.0, pairs=[]),
    CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)]),
    CorrelationModel(mode="herd", strength=0.30, pairs=[(3, 4)]),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run multi-objective horizon experiment matrix")
    ap.add_argument("strategies", nargs="+", help="Strategy tags or Python file paths")
    ap.add_argument("--n-matches", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = 0

    matrix_rows = []
    for objective in OBJECTIVES:
        for horizon in HORIZONS:
            for llm_mode in LLM_MODES:
                for corr in CORR_MODES:
                    run_seed = args.seed + idx
                    idx += 1
                    result = run_population_tournament(
                        args.strategies,
                        n_matches=args.n_matches,
                        n_games_per_match=horizon,
                        rule_profile=args.rule_profile,
                        seed=run_seed,
                        objective=objective,
                        correlation=corr,
                    )
                    row = {
                        "objective": objective,
                        "horizon": horizon,
                        "llm_mode": llm_mode,
                        "correlation": {
                            "mode": corr.mode,
                            "strength": corr.strength,
                            "pairs": corr.pairs,
                        },
                        "seed": run_seed,
                        "leaderboard": result["leaderboard"],
                    }
                    matrix_rows.append(row)

    matrix_path = out_dir / "matrix_results.json"
    with open(matrix_path, "w", encoding="utf-8") as f:
        json.dump(matrix_rows, f, indent=2)

    print(f"wrote {len(matrix_rows)} experiment rows to {matrix_path}")


if __name__ == "__main__":
    main()
