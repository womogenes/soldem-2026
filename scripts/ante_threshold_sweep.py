#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def case_grid() -> list[dict]:
    cases: list[dict] = []

    # Non-sprint, winner-takes-all.
    for ante in [35, 40, 45, 50]:
        cases.append(
            {
                "label": f"wta_ns_140_a{ante}_o4",
                "overrides": {
                    "start_chips": 140,
                    "ante_amt": ante,
                    "n_orbits": 4,
                    "pot_distribution_policy": "winner_takes_all",
                },
            }
        )
    for ante in [40, 50, 60, 70]:
        cases.append(
            {
                "label": f"wta_ns_200_a{ante}_o4",
                "overrides": {
                    "start_chips": 200,
                    "ante_amt": ante,
                    "n_orbits": 4,
                    "pot_distribution_policy": "winner_takes_all",
                },
            }
        )
    for ante in [40, 48, 56]:
        cases.append(
            {
                "label": f"wta_ns_160_a{ante}_o3",
                "overrides": {
                    "start_chips": 160,
                    "ante_amt": ante,
                    "n_orbits": 3,
                    "pot_distribution_policy": "winner_takes_all",
                },
            }
        )

    # Sprint, winner-takes-all.
    for ante in [25, 30, 35, 40, 50]:
        cases.append(
            {
                "label": f"wta_sp_140_a{ante}_o2",
                "overrides": {
                    "start_chips": 140,
                    "ante_amt": ante,
                    "n_orbits": 2,
                    "pot_distribution_policy": "winner_takes_all",
                },
            }
        )

    # Controls: split-pot.
    cases.append(
        {
            "label": "highlow_ns_140_a50_o4",
            "overrides": {
                "start_chips": 140,
                "ante_amt": 50,
                "n_orbits": 4,
                "pot_distribution_policy": "high_low_split",
            },
        }
    )
    cases.append(
        {
            "label": "top2_ns_140_a50_o4",
            "overrides": {
                "start_chips": 140,
                "ante_amt": 50,
                "n_orbits": 4,
                "pot_distribution_policy": "top2_split",
            },
        }
    )
    cases.append(
        {
            "label": "highlow_sp_140_a50_o2",
            "overrides": {
                "start_chips": 140,
                "ante_amt": 50,
                "n_orbits": 2,
                "pot_distribution_policy": "high_low_split",
            },
        }
    )

    return cases


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
            "--objectives",
            "first_place",
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


def first_place_summary(solver_out: dict) -> dict:
    rec = solver_out.get("objective_winners", {}).get("first_place", {})
    ranking = rec.get("ranking", [])
    winner = str(rec.get("winner", "")).strip()
    top = ranking[0] if ranking else {"mean_metric_value": 0.0, "tag": winner}
    second = ranking[1] if len(ranking) > 1 else top
    gap = float(top.get("mean_metric_value", 0.0)) - float(second.get("mean_metric_value", 0.0))
    return {
        "winner": winner,
        "top_tag": str(top.get("tag", "")).strip(),
        "top_metric": float(top.get("mean_metric_value", 0.0)),
        "second_tag": str(second.get("tag", "")).strip(),
        "second_metric": float(second.get("mean_metric_value", 0.0)),
        "gap": gap,
        "ranking_top3": ranking[:3],
    }


def parse_seeds(text: str) -> list[int]:
    out = []
    for tok in text.split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.append(int(tok))
    if not out:
        raise ValueError("at least one seed is required")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="First-place ante threshold sweep")
    ap.add_argument("--n-tables", type=int, default=8)
    ap.add_argument("--n-games", type=int, default=8)
    ap.add_argument("--seeds", default="62001,62002")
    ap.add_argument("--label-substr", default="")
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/ante_threshold_sweep.json",
    )
    args = ap.parse_args()

    seeds = parse_seeds(args.seeds)
    cases = case_grid()
    if args.label_substr:
        needle = args.label_substr.strip().lower()
        cases = [c for c in cases if needle in str(c["label"]).lower()]
        if not cases:
            raise RuntimeError(f"no cases matched label substring: {args.label_substr!r}")

    rows = []
    by_case: dict[str, list[dict]] = defaultdict(list)

    for cix, case in enumerate(cases):
        label = str(case["label"])
        overrides = dict(case["overrides"])
        ratio = float(overrides["ante_amt"]) / float(overrides["start_chips"])
        for six, seed in enumerate(seeds):
            run_seed = seed + (cix * 1000) + six
            solver_out = run_solver(
                overrides=overrides,
                n_tables=args.n_tables,
                n_games=args.n_games,
                seed=run_seed,
            )
            summary = first_place_summary(solver_out)
            row = {
                "label": label,
                "seed": run_seed,
                "ante_ratio": ratio,
                "overrides": overrides,
                "summary": summary,
            }
            rows.append(row)
            by_case[label].append(row)

    aggregated = []
    for label, group in by_case.items():
        wins = Counter(r["summary"]["winner"] for r in group)
        gaps = [float(r["summary"]["gap"]) for r in group]
        ratio = float(group[0]["ante_ratio"])
        overrides = group[0]["overrides"]
        aggregated.append(
            {
                "label": label,
                "ante_ratio": ratio,
                "overrides": overrides,
                "winner_counts": dict(wins),
                "mean_gap": (sum(gaps) / len(gaps)) if gaps else 0.0,
                "seeds": [int(r["seed"]) for r in group],
            }
        )

    aggregated.sort(
        key=lambda r: (
            r["overrides"].get("pot_distribution_policy", ""),
            r["overrides"].get("n_orbits", 0),
            r["ante_ratio"],
        )
    )

    result = {
        "n_tables": args.n_tables,
        "n_games": args.n_games,
        "seeds": seeds,
        "cases": cases,
        "runs": rows,
        "aggregate": aggregated,
    }

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out_path), "n_runs": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
