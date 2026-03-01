#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Build day-of policy map from matrix analysis")
    ap.add_argument("analysis_json", help="Path to *.analysis.json from analyze_long_matrix.py")
    ap.add_argument("--out", default="")
    ap.add_argument("--winner-mode", choices=["mean", "lcb"], default="mean")
    args = ap.parse_args()

    data = json.loads(Path(args.analysis_json).read_text())
    rows = data["scenario_summaries"]

    policy = {
        "default": {},
        "by_condition": {},
    }

    # Default recommendation: baseline_v1, horizon 10, corr none.
    for objective in ["ev", "first_place", "robustness"]:
        cand = [
            r
            for r in rows
            if r["rule_profile"] == "baseline_v1"
            and r["objective"] == objective
            and r["horizon"] == 10
            and r["corr_mode"] == "none"
        ]
        if cand:
            if args.winner_mode == "lcb":
                best = max(cand, key=lambda r: r["winner_lcb_value"])
                policy["default"][objective] = best["winner_lcb"]
            else:
                best = max(cand, key=lambda r: r["winner_mean"])
                policy["default"][objective] = best["winner"]

    for r in rows:
        key = f"{r['rule_profile']}|{r['objective']}|h{r['horizon']}|{r['corr_mode']}"
        selected = r["winner_lcb"] if args.winner_mode == "lcb" else r["winner"]
        policy["by_condition"][key] = {
            "winner": selected,
            "winner_mean_tag": r["winner"],
            "winner_lcb_tag": r["winner_lcb"],
            "metric": r["metric_key"],
            "winner_mean": r["winner_mean"],
            "winner_ci95_low": r["winner_ci95_low"],
            "winner_ci95_high": r["winner_ci95_high"],
            "margin": r["margin"],
            "runner_up": r["runner_up"],
            "winner_vs_runner_pairwise_conf": r["winner_vs_runner_pairwise_conf"],
        }

    out = args.out or str(Path(args.analysis_json).with_suffix(".dayof_policy.json"))
    Path(out).write_text(json.dumps(policy, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
