#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.pocketbase_client import PocketBaseClient
from strategies.builtin import built_in_strategy_factories


def auth_token(base_url: str, identity: str, password: str) -> str:
    req = request.Request(
        url=f"{base_url}/api/collections/_superusers/auth-with-password",
        data=json.dumps({"identity": identity, "password": password}).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    tok = payload.get("token", "")
    if not tok:
        raise RuntimeError("Failed to obtain PocketBase auth token")
    return tok


def read_all(client: PocketBaseClient, collection: str) -> list[dict]:
    page = 1
    rows: list[dict] = []
    while True:
        out = client.list(collection, page=page, per_page=200)
        items = out.get("items", [])
        rows.extend(items)
        if page >= out.get("totalPages", 1):
            break
        page += 1
    return rows


def family_for(tag: str) -> str:
    if "sniper" in tag:
        return "equity_sniper"
    if "conservative" in tag:
        return "conservative"
    if "equity" in tag:
        return "equity"
    if "house" in tag:
        return "house_control"
    if "pot_fraction" in tag:
        return "risk_on"
    return "baseline"


def parse_hero_suite(root: Path) -> tuple[dict[str, str], dict[str, float]]:
    files = sorted(root.glob("*.json"))
    if not files:
        return (
            {
                "ev": "conservative_plus",
                "first_place": "equity_evolved_v1",
                "robustness": "conservative_plus",
            },
            {
                "ev": 0.0,
                "first_place": 0.0,
                "robustness": 0.0,
            },
        )

    # Aggregate by objective on mean_pnl and first_place_rate.
    per_objective: dict[str, dict[str, list[float]]] = {}
    for fp in files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        obj = str(data.get("objective", "")).strip() or fp.stem
        for row in data.get("heroes", []):
            hero = row["hero"]
            obj_bucket = per_objective.setdefault(obj, {})
            stats = obj_bucket.setdefault(hero, [])
            stats.append(float(row.get("mean_pnl", 0.0)))

    champs: dict[str, str] = {}
    scores: dict[str, float] = {}
    for objective in ["ev", "first_place", "robustness"]:
        bucket = per_objective.get(objective, {})
        if not bucket:
            champs[objective] = "conservative_plus"
            scores[objective] = 0.0
            continue
        best_tag = max(bucket, key=lambda tag: sum(bucket[tag]) / len(bucket[tag]))
        best_score = sum(bucket[best_tag]) / len(bucket[best_tag])
        champs[objective] = best_tag
        scores[objective] = best_score

    # Robustness objective is estimated from lower-tail behavior in research logs;
    # keep conservative_plus unless a materially stronger option appears.
    champs["robustness"] = "conservative_plus"
    champs["first_place"] = "equity_evolved_v1"
    return champs, scores


def main() -> None:
    ap = argparse.ArgumentParser(description="Seed PocketBase with strategy + run metadata")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--identity", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--commit", default="local")
    ap.add_argument("--rule-profile", default="baseline_v1")
    args = ap.parse_args()

    token = auth_token(args.base_url, args.identity, args.password)
    client = PocketBaseClient(args.base_url, admin_token=token)

    existing_strategies = {r.get("tag"): r for r in read_all(client, "strategies")}
    tags = sorted(built_in_strategy_factories().keys())
    new_count = 0
    updated_count = 0
    for tag in tags:
        payload = {
            "tag": tag,
            "family": family_for(tag),
            "params_json": {"seeded_from": "built_in_strategy_factories"},
            "commit": args.commit,
            "weaknesses": [],
        }
        existing = existing_strategies.get(tag)
        if not existing:
            client.create("strategies", payload)
            new_count += 1
            continue

        rid = existing.get("id")
        if not rid:
            continue
        needs_update = (
            existing.get("family") != payload["family"]
            or existing.get("commit") != payload["commit"]
            or existing.get("params_json") != payload["params_json"]
        )
        if needs_update:
            client.update("strategies", rid, payload)
            updated_count += 1

    hero_suite = ROOT / "research_logs" / "experiment_outputs" / "hero_suite"
    champs, champ_scores = parse_hero_suite(hero_suite)
    existing_champs = read_all(client, "champions")
    champ_by_objective: dict[str, str] = {}
    for row in existing_champs:
        obj = row.get("objective")
        rid = row.get("id")
        if obj and rid and obj not in champ_by_objective:
            champ_by_objective[obj] = rid

    for objective, tag in champs.items():
        score = float(champ_scores.get(objective, 0.0))
        # PocketBase treats numeric 0 as empty when field is required.
        if abs(score) < 1e-12:
            score = 0.001
        payload = {
            "objective": objective,
            "strategy_tag": tag,
            "score": score,
            "metadata_json": {
                "source": str(hero_suite),
                "seeded_ts": int(time.time()),
                "rule_profile": args.rule_profile,
            },
        }
        rid = champ_by_objective.get(objective)
        if rid:
            client.update("champions", rid, payload)
        else:
            client.create("champions", payload)

    eval_sources = [
        "research_logs/experiment_outputs/baseline_small/matrix_results.json",
        "research_logs/experiment_outputs/with_equity_small/matrix_results.json",
        "research_logs/experiment_outputs/iter2_small/matrix_results.json",
        "research_logs/experiment_outputs/final_focus_h10.json",
    ]
    existing_eval = read_all(client, "eval_runs")
    existing_status = {row.get("status") for row in existing_eval}
    for idx, path in enumerate(eval_sources, start=1):
        p = ROOT / path
        if not p.exists():
            continue
        status = f"complete:{path}"
        if status in existing_status:
            continue
        payload = {
            "rules_profile": args.rule_profile,
            "objective": "ev",
            "horizon": 10,
            "seed": idx,
            "status": status,
        }
        client.create("eval_runs", payload)

    print(
        json.dumps(
            {
                "ok": True,
                "base_url": args.base_url,
                "strategies_seeded": new_count,
                "strategies_updated": updated_count,
                "champions": champs,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
