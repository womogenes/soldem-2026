#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import request


def auth_token(base_url: str, identity: str, password: str) -> str:
    req = request.Request(
        url=f"{base_url}/api/collections/_superusers/auth-with-password",
        data=json.dumps({"identity": identity, "password": password}).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))["token"]


def api_get(base_url: str, token: str, path: str) -> dict:
    req = request.Request(
        url=f"{base_url}{path}",
        headers={"authorization": f"Bearer {token}"},
        method="GET",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_post(base_url: str, token: str, path: str, payload: dict) -> dict:
    req = request.Request(
        url=f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_patch(base_url: str, token: str, path: str, payload: dict) -> dict:
    req = request.Request(
        url=f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
        },
        method="PATCH",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_fields(schema_rows: list[dict]) -> list[dict]:
    fields = []
    for row in schema_rows:
        field = {
            "name": row["name"],
            "type": row["type"],
            "required": bool(row.get("required", False)),
        }
        fields.append(field)
    return fields


def main() -> None:
    ap = argparse.ArgumentParser(description="Create/update PocketBase collections from schema file")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--identity", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument(
        "--schema-file",
        default="infra/pocketbase_collections.json",
        help="Path to local schema json file",
    )
    args = ap.parse_args()

    schema_path = Path(args.schema_file)
    specs = json.loads(schema_path.read_text(encoding="utf-8"))

    token = auth_token(args.base_url, args.identity, args.password)
    existing = api_get(args.base_url, token, "/api/collections?perPage=200")
    by_name = {item["name"]: item for item in existing.get("items", [])}

    for spec in specs:
        name = spec["name"]
        if name not in by_name:
            created = api_post(
                args.base_url,
                token,
                "/api/collections",
                {"name": name, "type": spec.get("type", "base")},
            )
            by_name[name] = created
            print(f"created collection {name}")

        fields = normalize_fields(spec.get("schema", []))
        patched = api_patch(
            args.base_url,
            token,
            f"/api/collections/{name}",
            {"fields": fields},
        )
        field_names = [f.get("name") for f in patched.get("fields", []) if not f.get("system")]
        print(f"synced {name}: fields={field_names}")


if __name__ == "__main__":
    main()
