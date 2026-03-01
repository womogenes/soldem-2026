#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Build combined day-of policy from multiple analysis files")
    ap.add_argument("analysis_json", nargs="+", help="One or more *.analysis.json files")
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--winner-mode", choices=["mean", "lcb"], default="mean")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    grouped = defaultdict(list)
    for path in args.analysis_json:
        data = json.loads(Path(path).read_text())
        for row in data["scenario_summaries"]:
            if row["rule_profile"] != args.rule_profile:
                continue
            key = (
                row["rule_profile"],
                row["objective"],
                row["horizon"],
                row["corr_mode"],
                row["metric_key"],
            )
            grouped[key].append(row)

    policy = {"default": {}, "by_condition": {}}

    for key, rows in grouped.items():
        rule, objective, horizon, corr, metric_key = key
        # Combine from top3 rows only to avoid very weak tails.
        agg = defaultdict(list)
        agg_lcb = defaultdict(list)
        for r in rows:
            for t in r["top3"]:
                agg[t["tag"]].append(t["mean_metric"])
                agg_lcb[t["tag"]].append(t.get("ci95_low", t["mean_metric"]))
        mean_score = {tag: sum(vals) / len(vals) for tag, vals in agg.items()}
        lcb_score = {tag: sum(vals) / len(vals) for tag, vals in agg_lcb.items()}
        ranking_mean = sorted(mean_score.items(), key=lambda kv: kv[1], reverse=True)
        ranking_lcb = sorted(lcb_score.items(), key=lambda kv: kv[1], reverse=True)
        ranking = ranking_lcb if args.winner_mode == "lcb" else ranking_mean
        winner = ranking[0][0]
        runner = ranking[1][0] if len(ranking) > 1 else None
        margin = ranking[0][1] - (ranking[1][1] if len(ranking) > 1 else 0.0)

        cond_key = f"{rule}|{objective}|h{horizon}|{corr}"
        policy["by_condition"][cond_key] = {
            "winner": winner,
            "winner_mean_tag": ranking_mean[0][0] if ranking_mean else winner,
            "winner_lcb_tag": ranking_lcb[0][0] if ranking_lcb else winner,
            "metric": metric_key,
            "winner_mean": ranking[0][1],
            "runner_up": runner,
            "margin": margin,
            "sources": args.analysis_json,
        }

    # Defaults from h10 none.
    for objective in ["ev", "first_place", "robustness"]:
        cond_key = f"{args.rule_profile}|{objective}|h10|none"
        if cond_key in policy["by_condition"]:
            policy["default"][objective] = policy["by_condition"][cond_key]["winner"]

    out = args.out or f"research_logs/experiment_outputs/dayof_policy_combined_{args.rule_profile}.json"
    Path(out).write_text(json.dumps(policy, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
