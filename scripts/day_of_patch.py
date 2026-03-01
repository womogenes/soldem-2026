#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from urllib import request


PRESETS: dict[str, dict] = {
    "baseline": {"profile_name": "baseline_v1", "overrides": {}},
    "top2_split": {"profile_name": "top2_split", "overrides": {}},
    "high_low_split": {"profile_name": "high_low_split", "overrides": {}},
    "single_card_sell": {"profile_name": "single_card_sell", "overrides": {}},
    "seller_self_bid": {"profile_name": "seller_self_bid", "overrides": {}},
    "standard_rankings": {"profile_name": "standard_rankings", "overrides": {}},
    "weird_short_stack": {
        "profile_name": "baseline_v1",
        "overrides": {"start_chips": 120, "ante_amt": 25, "n_orbits": 2},
    },
    "weird_long_game": {
        "profile_name": "baseline_v1",
        "overrides": {"start_chips": 300, "ante_amt": 40, "n_orbits": 5},
    },
    "weird_6p": {
        "profile_name": "baseline_v1",
        "overrides": {"n_players": 6},
    },
}


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


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply day-of rule variant patch to advisor session")
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument(
        "--preset",
        default="baseline",
        choices=sorted(PRESETS.keys()),
        help="Predefined fast patch preset",
    )
    ap.add_argument(
        "--overrides-json",
        default="{}",
        help="Additional JSON overrides merged on top of preset",
    )
    args = ap.parse_args()

    preset = PRESETS[args.preset]
    extra = json.loads(args.overrides_json)
    payload = {
        "profile_name": preset["profile_name"],
        "overrides": {**preset["overrides"], **extra},
    }

    apply_out = post_json(f"{args.api}/rules/apply_profile", payload)
    state = get_json(f"{args.api}/session/state")
    champs = state.get("resolved_champions", {})

    print(
        json.dumps(
            {
                "applied": apply_out,
                "resolved_champions": champs,
                "rule_profile": state.get("rule_profile", {}),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
