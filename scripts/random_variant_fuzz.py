#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sample_overrides(rng: random.Random) -> dict:
    start_chips = rng.choice([120, 140, 180, 200, 260, 320])
    ante_amt = rng.choice([20, 25, 30, 35, 40, 50])
    if ante_amt >= start_chips:
        ante_amt = max(20, int(start_chips * 0.2))
    return {
        "start_chips": start_chips,
        "ante_amt": ante_amt,
        "n_orbits": rng.choice([2, 3, 4, 5]),
        "allow_multi_card_sell": rng.choice([True, False]),
        "seller_can_bid_own_card": rng.choice([True, False]),
        "pot_distribution_policy": rng.choice(
            ["winner_takes_all", "top2_split", "high_low_split"]
        ),
        "hand_ranking_policy": rng.choice(["rarity_50", "standard_plus_five_kind"]),
    }


def run_solver(
    *,
    overrides: dict,
    n_tables: int,
    n_games: int,
    seed: int,
) -> dict:
    solver = ROOT / "scripts" / "quick_variant_hero_solver.py"
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "out.json"
        cmd = [
            sys.executable,
            str(solver),
            "--rule-profile",
            "baseline_v1",
            "--rule-overrides-json",
            json.dumps(overrides, separators=(",", ":")),
            "--n-tables",
            str(n_tables),
            "--n-games",
            str(n_games),
            "--seed",
            str(seed),
            "--out",
            str(out_path),
        ]
        subprocess.run(cmd, check=True)
        return json.loads(out_path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Random weird-variant fuzzing using quick solver")
    ap.add_argument("--n-variants", type=int, default=8)
    ap.add_argument("--n-tables", type=int, default=12)
    ap.add_argument("--n-games", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/random_variant_fuzz.json",
    )
    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows = []
    count_ev: Counter[str] = Counter()
    count_fp: Counter[str] = Counter()
    count_rb: Counter[str] = Counter()

    for i in range(args.n_variants):
        overrides = sample_overrides(rng)
        out = run_solver(
            overrides=overrides,
            n_tables=args.n_tables,
            n_games=args.n_games,
            seed=args.seed + (i * 991),
        )
        ow = out.get("objective_winners", {})
        ev = str(ow.get("ev", {}).get("winner", "")).strip()
        fp = str(ow.get("first_place", {}).get("winner", "")).strip()
        rb = str(ow.get("robustness", {}).get("winner", "")).strip()
        if ev:
            count_ev[ev] += 1
        if fp:
            count_fp[fp] += 1
        if rb:
            count_rb[rb] += 1
        rows.append(
            {
                "variant_index": i,
                "overrides": overrides,
                "winners": {"ev": ev, "first_place": fp, "robustness": rb},
            }
        )

    result = {
        "n_variants": args.n_variants,
        "n_tables": args.n_tables,
        "n_games": args.n_games,
        "seed": args.seed,
        "variants": rows,
        "winner_counts": {
            "ev": dict(count_ev),
            "first_place": dict(count_fp),
            "robustness": dict(count_rb),
        },
    }

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
