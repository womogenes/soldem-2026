#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.builtin import built_in_strategy_factories


def _request_json(
    method: str,
    url: str,
    payload: dict | None = None,
    token: str | None = None,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code} {method} {url}: {body}") from e


def auth(base_url: str, email: str, password: str) -> str:
    out = _request_json(
        "POST",
        f"{base_url}/api/collections/_superusers/auth-with-password",
        {"identity": email, "password": password},
    )
    return out["token"]


def list_records(base_url: str, token: str, collection: str, filter_expr: str | None = None) -> list[dict]:
    qs = "page=1&perPage=200"
    if filter_expr:
        qs += "&filter=" + urllib.parse.quote(filter_expr, safe="")
    out = _request_json(
        "GET",
        f"{base_url}/api/collections/{collection}/records?{qs}",
        token=token,
    )
    return out.get("items", [])


def create_record(base_url: str, token: str, collection: str, payload: dict[str, Any]) -> dict:
    return _request_json(
        "POST",
        f"{base_url}/api/collections/{collection}/records",
        payload,
        token=token,
    )


def upsert_strategy(base_url: str, token: str, tag: str) -> None:
    existing = list_records(base_url, token, "strategies", filter_expr=f'tag="{tag}"')
    if existing:
        return
    create_record(
        base_url,
        token,
        "strategies",
        {
            "tag": tag,
            "family": "builtin_v3",
            "params_json": {},
            "commit": "working_tree",
            "weaknesses": [],
        },
    )


def ingest_population_file(base_url: str, token: str, path: Path) -> None:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        obj = {"rows": obj}
    def ingest_one(
        leaderboard: list[dict],
        objective: str,
        rule_profile: str,
        horizon: int,
        seed: int,
        extra_meta: dict | None = None,
    ) -> None:
        run = create_record(
            base_url,
            token,
            "eval_runs",
            {
                "rules_profile": rule_profile,
                "objective": objective,
                "horizon": max(1, int(horizon)),
                "seed": max(1, int(seed)),
                "status": "completed",
            },
        )
        run_id = run["id"]

        top = max(leaderboard, key=lambda row: row.get("expected_pnl", -10**9))
        meta = {
            "run_id": run_id,
            "source_file": str(path),
            "rule_profile": rule_profile,
            "horizon": horizon,
        }
        if extra_meta:
            meta.update(extra_meta)
        create_record(
            base_url,
            token,
            "champions",
            {
                "objective": objective,
                "strategy_tag": top["tag"],
                "score": float(top.get("expected_pnl", 0.0)),
                "metadata_json": meta,
            },
        )

        for i, row in enumerate(
            sorted(leaderboard, key=lambda x: x.get("expected_pnl", 0.0), reverse=True),
            start=1,
        ):
            create_record(
                base_url,
                token,
                "match_results",
                {
                    "run_id": run_id,
                    "seat_tags": [row["tag"]],
                    "pnl": [float(row.get("expected_pnl", 0.0))],
                    "rank": [i],
                    "artifact_path": str(path),
                },
            )

    # Standard population output.
    if "leaderboard" in obj:
        objective = obj.get("objective", "ev")
        rule_profile = obj.get("rule_profile", "baseline_v1")
        horizon = max(1, int(obj.get("n_games_per_match", 10)))
        raw_seed = obj.get("seed")
        if raw_seed is None:
            seed = (abs(hash(str(path))) % 1_000_000) + 1
        else:
            seed = int(raw_seed)
            if seed <= 0:
                seed = abs(seed) + 1
        ingest_one(obj["leaderboard"], objective, rule_profile, horizon, seed)
        return

    # Long validation output with many runs.
    if "runs" in obj and isinstance(obj["runs"], list):
        meta = obj.get("meta", {})
        default_profile = meta.get("rule_profile", "baseline_v1")
        default_horizon = int(meta.get("n_games_per_match", 10))
        for run in obj["runs"]:
            leaderboard = run.get("leaderboard")
            if not leaderboard:
                continue
            objective = run.get("objective", "ev")
            rule_profile = run.get("profile", run.get("rule_profile", default_profile))
            horizon = int(run.get("horizon", default_horizon))
            seed = int(run.get("seed", (abs(hash(str(path))) % 1_000_000) + 1))
            extra = {}
            if "correlation" in run:
                extra["correlation"] = run["correlation"]
            ingest_one(leaderboard, objective, rule_profile, horizon, seed, extra_meta=extra)
        return

    # Generic matrix output with rows list.
    if "rows" in obj and isinstance(obj["rows"], list):
        for run in obj["rows"]:
            leaderboard = run.get("leaderboard")
            if not leaderboard:
                continue
            objective = run.get("objective", "ev")
            rule_profile = run.get("profile", run.get("rule_profile", "baseline_v1"))
            horizon = int(run.get("horizon", 10))
            seed = int(run.get("seed", (abs(hash(str(path))) % 1_000_000) + 1))
            extra = {}
            if "correlation" in run:
                extra["correlation"] = run["correlation"]
            ingest_one(leaderboard, objective, rule_profile, horizon, seed, extra_meta=extra)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync strategy metadata and experiment summaries to PocketBase")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-email", required=True)
    ap.add_argument("--admin-password", required=True)
    ap.add_argument(
        "--glob",
        default="research_logs/experiment_outputs/candidates_*.json",
        help="Glob of population tournament result files",
    )
    args = ap.parse_args()

    token = auth(args.base_url, args.admin_email, args.admin_password)

    for tag in sorted(built_in_strategy_factories().keys()):
        upsert_strategy(args.base_url, token, tag)

    files = sorted(Path(".").glob(args.glob))
    for path in files:
        ingest_population_file(args.base_url, token, path)
        print(f"ingested:{path}")


if __name__ == "__main__":
    main()
