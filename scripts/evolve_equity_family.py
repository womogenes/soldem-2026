#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import CorrelationModel, run_match


def write_candidate(path: Path, tag: str, params: dict) -> None:
    text = f"""from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier={params['bid_multiplier']},
        delta_scale={params['delta_scale']},
        min_delta={params['min_delta']},
        max_stack_frac={params['max_stack_frac']},
        max_pot_frac={params['max_pot_frac']},
        house_multiplier={params['house_multiplier']},
        preserve_weight={params['preserve_weight']},
        sell_count_early={params['sell_count_early']},
        sell_count_late={params['sell_count_late']},
        tag="{tag}",
    )
"""
    path.write_text(text, encoding="utf-8")


def sample_params(rng: random.Random) -> dict:
    return {
        "bid_multiplier": round(rng.uniform(0.62, 1.05), 3),
        "delta_scale": round(rng.uniform(5400.0, 7600.0), 1),
        "min_delta": rng.randint(250, 1100),
        "max_stack_frac": round(rng.uniform(0.14, 0.34), 3),
        "max_pot_frac": round(rng.uniform(0.10, 0.26), 3),
        "house_multiplier": round(rng.uniform(0.95, 1.45), 3),
        "preserve_weight": round(rng.uniform(0.65, 1.35), 3),
        "sell_count_early": rng.choice([1, 2]),
        "sell_count_late": 1,
    }


def eval_hero(
    hero_spec: str,
    opponent_pool: list[str],
    *,
    n_tables: int,
    n_games: int,
    seed: int,
    objective: str,
    correlation: CorrelationModel,
) -> tuple[float, float]:
    rng = random.Random(seed)
    pnls: list[float] = []
    firsts = 0
    total = 0
    for _ in range(n_tables):
        opp = [rng.choice(opponent_pool) for _ in range(4)]
        lineup = [hero_spec, *opp]
        rng.shuffle(lineup)
        seat = lineup.index(hero_spec)
        out = run_match(
            lineup,
            n_games=n_games,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile="baseline_v1",
            objective=objective,
            correlation=correlation,
        )
        for g in out["games"]:
            total += 1
            pnl = float(g["pnl"][seat])
            pnls.append(pnl)
            if int(g["rk"][seat]) == 1:
                firsts += 1
    ev = mean(pnls) if pnls else 0.0
    first = (firsts / total) if total else 0.0
    return ev, first


def main() -> None:
    ap = argparse.ArgumentParser(description="Random-search evolution over EquityAwareStrategy parameters")
    ap.add_argument("--candidates", type=int, default=24)
    ap.add_argument("--n-tables", type=int, default=24)
    ap.add_argument("--n-games", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--objective", default="ev")
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
    ap.add_argument(
        "--out-dir",
        default="research_logs/generated_strategies",
    )
    ap.add_argument(
        "--out-json",
        default="research_logs/experiment_outputs/evolve_equity_results.json",
    )
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    corr = CorrelationModel(mode="respect", strength=0.30, pairs=[(1, 2)])
    rows = []
    for i in range(args.candidates):
        tag = f"equity_auto_{i:03d}"
        params = sample_params(rng)
        path = out_dir / f"{tag}.py"
        write_candidate(path, tag, params)
        ev, first = eval_hero(
            str(path),
            args.opponents,
            n_tables=args.n_tables,
            n_games=args.n_games,
            seed=args.seed + (i * 137),
            objective=args.objective,
            correlation=corr,
        )
        rows.append(
            {
                "tag": tag,
                "path": str(path),
                "params": params,
                "expected_pnl": ev,
                "first_place_rate": first,
                "score": (ev + (first * 30.0)),
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)
    result = {
        "seed": args.seed,
        "objective": args.objective,
        "n_candidates": args.candidates,
        "n_tables": args.n_tables,
        "n_games": args.n_games,
        "top5": rows[:5],
        "all": rows,
    }
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps({"top": rows[:3], "out_json": str(out_json)}, indent=2))


if __name__ == "__main__":
    main()
