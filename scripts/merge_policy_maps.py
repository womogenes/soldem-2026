#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge policy maps into a single day-of policy file")
    ap.add_argument("policy_json", nargs="+", help="Policy files merged in order; later files override keys")
    ap.add_argument("--default-from", default="", help="Optional policy file to source top-level default from")
    ap.add_argument("--out", required=True, help="Output policy path")
    args = ap.parse_args()

    merged = {"default": {}, "by_condition": {}}
    for path in args.policy_json:
        data = json.loads(Path(path).read_text())
        merged["by_condition"].update(data.get("by_condition", {}))
        if not merged["default"] and data.get("default"):
            merged["default"] = dict(data.get("default", {}))

    if args.default_from:
        base = json.loads(Path(args.default_from).read_text())
        merged["default"] = dict(base.get("default", {}))

    merged["sources"] = args.policy_json
    if args.default_from:
        merged["default_source"] = args.default_from

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
