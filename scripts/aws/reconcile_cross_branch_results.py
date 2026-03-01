#!/usr/bin/env python
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _top_winners(rows: list[dict], limit: int = 12) -> list[tuple[str, int]]:
    wins = Counter(row["winner_tag"] for row in rows)
    return wins.most_common(limit)


def _objective_summary(rows: list[dict], top_n: int = 8) -> dict[str, list[dict]]:
    by_obj = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = row["metric_key"]
        for ent in row["leaderboard"]:
            by_obj[row["objective"]][ent["tag"]].append(float(ent[key]))

    out: dict[str, list[dict]] = {}
    for obj, tag_vals in by_obj.items():
        rows_obj: list[dict] = []
        for tag, vals in tag_vals.items():
            vals = sorted(vals)
            n = len(vals)
            rows_obj.append(
                {
                    "tag": tag,
                    "n": n,
                    "mean": sum(vals) / n,
                    "q25": vals[max(0, int((n - 1) * 0.25))],
                    "q10": vals[max(0, int((n - 1) * 0.10))],
                }
            )
        rows_obj.sort(key=lambda r: (r["mean"], r["q25"], r["q10"]), reverse=True)
        out[obj] = rows_obj[:top_n]
    return out


def _pairwise_dominance(rows: list[dict], top_n: int = 12) -> list[dict]:
    pair = defaultdict(lambda: [0, 0, 0.0])  # wins, total, margin_sum
    tags = set()
    for row in rows:
        key = row["metric_key"]
        score = {e["tag"]: float(e[key]) for e in row["leaderboard"]}
        tags.update(score)
        for a, b in itertools.permutations(score.keys(), 2):
            if score[a] > score[b]:
                pair[(a, b)][0] += 1
            pair[(a, b)][1] += 1
            pair[(a, b)][2] += score[a] - score[b]

    agg: list[dict] = []
    for tag in sorted(tags):
        rates = []
        margins = []
        for opp in sorted(tags):
            if opp == tag:
                continue
            wins, total, margin = pair[(tag, opp)]
            if total == 0:
                continue
            rates.append(wins / total)
            margins.append(margin / total)
        if not rates:
            continue
        agg.append(
            {
                "tag": tag,
                "avg_pairwise_win_rate": sum(rates) / len(rates),
                "avg_pairwise_margin": sum(margins) / len(margins),
                "worst_opponent_win_rate": min(rates),
            }
        )

    agg.sort(
        key=lambda r: (
            r["avg_pairwise_win_rate"],
            r["avg_pairwise_margin"],
            r["worst_opponent_win_rate"],
        ),
        reverse=True,
    )
    return agg[:top_n]


def main() -> None:
    ap = argparse.ArgumentParser(description="Reconcile distributed cross-branch results")
    ap.add_argument(
        "--broad-summary",
        action="append",
        default=[],
        help="Broad summary JSON path. Repeat flag for multiple files.",
    )
    ap.add_argument(
        "--focus-summary",
        default="",
        help="Focused summary JSON path used for pairwise exploitability.",
    )
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/cross_branch_reconcile_summary.json",
    )
    args = ap.parse_args()

    if not args.broad_summary:
        raise SystemExit("Need at least one --broad-summary")

    broad_rows: list[dict] = []
    for raw in args.broad_summary:
        payload = _load(Path(raw))
        broad_rows.extend(payload.get("rows", []))

    out = {
        "broad_rows": len(broad_rows),
        "broad_top_winners": _top_winners(broad_rows, limit=20),
        "broad_objective_summary": _objective_summary(broad_rows),
    }

    if args.focus_summary:
        focus_payload = _load(Path(args.focus_summary))
        focus_rows = focus_payload.get("rows", [])
        out["focus_rows"] = len(focus_rows)
        out["focus_top_winners"] = _top_winners(focus_rows, limit=20)
        out["focus_objective_summary"] = _objective_summary(focus_rows)
        out["focus_pairwise_dominance"] = _pairwise_dominance(focus_rows)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
