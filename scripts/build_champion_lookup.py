#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

RISKY_FIRST_PLACE_TAGS = {"pot_fraction", "random", "bully"}


def extract_summary_cells(obj: Any) -> tuple[list[dict], str]:
    if isinstance(obj, dict):
        profile_default = obj.get("meta", {}).get("rule_profile", "baseline_v1")
        summary = obj.get("summary")
        if isinstance(summary, list):
            return summary, profile_default
        if isinstance(summary, dict) and isinstance(summary.get("summary_cells"), list):
            return summary["summary_cells"], profile_default
        if isinstance(obj.get("rows"), list):
            return obj["rows"], profile_default
    if isinstance(obj, list):
        return obj, "baseline_v1"
    raise ValueError("Unsupported input format for champion lookup generation")


def top_tag_from_cell(cell: dict) -> str | None:
    top = cell.get("top")
    if isinstance(top, dict):
        return top.get("tag")
    if isinstance(top, str):
        return top
    if isinstance(cell.get("top_tag"), str):
        return cell["top_tag"]
    return None


def build_raw_lookup(cells: list[dict], default_profile: str) -> dict[str, dict[str, str]]:
    votes: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )

    for cell in cells:
        profile = cell.get("profile") or cell.get("rule_profile") or default_profile
        objective = cell.get("objective")
        tag = top_tag_from_cell(cell)
        if not objective or not tag:
            continue
        votes[profile][objective][tag] += 1

    out: dict[str, dict[str, str]] = {}
    for profile, by_objective in sorted(votes.items()):
        row: dict[str, str] = {}
        for objective, by_tag in sorted(by_objective.items()):
            best_tag = max(by_tag.items(), key=lambda kv: (kv[1], kv[0]))[0]
            row[objective] = best_tag
        out[profile] = row
    return out


def build_safe_lookup(raw: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for profile, mapping in sorted(raw.items()):
        ev = mapping.get("ev", "market_maker_v2")
        first_raw = mapping.get("first_place", ev)
        first = ev if first_raw in RISKY_FIRST_PLACE_TAGS else first_raw
        robust = mapping.get("robustness", "regime_switch_v2")
        tour = mapping.get("tournament_win", ev)
        out[profile] = {
            "ev": ev,
            "first_place": first,
            "robustness": robust,
            "tournament_win": tour,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build raw/safe champion lookup maps from validation JSON"
    )
    ap.add_argument("--src", required=True, help="Validation output JSON path")
    ap.add_argument("--out-raw", required=True, help="Output path for raw lookup map")
    ap.add_argument("--out-safe", required=True, help="Output path for safe lookup map")
    args = ap.parse_args()

    src = Path(args.src)
    obj = json.loads(src.read_text(encoding="utf-8"))
    cells, default_profile = extract_summary_cells(obj)
    raw = build_raw_lookup(cells, default_profile=default_profile)
    safe = build_safe_lookup(raw)

    out_raw = Path(args.out_raw)
    out_safe = Path(args.out_safe)
    out_raw.parent.mkdir(parents=True, exist_ok=True)
    out_safe.parent.mkdir(parents=True, exist_ok=True)
    out_raw.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    out_safe.write_text(json.dumps(safe, indent=2), encoding="utf-8")

    print(f"wrote {out_raw}")
    print(f"wrote {out_safe}")


if __name__ == "__main__":
    main()
