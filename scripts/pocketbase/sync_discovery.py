#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient


def parse_spec(spec: str) -> tuple[str, dict]:
    if ":" not in spec:
        return spec, {}
    family, raw = spec.split(":", 1)
    params: dict[str, object] = {}
    for part in raw.split(","):
        if not part.strip():
            continue
        key, value = part.split("=", 1)
        params[key.strip()] = value.strip()
    return family, params


def fetch_existing_by_tag(client: PocketBaseClient, collection: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    page = 1
    while True:
        row = client.list(collection, page=page, per_page=200)
        items = row.get("items", [])
        for item in items:
            tag = item.get("tag")
            if tag:
                out[tag] = item
        if page >= row.get("totalPages", 1):
            break
        page += 1
    return out


def upsert_strategy_records(
    client: PocketBaseClient,
    candidates: list[str],
    commit: str,
) -> list[dict]:
    existing = fetch_existing_by_tag(client, "strategies")
    touched = []
    for spec in candidates:
        family, params = parse_spec(spec)
        payload = {
            "tag": spec,
            "family": family,
            "params_json": params,
            "commit": commit,
            "weaknesses": [],
        }
        prev = existing.get(spec)
        if prev:
            rec = client.update("strategies", prev["id"], payload)
        else:
            rec = client.create("strategies", payload)
        touched.append(rec)
    return touched


def write_champion_records(
    client: PocketBaseClient,
    large_validation_path: Path,
) -> list[dict]:
    rows = json.loads(large_validation_path.read_text(encoding="utf-8"))
    out = []
    for row in rows:
        winner = row["winner"]
        payload = {
            "objective": row["objective"],
            "strategy_tag": winner["tag"],
            "score": float(winner[row["metric_key"]]),
            "metadata_json": {
                "metric_key": row["metric_key"],
                "expected_pnl": winner.get("expected_pnl"),
                "first_place_rate": winner.get("first_place_rate"),
                "robustness": winner.get("robustness"),
                "samples": winner.get("samples"),
            },
        }
        out.append(client.create("champions", payload))
    return out


def write_eval_run_records(
    client: PocketBaseClient,
    matrix_path: Path,
) -> list[dict]:
    rows = json.loads(matrix_path.read_text(encoding="utf-8"))
    out = []
    for idx, row in enumerate(rows, start=1):
        payload = {
            "rules_profile": row["profile"],
            "objective": row["objective"],
            "horizon": 10,
            "seed": idx,
            "status": "completed",
        }
        out.append(client.create("eval_runs", payload))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync discovered strategy artifacts to PocketBase")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-token", default="")
    ap.add_argument("--admin-email", default="")
    ap.add_argument("--admin-password", default="")
    ap.add_argument("--commit", default="")
    ap.add_argument(
        "--evolution-summary",
        default="research_logs/experiment_outputs/evolution_summary.json",
    )
    ap.add_argument(
        "--large-validation",
        default="research_logs/experiment_outputs/large_validation_baseline_respect.json",
    )
    ap.add_argument(
        "--rule-validation",
        default="research_logs/experiment_outputs/rule_profile_validation.json",
    )
    args = ap.parse_args()

    client = PocketBaseClient(args.base_url, admin_token=args.admin_token or None)
    if not client.admin_token and args.admin_email and args.admin_password:
        client.auth_superuser(args.admin_email, args.admin_password)

    if not client.admin_token:
        raise SystemExit(
            "Need --admin-token or --admin-email/--admin-password for authenticated sync"
        )

    evo = json.loads(Path(args.evolution_summary).read_text(encoding="utf-8"))
    candidates = [row["candidate"] for row in evo.get("top_candidates", [])]

    strategy_records = upsert_strategy_records(client, candidates, commit=args.commit)
    champion_records = write_champion_records(client, Path(args.large_validation))
    eval_records = write_eval_run_records(client, Path(args.rule_validation))

    summary = {
        "strategies_upserted": len(strategy_records),
        "champions_created": len(champion_records),
        "eval_runs_created": len(eval_records),
        "base_url": args.base_url,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
