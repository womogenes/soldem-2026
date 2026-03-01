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


def pb_field_from_schema(field: dict) -> dict:
    out = {
        "name": field["name"],
        "type": field["type"],
        "required": bool(field.get("required", False)),
        "presentable": False,
    }
    if field["type"] == "text":
        out["max"] = 0
        out["min"] = 0
        out["pattern"] = ""
        out["autogeneratePattern"] = ""
    elif field["type"] == "number":
        out["max"] = None
        out["min"] = None
        out["noDecimal"] = False
    elif field["type"] == "json":
        out["maxSize"] = 0
    return out


def build_collection_payload(spec: dict) -> dict:
    fields = [pb_field_from_schema(f) for f in spec.get("schema", [])]
    return {
        "name": spec["name"],
        "type": spec.get("type", "base"),
        "fields": fields,
        "listRule": "",
        "viewRule": "",
        "createRule": "",
        "updateRule": "",
        "deleteRule": "",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply PocketBase collection schema")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-token", default="")
    ap.add_argument("--admin-email", default="")
    ap.add_argument("--admin-password", default="")
    ap.add_argument(
        "--collections-json",
        default="infra/pocketbase_collections.json",
    )
    ap.add_argument("--drop-existing", action="store_true")
    args = ap.parse_args()

    client = PocketBaseClient(args.base_url, admin_token=args.admin_token or None)
    if not client.admin_token and args.admin_email and args.admin_password:
        client.auth_superuser(args.admin_email, args.admin_password)
    if not client.admin_token:
        raise SystemExit("Need admin auth token or admin email/password")

    specs = json.loads(Path(args.collections_json).read_text(encoding="utf-8"))
    existing_items = client.list_collections(page=1, per_page=500).get("items", [])
    existing_by_name = {item["name"]: item for item in existing_items}

    created = []
    dropped = []
    skipped = []

    for spec in specs:
        found = existing_by_name.get(spec["name"])
        if found and args.drop_existing:
            client.delete_collection(found["id"])
            dropped.append(spec["name"])
            found = None
        if found:
            skipped.append(spec["name"])
            continue

        payload = build_collection_payload(spec)
        client.create_collection(payload)
        created.append(spec["name"])

    print(
        json.dumps(
            {
                "created": created,
                "dropped": dropped,
                "skipped": skipped,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
