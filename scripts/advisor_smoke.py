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


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def check_six_player_normalization(api: str) -> dict:
    post_json(
        f"{api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {"n_players": 6, "start_chips": 200}},
    )
    post_json(f"{api}/session/reset", {})

    rec = post_json(
        f"{api}/advisor/recommend",
        {
            "phase": "bid",
            "output_mode": "metrics",
            "objective": "ev",
            "seat": 99,
            "seller_idx": 99,
            "round_num": -7,
            "n_orbits": 0,
            "pot": -20,
            "stacks": [100, -5, 50],
            "my_cards": [[14, "spades"], [10, "hearts"]],
            "auction_cards": [[13, "clubs"]],
        },
    )
    norm = rec.get("normalized_round", {})
    expect(norm.get("seat") == 5, f"seat clamp failed: {norm}")
    expect(norm.get("seller_idx") == 5, f"seller clamp failed: {norm}")
    expect(norm.get("round_num") == 0, f"round clamp failed: {norm}")
    expect(norm.get("n_orbits") == 1, f"orbit clamp failed: {norm}")
    expect(norm.get("pot") == 0, f"pot clamp failed: {norm}")
    expect(norm.get("stacks") == [100, 0, 50, 200, 200, 200], f"stack normalization failed: {norm}")
    expect("strategy_reason_text" in rec, "strategy_reason_text missing in /advisor/recommend response")
    expect(rec.get("rule_profile", {}).get("n_players") == 6, "rule_profile n_players mismatch")

    rec_all = post_json(
        f"{api}/advisor/recommend",
        {
            "phase": "bid",
            "output_mode": "all",
            "objective": "first_place",
            "seat": 4,
            "seller_idx": 3,
            "round_num": 1,
            "n_orbits": 3,
            "pot": 40,
            "stacks": [190, 180, 170, 160, 150, 140],
            "my_cards": [[11, "diamonds"], [7, "hearts"]],
            "auction_cards": [[12, "spades"]],
        },
    )
    expect("normalized_round" in rec_all, "normalized_round missing in output_mode=all response")
    modes = rec_all.get("modes", {})
    expect("metrics" in modes and "top3" in modes and "action_first" in modes, "missing modes in output_mode=all")

    return {
        "mode": "six_player_normalization",
        "normalized_round": norm,
        "strategy_reason": rec.get("strategy_reason"),
    }


def check_five_player_trim(api: str) -> dict:
    post_json(
        f"{api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {}},
    )
    post_json(f"{api}/session/reset", {})

    rec = post_json(
        f"{api}/advisor/recommend",
        {
            "phase": "bid",
            "output_mode": "action_first",
            "objective": "ev",
            "seat": -3,
            "seller_idx": -99,
            "round_num": 2,
            "n_orbits": 3,
            "pot": 100,
            "stacks": [10, 20, 30, 40, 50, 999, 111],
            "my_cards": [[9, "clubs"], [8, "clubs"]],
            "auction_cards": [[14, "hearts"]],
        },
    )
    norm = rec.get("normalized_round", {})
    expect(norm.get("seat") == 0, f"seat min clamp failed: {norm}")
    expect(norm.get("seller_idx") == -1, f"seller min clamp failed: {norm}")
    expect(norm.get("stacks") == [10, 20, 30, 40, 50], f"stack trim failed: {norm}")
    expect(rec.get("rule_profile", {}).get("n_players") == 5, "rule_profile n_players should be baseline 5")
    return {
        "mode": "five_player_trim",
        "normalized_round": norm,
        "primary_action": rec.get("primary_action"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Smoke-check advisor normalization responses against live API")
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    args = ap.parse_args()

    checks = [check_six_player_normalization(args.api), check_five_player_trim(args.api)]

    # Restore baseline profile.
    post_json(
        f"{args.api}/rules/apply_profile",
        {"profile_name": "baseline_v1", "overrides": {}},
    )
    post_json(f"{args.api}/session/reset", {})

    print(json.dumps({"ok": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
