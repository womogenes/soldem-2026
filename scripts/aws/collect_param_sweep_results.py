#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import subprocess
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


def aggregate(payloads: list[dict]) -> dict:
    champion = payloads[0]["champion"] if payloads else ""
    per_candidate_rows: dict[str, list[dict]] = defaultdict(list)
    for payload in payloads:
        for row in payload.get("rows", []):
            candidate = row["candidate"]
            per_candidate_rows[candidate].extend(row.get("scenario_rows", []))

    summary_rows = []
    for candidate, rows in sorted(per_candidate_rows.items()):
        if not rows:
            continue
        deltas = [r["delta_vs_champion"] for r in rows]
        wins = sum(1 for d in deltas if d > 0)
        ties = sum(1 for d in deltas if abs(d) < 1e-12)
        losses = len(deltas) - wins - ties
        mean_delta = sum(deltas) / len(deltas)

        by_obj: dict[str, dict] = {}
        for obj in ["ev", "first_place", "robustness"]:
            vals = [r for r in rows if r["objective"] == obj]
            if not vals:
                continue
            d = [r["delta_vs_champion"] for r in vals]
            by_obj[obj] = {
                "n": len(vals),
                "mean_delta": sum(d) / len(d),
                "wins": sum(1 for x in d if x > 0),
                "ties": sum(1 for x in d if abs(x) < 1e-12),
            }

        summary_rows.append(
            {
                "candidate": candidate,
                "n_scenarios": len(rows),
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "mean_delta_vs_champion": mean_delta,
                "by_objective": by_obj,
            }
        )

    summary_rows.sort(
        key=lambda r: (r["mean_delta_vs_champion"], r["wins"], -r["losses"]),
        reverse=True,
    )
    return {
        "champion": champion,
        "n_candidates": len(summary_rows),
        "candidate_summary": summary_rows,
    }


def sync_pocketbase(summary: dict, base_url: str, token: str, run_id: str) -> None:
    client = PocketBaseClient(base_url, admin_token=token)
    for idx, row in enumerate(summary["candidate_summary"], start=1):
        client.create(
            "champions",
            {
                "objective": f"param_sweep_{run_id}",
                "strategy_tag": row["candidate"],
                "score": float(row["mean_delta_vs_champion"]),
                "metadata_json": {
                    "rank": idx,
                    "wins": row["wins"],
                    "ties": row["ties"],
                    "losses": row["losses"],
                    "n_scenarios": row["n_scenarios"],
                },
            },
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect EC2 param-sweep result files from S3")
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--mapping-file", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--sync-pocketbase-url", default="")
    ap.add_argument("--sync-pocketbase-token", default="")
    args = ap.parse_args()

    mapping_path = Path(args.mapping_file)
    mapping_rows = load_map(mapping_path)
    if not mapping_rows:
        raise SystemExit("No mapping rows found")

    run_id = mapping_rows[0]["run_id"]
    local_dir = Path(f"research_logs/experiment_outputs/param_sweep_{run_id}")
    local_dir.mkdir(parents=True, exist_ok=True)

    payloads: list[dict] = []
    missing: list[str] = []
    for row in mapping_rows:
        key = row["result_key"]
        target = local_dir / f"worker_{row['worker_idx']}.json"
        rc = subprocess.run(
            ["aws", "s3", "cp", f"s3://{args.bucket}/{key}", str(target)],
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
    summary["mapping_file"] = args.mapping_file

    out_path = Path(args.out) if args.out else local_dir / "aggregate_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "missing": len(missing)}, indent=2))

    if args.sync_pocketbase_url and args.sync_pocketbase_token:
        sync_pocketbase(summary, args.sync_pocketbase_url, args.sync_pocketbase_token, run_id)


if __name__ == "__main__":
    main()
