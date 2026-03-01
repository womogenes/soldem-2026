#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime
from urllib import error, request


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Request failed {url}: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(f"Non-JSON response from {url}: {body}")


def _get_json(url: str) -> dict:
    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Request failed {url}: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(f"Non-JSON response from {url}: {body}")


def _print_block(title: str, payload: dict) -> None:
    print(f"\n== {title} ==")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Apply Sold 'Em rule variation and refresh champions quickly."
    )
    ap.add_argument("--api-url", default="http://127.0.0.1:8000")
    ap.add_argument("--profile-name", default="baseline_v1")
    ap.add_argument("--overrides-json", default="{}")
    ap.add_argument("--skip-recompute", action="store_true")
    ap.add_argument("--n-matches", type=int, default=35)
    ap.add_argument("--n-games-per-match", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260301)
    ap.add_argument("--load-latest-champions", action="store_true")
    ap.add_argument("--summary-path", default="")
    args = ap.parse_args()

    try:
        overrides = json.loads(args.overrides_json)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--overrides-json must be valid JSON object: {exc}")
    if not isinstance(overrides, dict):
        raise SystemExit("--overrides-json must decode to a JSON object")

    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"local_timestamp={ts}")

    apply_resp = _post_json(
        f"{args.api_url}/rules/apply_profile",
        {"profile_name": args.profile_name, "overrides": overrides},
    )
    _print_block("Applied profile", apply_resp)

    if not args.skip_recompute:
        recompute_resp = _post_json(
            f"{args.api_url}/strategies/recompute_champions",
            {
                "n_matches": args.n_matches,
                "n_games_per_match": args.n_games_per_match,
                "seed": args.seed,
            },
        )
        concise = {
            "champions": recompute_resp.get("champions", {}),
            "champion_source": recompute_resp.get("champion_source"),
            "champion_loaded_at": recompute_resp.get("champion_loaded_at"),
            "champion_summary": recompute_resp.get("champion_summary", {}),
        }
        _print_block("Recomputed champions", concise)

    if args.load_latest_champions or args.summary_path:
        summary_path = args.summary_path if args.summary_path else None
        load_resp = _post_json(
            f"{args.api_url}/strategies/load_champions",
            {"summary_path": summary_path},
        )
        concise = {
            "ok": load_resp.get("ok"),
            "champions": load_resp.get("champions", {}),
            "champion_source": load_resp.get("champion_source"),
            "champion_summary": load_resp.get("champion_summary", {}),
        }
        _print_block("Loaded champions from summary", concise)

    state = _get_json(f"{args.api_url}/session/state")
    concise_state = {
        "rule_profile": state.get("rule_profile", {}),
        "champions": state.get("champions", {}),
        "champion_source": state.get("champion_source"),
        "champion_summary": state.get("champion_summary", {}),
    }
    _print_block("Session state", concise_state)


if __name__ == "__main__":
    main()
