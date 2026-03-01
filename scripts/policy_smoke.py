#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from urllib import request


def post_json(url: str, payload: dict) -> dict:
    req = request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str) -> dict:
    req = request.Request(url=url, method="GET")
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def apply_and_check(api: str, *, overrides: dict, expect_first: str, expect_high_ante: bool) -> dict:
    post_json(
        f"{api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": overrides},
    )
    st = get_json(f"{api}/session/state")
    got_first = st.get("resolved_champions", {}).get("first_place")
    got_high = bool(st.get("first_place_policy_cues", {}).get("high_ante_pressure", False))
    if got_first != expect_first:
        raise RuntimeError(
            f"first_place mismatch for overrides={overrides}: expected {expect_first}, got {got_first}"
        )
    if got_high != expect_high_ante:
        raise RuntimeError(
            f"high_ante_pressure mismatch for overrides={overrides}: expected {expect_high_ante}, got {got_high}"
        )
    return {
        "overrides": overrides,
        "resolved_first_place": got_first,
        "high_ante_pressure": got_high,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Smoke-check first-place policy routing against live API")
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    args = ap.parse_args()

    checks = []
    checks.append(
        apply_and_check(
            args.api,
            overrides={},
            expect_first="meta_switch",
            expect_high_ante=False,
        )
    )
    checks.append(
        apply_and_check(
            args.api,
            overrides={
                "start_chips": 200,
                "ante_amt": 50,
                "n_orbits": 4,
                "pot_distribution_policy": "winner_takes_all",
            },
            expect_first="pot_fraction",
            expect_high_ante=True,
        )
    )
    checks.append(
        apply_and_check(
            args.api,
            overrides={
                "start_chips": 140,
                "ante_amt": 35,
                "n_orbits": 4,
                "pot_distribution_policy": "winner_takes_all",
            },
            expect_first="equity_evolved_v1",
            expect_high_ante=False,
        )
    )

    # Restore baseline profile.
    post_json(
        f"{args.api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {}},
    )

    print(json.dumps({"ok": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
