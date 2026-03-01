#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _req_json(method: str, url: str, payload: dict | None = None, token: str | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def auth_superuser(base_url: str, email: str, password: str) -> str:
    out = _req_json(
        "POST",
        f"{base_url}/api/collections/_superusers/auth-with-password",
        {"identity": email, "password": password},
    )
    return out["token"]


def ensure_collection(base_url: str, token: str, spec: dict) -> str:
    payload = {
        "name": spec["name"],
        "type": spec.get("type", "base"),
        "fields": spec.get("fields") or spec.get("schema", []),
    }
    try:
        out = _req_json("POST", f"{base_url}/api/collections", payload, token=token)
        return f"created:{out['name']}"
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 400 and (
            "already exists" in body or "validation_collection_name_exists" in body
        ):
            return f"exists:{spec['name']}"
        raise RuntimeError(f"collection {spec['name']} failed ({e.code}): {body}") from e


def list_collections(base_url: str, token: str) -> list[str]:
    out = _req_json("GET", f"{base_url}/api/collections?perPage=200&page=1", token=token)
    return [item["name"] for item in out.get("items", [])]


def main() -> None:
    ap = argparse.ArgumentParser(description="Bootstrap PocketBase collections from infra json")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--admin-email", required=True)
    ap.add_argument("--admin-password", required=True)
    ap.add_argument("--collections", default="infra/pocketbase_collections.json")
    args = ap.parse_args()

    specs = json.loads(Path(args.collections).read_text(encoding="utf-8"))
    token = auth_superuser(args.base_url, args.admin_email, args.admin_password)

    for spec in specs:
        print(ensure_collection(args.base_url, token, spec))

    names = list_collections(args.base_url, token)
    print("collections:", ",".join(sorted(names)))


if __name__ == "__main__":
    main()
