#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient


def load_map(path: Path) -> list[dict]:
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def aggregate(worker_summaries: list[dict]) -> dict:
    top1_votes = Counter()
    top1_by_objective = defaultdict(Counter)
    top1_by_profile = defaultdict(Counter)
    weighted_rank_score = Counter()
    top_rows: list[dict] = []

    for summary in worker_summaries:
        objective = summary.get("objective", "")
        profile = summary.get("rule_profile", "")
        top_candidates = summary.get("top_candidates") or []
        if not top_candidates:
            continue
        top1 = top_candidates[0]
        top_tag = top1.get("candidate")
        if isinstance(top_tag, str) and top_tag:
            top1_votes[top_tag] += 1
            if objective:
                top1_by_objective[objective][top_tag] += 1
            if profile:
                top1_by_profile[profile][top_tag] += 1

        for rank, row in enumerate(top_candidates[:10], start=1):
            tag = row.get("candidate")
            if not isinstance(tag, str) or not tag:
                continue
            weighted_rank_score[tag] += max(0, 11 - rank)
            top_rows.append(
                {
                    "worker_idx": summary.get("worker_idx"),
                    "objective": objective,
                    "rule_profile": profile,
                    "candidate": tag,
                    "rank": rank,
                    "metric_key": summary.get("metric_key"),
                    "metric_value": row.get("metrics", {}).get(summary.get("metric_key", "")),
                }
            )

    ranked_candidates = sorted(
        weighted_rank_score.items(),
        key=lambda kv: (kv[1], top1_votes.get(kv[0], 0), kv[0]),
        reverse=True,
    )

    return {
        "n_worker_summaries": len(worker_summaries),
        "top1_votes": dict(top1_votes),
        "top1_by_objective": {k: dict(v) for k, v in top1_by_objective.items()},
        "top1_by_profile": {k: dict(v) for k, v in top1_by_profile.items()},
        "weighted_rank_score": dict(weighted_rank_score),
        "ranked_candidates": [
            {"candidate": tag, "rank_score": score, "top1_votes": top1_votes.get(tag, 0)}
            for tag, score in ranked_candidates
        ],
        "top_rows": top_rows,
    }


def write_candidate_pool(summary: dict, path: Path, limit: int) -> None:
    lines = []
    for row in summary.get("ranked_candidates", [])[:limit]:
        lines.append(row["candidate"])
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def sync_pocketbase(summary: dict, base_url: str, token: str, run_id: str) -> None:
    client = PocketBaseClient(base_url, admin_token=token)
    ranked = summary.get("ranked_candidates", [])
    total = max(1, len(summary.get("top_rows", [])))
    for idx, row in enumerate(ranked, start=1):
        client.create(
            "champions",
            {
                "objective": f"evolution_{run_id}",
                "strategy_tag": row["candidate"],
                "score": float(row["rank_score"] / total),
                "metadata_json": {
                    "run_id": run_id,
                    "rank": idx,
                    "rank_score": row["rank_score"],
                    "top1_votes": row["top1_votes"],
                },
            },
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect distributed EC2 evolution results from S3")
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--mapping-file", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--candidate-out", default="")
    ap.add_argument("--candidate-limit", type=int, default=20)
    ap.add_argument("--sync-pocketbase-url", default="")
    ap.add_argument("--sync-pocketbase-token", default="")
    args = ap.parse_args()

    mapping_rows = load_map(Path(args.mapping_file))
    if not mapping_rows:
        raise SystemExit("No mapping rows found")

    run_id = mapping_rows[0]["run_id"]
    out_dir = Path(f"research_logs/experiment_outputs/evolution_{run_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    worker_summaries: list[dict] = []
    missing: list[str] = []
    for row in mapping_rows:
        key = row["summary_key"]
        target = out_dir / f"worker_{row['worker_idx']}_summary.json"
        rc = subprocess.run(
            ["aws", "s3", "cp", f"s3://{args.bucket}/{key}", str(target)],
            capture_output=True,
            text=True,
        )
        if rc.returncode != 0:
            missing.append(key)
            continue
        worker_summaries.append(json.loads(target.read_text(encoding="utf-8")))

    summary = aggregate(worker_summaries)
    summary["run_id"] = run_id
    summary["missing_keys"] = missing
    summary["mapping_file"] = args.mapping_file

    out_path = Path(args.out) if args.out else out_dir / "aggregate_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    candidate_out = (
        Path(args.candidate_out)
        if args.candidate_out
        else Path(f"research_logs/experiment_inputs/evolution_candidate_pool_{run_id}.txt")
    )
    write_candidate_pool(summary, candidate_out, limit=args.candidate_limit)

    print(
        json.dumps(
            {
                "out": str(out_path),
                "candidate_pool": str(candidate_out),
                "missing": len(missing),
            },
            indent=2,
        )
    )

    if args.sync_pocketbase_url and args.sync_pocketbase_token:
        sync_pocketbase(summary, args.sync_pocketbase_url, args.sync_pocketbase_token, run_id)


if __name__ == "__main__":
    main()
