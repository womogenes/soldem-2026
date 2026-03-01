#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_ANCHORS = [
    "random",
    "pot_fraction",
    "delta_value",
    "conservative",
    "bully",
    "seller_profit",
    "adaptive_profile",
]


def read_lines(path: Path) -> list[str]:
    rows: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        rows.append(s)
    return rows


def parse_ranked_candidates(summary: dict) -> list[str]:
    rows = summary.get("ranked_candidates")
    if not isinstance(rows, list):
        return []
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cand = row.get("candidate")
        if isinstance(cand, str) and cand:
            out.append(cand)
    return out


def dedup(rows: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if row in seen:
            continue
        seen.add(row)
        out.append(row)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build a distributed validation strategy list from evolution summary + anchors"
    )
    ap.add_argument("--summary", required=True, help="Path to evolution aggregate_summary.json")
    ap.add_argument("--out", required=True, help="Output txt path (one strategy spec per line)")
    ap.add_argument("--top-n", type=int, default=16)
    ap.add_argument("--no-default-anchors", action="store_true")
    ap.add_argument(
        "--include-file",
        action="append",
        default=[],
        help="Additional text file with strategy specs (repeatable)",
    )
    ap.add_argument(
        "--include-spec",
        action="append",
        default=[],
        help="Additional strategy spec to include (repeatable)",
    )
    ap.add_argument(
        "--exclude-spec",
        action="append",
        default=[],
        help="Strategy spec to exclude (repeatable)",
    )
    args = ap.parse_args()

    summary_path = Path(args.summary)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    ranked = parse_ranked_candidates(summary)

    specs: list[str] = []
    if not args.no_default_anchors:
        specs.extend(DEFAULT_ANCHORS)

    for path_str in args.include_file:
        specs.extend(read_lines(Path(path_str)))
    specs.extend(s.strip() for s in args.include_spec if s.strip())
    specs.extend(ranked[: max(0, args.top_n)])

    unique_specs = dedup(specs)
    excluded = {s.strip() for s in args.exclude_spec if s.strip()}
    filtered = [s for s in unique_specs if s not in excluded]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(filtered) + ("\n" if filtered else ""), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "out": str(out_path),
                "count": len(filtered),
                "top_n_used": min(len(ranked), max(0, args.top_n)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
