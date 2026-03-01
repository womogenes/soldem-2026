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


def check_correlated_pair_override(api: str) -> dict:
    post_json(
        f"{api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {}},
    )
    post_json(f"{api}/session/reset", {})
    events = [
        {"event_type": "auction_result", "seller_idx": 0, "winner_idx": 1},
        {"event_type": "auction_result", "seller_idx": 1, "winner_idx": 0},
        {"event_type": "auction_result", "seller_idx": 0, "winner_idx": 1},
        {"event_type": "auction_result", "seller_idx": 1, "winner_idx": 0},
        {"event_type": "auction_result", "seller_idx": 2, "winner_idx": 3},
        {"event_type": "auction_result", "seller_idx": 3, "winner_idx": 4},
        {"event_type": "auction_result", "seller_idx": 0, "winner_idx": 1},
        {"event_type": "auction_result", "seller_idx": 1, "winner_idx": 0},
    ]
    for row in events:
        post_json(f"{api}/session/event", row)
    st = get_json(f"{api}/session/state")
    mode = st.get("table_read", {}).get("mode")
    confidence = float(st.get("table_read", {}).get("confidence", 0.0))
    got_first = st.get("resolved_champions", {}).get("first_place")
    got_reason = st.get("resolved_champion_reasons", {}).get("first_place")
    if mode != "correlated_pair" or confidence < 0.75:
        raise RuntimeError(
            f"correlated_pair read not reached: mode={mode!r} confidence={confidence}"
        )
    if got_first != "equity_evolved_v1":
        raise RuntimeError(
            f"correlated_pair first_place mismatch: expected equity_evolved_v1, got {got_first}"
        )
    if got_reason != "correlated_pair_defensive_first_place":
        raise RuntimeError(
            "correlated_pair reason mismatch: "
            f"expected correlated_pair_defensive_first_place, got {got_reason}"
        )
    return {
        "correlated_pair_mode": mode,
        "correlated_pair_confidence": confidence,
        "resolved_first_place": got_first,
        "resolved_reason": got_reason,
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
                "start_chips": 160,
                "ante_amt": 42,
                "n_orbits": 3,
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
            expect_first="pot_fraction",
            expect_high_ante=True,
        )
    )
    checks.append(
        apply_and_check(
            args.api,
            overrides={
                "n_players": 6,
                "start_chips": 200,
                "ante_amt": 40,
                "n_orbits": 3,
                "pot_distribution_policy": "winner_takes_all",
            },
            expect_first="meta_switch",
            expect_high_ante=False,
        )
    )
    checks.append(
        apply_and_check(
            args.api,
            overrides={
                "start_chips": 200,
                "ante_amt": 35,
                "n_orbits": 4,
                "pot_distribution_policy": "winner_takes_all",
            },
            expect_first="equity_evolved_v1",
            expect_high_ante=False,
        )
    )
    checks.append(check_correlated_pair_override(args.api))

    # Restore baseline profile.
    post_json(
        f"{args.api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {}},
    )
    post_json(f"{args.api}/session/reset", {})

    print(json.dumps({"ok": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
