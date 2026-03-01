#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import statistics


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _std(xs: list[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _sem(xs: list[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    return _std(xs) / (len(xs) ** 0.5)


def _ci95(xs: list[float]) -> tuple[float, float]:
    m = _mean(xs)
    e = 1.96 * _sem(xs)
    return (m - e, m + e)


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze long parallel matrix output")
    ap.add_argument("matrix_json", help="Path to long_parallel_matrix_*.json")
    ap.add_argument("--out-md", default="")
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    data = json.loads(Path(args.matrix_json).read_text())
    rows = data["rows"]

    grouped = defaultdict(list)
    for row in rows:
        s = row["scenario"]
        key = (
            s["rule_profile"],
            s["objective"],
            s["horizon"],
            s["corr_mode"],
        )
        grouped[key].append(row)

    scenario_summaries = []
    for key, reps in grouped.items():
        metric_key = reps[0]["metric_key"]
        perf_by_tag = defaultdict(list)
        for rep in reps:
            for lb in rep["leaderboard"]:
                perf_by_tag[lb["tag"]].append(lb[metric_key])

        score_rows = []
        for tag, vals in perf_by_tag.items():
            lo, hi = _ci95(vals)
            score_rows.append(
                {
                    "tag": tag,
                    "mean_metric": _mean(vals),
                    "std_metric": _std(vals),
                    "sem_metric": _sem(vals),
                    "ci95_low": lo,
                    "ci95_high": hi,
                    "n": len(vals),
                }
            )
        score_rows.sort(key=lambda x: x["mean_metric"], reverse=True)
        top = score_rows[0]
        top_lcb = max(score_rows, key=lambda x: x["ci95_low"])
        runner = score_rows[1] if len(score_rows) > 1 else None
        margin = top["mean_metric"] - (runner["mean_metric"] if runner else 0.0)
        pairwise_conf = None
        if runner:
            top_vals = perf_by_tag[top["tag"]]
            runner_vals = perf_by_tag[runner["tag"]]
            if len(top_vals) == len(runner_vals) and top_vals:
                wins = 0.0
                for tv, rv in zip(top_vals, runner_vals):
                    if tv > rv:
                        wins += 1.0
                    elif tv == rv:
                        wins += 0.5
                pairwise_conf = wins / len(top_vals)

        scenario_summaries.append(
            {
                "rule_profile": key[0],
                "objective": key[1],
                "horizon": key[2],
                "corr_mode": key[3],
                "metric_key": metric_key,
                "winner": top["tag"],
                "winner_mean": top["mean_metric"],
                "winner_std": top["std_metric"],
                "winner_sem": top["sem_metric"],
                "winner_ci95_low": top["ci95_low"],
                "winner_ci95_high": top["ci95_high"],
                "winner_lcb": top_lcb["tag"],
                "winner_lcb_value": top_lcb["ci95_low"],
                "runner_up": runner["tag"] if runner else None,
                "margin": margin,
                "winner_vs_runner_pairwise_conf": pairwise_conf,
                "top3": score_rows[:3],
            }
        )

    scenario_summaries.sort(
        key=lambda r: (r["rule_profile"], r["objective"], r["horizon"], r["corr_mode"])
    )

    win_counts = defaultdict(int)
    lcb_counts = defaultdict(int)
    for row in scenario_summaries:
        win_counts[row["winner"]] += 1
        lcb_counts[row["winner_lcb"]] += 1

    summary = {
        "matrix_json": args.matrix_json,
        "winner_counts": dict(sorted(win_counts.items(), key=lambda kv: kv[1], reverse=True)),
        "winner_lcb_counts": dict(sorted(lcb_counts.items(), key=lambda kv: kv[1], reverse=True)),
        "scenario_summaries": scenario_summaries,
    }

    out_json = args.out_json
    if not out_json:
        out_json = str(Path(args.matrix_json).with_suffix(".analysis.json"))
    Path(out_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Long matrix analysis")
    lines.append("")
    lines.append(f"Source: {args.matrix_json}")
    lines.append("")
    lines.append("## Winner counts")
    lines.append("")
    for tag, count in sorted(win_counts.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {tag}: {count}")
    lines.append("")
    lines.append("## Winner counts by lcb")
    lines.append("")
    for tag, count in sorted(lcb_counts.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {tag}: {count}")

    lines.append("")
    lines.append("## Decision table")
    lines.append("")
    for r in scenario_summaries:
        lines.append(
            f"- {r['rule_profile']} | {r['objective']} | h={r['horizon']} | {r['corr_mode']} -> "
            f"mean:{r['winner']} ({r['metric_key']}={r['winner_mean']:.4f}, "
            f"ci95=[{r['winner_ci95_low']:.4f},{r['winner_ci95_high']:.4f}], margin={r['margin']:.4f}), "
            f"lcb:{r['winner_lcb']}"
        )

    out_md = args.out_md
    if not out_md:
        out_md = str(Path(args.matrix_json).with_suffix(".analysis.md"))
    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out_json)
    print(out_md)


if __name__ == "__main__":
    main()
