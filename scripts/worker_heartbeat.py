#!/usr/bin/env python
from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient


def main() -> None:
    ap = argparse.ArgumentParser(description="Send worker heartbeat to PocketBase")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-token", default="")
    ap.add_argument("--worker-id", required=True)
    ap.add_argument("--role", default="sim")
    ap.add_argument("--status", default="idle")
    args = ap.parse_args()

    client = PocketBaseClient(args.base_url, admin_token=args.admin_token or None)
    payload = {
        "worker_id": args.worker_id,
        "host": socket.gethostname(),
        "role": args.role,
        "heartbeat_ts": int(time.time()),
        "status": args.status,
    }
    rec = client.create("workers", payload)
    print(rec.get("id", ""))


if __name__ == "__main__":
    main()
