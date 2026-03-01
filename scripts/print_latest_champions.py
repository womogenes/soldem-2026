#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.champion_loader import find_latest_summary_path, load_champions_from_summary_file


def main() -> None:
    ap = argparse.ArgumentParser(description="Print latest recommended champions from artifacts")
    ap.add_argument(
        "--base-dir",
        default="research_logs/experiment_outputs",
        help="Directory containing summary artifacts",
    )
    ap.add_argument(
        "--summary-path",
        default="",
        help="Optional explicit summary file path",
    )
    ap.add_argument(
        "--default-tag",
        default="seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2",
    )
    args = ap.parse_args()

    if args.summary_path:
        path = Path(args.summary_path)
    else:
        found = find_latest_summary_path(args.base_dir)
        if found is None:
            raise SystemExit(f"No summary files found under {args.base_dir}")
        path = found

    champions, details = load_champions_from_summary_file(path, default_tag=args.default_tag)
    print(
        json.dumps(
            {
                "summary_path": str(path),
                "champions": champions,
                "details": details,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
