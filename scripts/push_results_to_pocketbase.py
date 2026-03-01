#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient


def main() -> None:
    ap = argparse.ArgumentParser(description="Push experiment results to PocketBase")
    ap.add_argument("result_json", help="Path to matrix/sweep/evolution result json")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-token", default="")
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--objective", default="ev")
    args = ap.parse_args()

    p = Path(args.result_json)
    data = json.loads(p.read_text())

    client = PocketBaseClient(args.base_url, admin_token=args.admin_token or None)

    run_payload = {
        "rules_profile": args.rule_profile,
        "objective": args.objective,
        "horizon": int(data.get("config", {}).get("n_matches", 0) or 0),
        "seed": int(data.get("config", {}).get("seed", int(time.time()))),
        "status": "completed",
    }
    run = client.create("eval_runs", run_payload)
    run_id = run.get("id", "")

    # Support both matrix-style and leaderboard-style payloads.
    candidates = []
    if "aggregate" in data and isinstance(data["aggregate"], list):
        for row in data["aggregate"][:10]:
            candidates.append((row.get("tag", ""), row.get("avg_ev", 0.0), row))
    elif "leaderboard" in data and isinstance(data["leaderboard"], list):
        for row in data["leaderboard"][:10]:
            candidates.append((row.get("tag", ""), row.get("expected_pnl", 0.0), row))

    for tag, score, row in candidates:
        if not tag:
            continue
        client.create(
            "champions",
            {
                "objective": args.objective,
                "strategy_tag": tag,
                "score": float(score),
                "metadata_json": row,
            },
        )

    print(json.dumps({"ok": True, "run_id": run_id, "champions_pushed": len(candidates)}))


if __name__ == "__main__":
    main()
