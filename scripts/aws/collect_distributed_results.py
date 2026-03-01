#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient


def load_map(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def aggregate(worker_payloads: list[dict]) -> dict:
    all_rows = []
    for payload in worker_payloads:
        all_rows.extend(payload.get("rows", []))

    win_counter = Counter(row["winner_tag"] for row in all_rows)
    by_objective = defaultdict(Counter)
    by_profile = defaultdict(Counter)
    for row in all_rows:
        by_objective[row["objective"]][row["winner_tag"]] += 1
        by_profile[row["profile"]][row["winner_tag"]] += 1

    return {
        "n_worker_payloads": len(worker_payloads),
        "n_scenarios": len(all_rows),
        "winner_counts": dict(win_counter),
        "winner_by_objective": {k: dict(v) for k, v in by_objective.items()},
        "winner_by_profile": {k: dict(v) for k, v in by_profile.items()},
        "rows": all_rows,
    }


def write_pocketbase(
    summary: dict,
    pb_url: str,
    pb_token: str,
    run_id: str,
):
    client = PocketBaseClient(pb_url, admin_token=pb_token)
    winners = summary["winner_counts"]
    total = max(1, sum(winners.values()))
    for tag, cnt in sorted(winners.items(), key=lambda kv: kv[1], reverse=True):
        score = float(cnt / total)
        client.create(
            "champions",
            {
                "objective": f"distributed_{run_id}",
                "strategy_tag": tag,
                "score": score,
                "metadata_json": {
                    "run_id": run_id,
                    "win_count": cnt,
                    "total_scenarios": total,
                },
            },
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect distributed EC2 result files from S3")
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--mapping-file", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--sync-pocketbase-url", default="")
    ap.add_argument("--sync-pocketbase-token", default="")
    args = ap.parse_args()

    mapping_path = Path(args.mapping_file)
    rows = load_map(mapping_path)
    if not rows:
        raise SystemExit("No rows in mapping file")

    run_id = rows[0]["run_id"]
    local_dir = Path(f"research_logs/experiment_outputs/distributed_{run_id}")
    local_dir.mkdir(parents=True, exist_ok=True)

    payloads: list[dict] = []
    missing: list[str] = []

    for row in rows:
        key = row["result_key"]
        target = local_dir / f"worker_{row['worker_idx']}.json"
        rc = __import__("subprocess").run(
            [
                "aws",
                "s3",
                "cp",
                f"s3://{args.bucket}/{key}",
                str(target),
            ],
            capture_output=True,
            text=True,
        )
        if rc.returncode != 0:
            missing.append(key)
            continue
        payloads.append(json.loads(target.read_text(encoding="utf-8")))

    summary = aggregate(payloads)
    summary["run_id"] = run_id
    summary["missing_keys"] = missing

    out_path = Path(args.out) if args.out else local_dir / "aggregate_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "missing": len(missing)}, indent=2))

    if args.sync_pocketbase_url and args.sync_pocketbase_token:
        write_pocketbase(
            summary,
            pb_url=args.sync_pocketbase_url,
            pb_token=args.sync_pocketbase_token,
            run_id=run_id,
        )


if __name__ == "__main__":
    main()
