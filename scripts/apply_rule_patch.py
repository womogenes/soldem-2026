#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from urllib import request


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply rule profile/overrides to running advisor API")
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--profile", default="baseline_v1")
    ap.add_argument(
        "--overrides",
        default="{}",
        help='JSON dict, e.g. "{\"seller_can_bid_own_card\": true}"',
    )
    args = ap.parse_args()

    overrides = json.loads(args.overrides)
    payload = json.dumps({"profile_name": args.profile, "overrides": overrides}).encode("utf-8")

    req = request.Request(
        url=f"{args.api}/rules/apply_profile",
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=15) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
