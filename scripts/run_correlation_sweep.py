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
    mode: str
    strength: float
    replicate: int
    seed: int


def run_scenario(s: Scenario, strategies: list[str], n_matches: int, horizon: int) -> dict:
    pairs_by_mode = {
        "respect": [(1, 2)],
        "herd": [(3, 4)],
        "kingmaker": [(0, 1), (2, 3)],
    }
    corr = CorrelationModel(mode=s.mode, strength=s.strength, pairs=pairs_by_mode[s.mode])
    out = run_population_tournament(
        strategies,
        n_matches=n_matches,
        n_games_per_match=horizon,
        rule_profile="baseline_v1",
        seed=s.seed,
        objective=s.objective,
        correlation=corr,
    )

    metric_key = (
        "expected_pnl"
        if s.objective == "ev"
        else ("first_place_rate" if s.objective == "first_place" else "robustness")
    )
    champ = max(out["leaderboard"], key=lambda row: row[metric_key])
    return {
        "scenario": {
            "objective": s.objective,
            "mode": s.mode,
            "strength": s.strength,
            "replicate": s.replicate,
            "seed": s.seed,
            "n_matches": n_matches,
            "horizon": horizon,
        },
        "metric_key": metric_key,
        "winner": champ["tag"],
        "winner_metric": champ[metric_key],
        "leaderboard": out["leaderboard"],
    }


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="Correlation strength sweep for research-backed strategy stress tests")
    ap.add_argument("--n-matches", type=int, default=160)
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--horizon", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7000)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out-dir", default="research_logs/experiment_outputs")
    ap.add_argument("--strengths", nargs="*", type=float, default=[0.0, 0.15, 0.30, 0.45, 0.60])
    ap.add_argument("--objectives", nargs="*", default=["ev", "first_place", "robustness"])
    ap.add_argument(
        "--strategies",
        nargs="*",
        default=[
            "conservative",
            "meta_switch_soft",
            "meta_switch",
            "level_k",
            "level_k_l3",
            "level_k|level=2|l0_fraction=0.309|tag=levelk_207605",
            "pot_fraction",
        ],
    )
    args = ap.parse_args()

    modes = ["respect", "herd", "kingmaker"]
    scenarios: list[Scenario] = []
    seed = args.seed
    for objective in args.objectives:
        for mode in modes:
            for strength in args.strengths:
                for rep in range(args.replicates):
                    seed += 1
                    scenarios.append(
                        Scenario(
                            objective=objective,
                            mode=mode,
                            strength=float(strength),
                            replicate=rep,
                            seed=seed,
                        )
                    )

    rows = []
    total = len(scenarios)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        fut_map = {
            ex.submit(run_scenario, s, args.strategies, args.n_matches, args.horizon): s
            for s in scenarios
        }
        done = 0
        for fut in as_completed(fut_map):
            rows.append(fut.result())
            done += 1
            if done % 6 == 0 or done == total:
                print(f"progress {done}/{total}", flush=True)

    grouped = defaultdict(list)
    for r in rows:
        s = r["scenario"]
        grouped[(s["objective"], s["mode"], s["strength"])].append(r)

    summary_rows = []
    winner_counts = Counter()
    for key, vals in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        objective, mode, strength = key
        metric_key = vals[0]["metric_key"]
        perf = defaultdict(list)
        wins = Counter()
        for v in vals:
            wins[v["winner"]] += 1
            winner_counts[v["winner"]] += 1
            for lb in v["leaderboard"]:
                perf[lb["tag"]].append(lb[metric_key])
        means = sorted(((tag, _mean(ms)) for tag, ms in perf.items()), key=lambda kv: kv[1], reverse=True)
        top = means[0]
        runner = means[1] if len(means) > 1 else ("", 0.0)
        summary_rows.append(
            {
                "objective": objective,
                "mode": mode,
                "strength": strength,
                "metric_key": metric_key,
                "winner": top[0],
                "winner_mean": top[1],
                "runner_up": runner[0],
                "margin": top[1] - runner[1],
                "winner_count_replicates": wins[top[0]],
                "wins": dict(wins),
                "top3": [{"tag": t, "mean_metric": m} for t, m in means[:3]],
            }
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"correlation_sweep_{ts}.json"
    md_path = out_dir / f"correlation_sweep_{ts}.md"

    payload = {
        "created_at": datetime.now().isoformat(),
        "config": vars(args),
        "winner_counts": dict(winner_counts),
        "summary": summary_rows,
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Correlation sweep summary",
        "",
        f"Generated at: {datetime.now().isoformat()}",
        "",
        "## Winner counts",
        "",
    ]
    for tag, count in winner_counts.most_common():
        lines.append(f"- {tag}: {count}")

    lines.extend(["", "## Winners by objective/mode/strength", ""])
    for r in summary_rows:
        lines.append(
            f"- {r['objective']} | {r['mode']} | s={r['strength']:.2f} -> "
            f"{r['winner']} ({r['metric_key']}={r['winner_mean']:.4f}, margin={r['margin']:.4f})"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
