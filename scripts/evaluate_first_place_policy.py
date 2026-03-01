#!/usr/bin/env python
from __future__ import annotations

import argparse
import glob
import json
import os
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.rules import BASELINE_PROFILE, resolve_profile


TARGET_WINNERS = {"equity_evolved_v1", "meta_switch", "pot_fraction"}


@dataclass(frozen=True)
class EvalRow:
    source: str
    overrides: dict
    winner: str


def iter_rows(pattern: str) -> list[EvalRow]:
    rows: list[EvalRow] = []
    for path in glob.glob(pattern):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        # Run-level format from sweep/probe style artifacts.
        if isinstance(data.get("runs"), list):
            for r in data["runs"]:
                if not isinstance(r, dict):
                    continue
                overrides = r.get("overrides")
                if not isinstance(overrides, dict):
                    continue
                winner = ""
                if isinstance(r.get("summary"), dict):
                    winner = str(r["summary"].get("winner", "")).strip()
                else:
                    winner = str(r.get("winner", "")).strip()
                if winner in TARGET_WINNERS:
                    rows.append(
                        EvalRow(
                            source=f"{os.path.basename(path)}::{r.get('label','case')}::{r.get('seed','')}",
                            overrides=overrides,
                            winner=winner,
                        )
                    )
            continue

        # Solver single-result format.
        ow = data.get("objective_winners")
        if not isinstance(ow, dict):
            continue
        fp = ow.get("first_place")
        if not isinstance(fp, dict):
            continue
        winner = str(fp.get("winner", "")).strip()
        overrides = data.get("rule_overrides")
        if (
            winner in TARGET_WINNERS
            and isinstance(overrides, dict)
            and all(k in overrides for k in ("start_chips", "ante_amt", "n_orbits"))
        ):
            rows.append(EvalRow(source=os.path.basename(path), overrides=overrides, winner=winner))
    return rows


def predict_from_rule(
    overrides: dict,
    *,
    ratio_threshold: float,
    absolute_ante: int | None,
) -> str:
    profile = resolve_profile("baseline_v1", **overrides)
    sprint = profile.n_orbits <= 2 and profile.start_chips <= 150
    winner_takes_all = profile.pot_distribution_policy == "winner_takes_all"
    wta_non_sprint = winner_takes_all and profile.n_orbits >= 3
    ante_ratio = (profile.ante_amt / profile.start_chips) if profile.start_chips > 0 else 0.0

    high_ante = wta_non_sprint and ante_ratio >= ratio_threshold
    if absolute_ante is not None:
        high_ante = high_ante or (wta_non_sprint and profile.ante_amt >= absolute_ante)

    if sprint and winner_takes_all:
        return "pot_fraction"
    if profile == BASELINE_PROFILE:
        return "meta_switch"
    if wta_non_sprint:
        if high_ante:
            return "pot_fraction"
        if profile.start_chips >= 180 and ante_ratio < 0.20:
            return "equity_evolved_v1"
        return "meta_switch"
    return "equity_evolved_v1"


def eval_policy(rows: list[EvalRow], *, ratio_threshold: float, absolute_ante: int | None) -> dict:
    hits = 0
    for r in rows:
        pred = predict_from_rule(
            r.overrides,
            ratio_threshold=ratio_threshold,
            absolute_ante=absolute_ante,
        )
        if pred == r.winner:
            hits += 1
    total = len(rows)
    return {
        "ratio_threshold": ratio_threshold,
        "absolute_ante": absolute_ante,
        "hits": hits,
        "total": total,
        "hit_rate": (hits / total) if total else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate first-place routing policies on artifact rows")
    ap.add_argument(
        "--glob",
        default="research_logs/experiment_outputs/*.json",
        help="glob pattern for artifacts",
    )
    ap.add_argument(
        "--ratio-thresholds",
        default="0.33,0.30,0.28,0.27,0.26,0.25",
    )
    ap.add_argument(
        "--absolute-antes",
        default="none,50",
        help="comma-separated list; use 'none' for ratio-only variants",
    )
    ap.add_argument(
        "--out",
        default="research_logs/experiment_outputs/first_place_policy_eval.json",
    )
    args = ap.parse_args()

    rows = iter_rows(args.glob)
    if not rows:
        raise RuntimeError("no evaluation rows found")

    ratios = [float(x.strip()) for x in args.ratio_thresholds.split(",") if x.strip()]
    absolutes: list[int | None] = []
    for tok in args.absolute_antes.split(","):
        t = tok.strip().lower()
        if not t:
            continue
        if t == "none":
            absolutes.append(None)
        else:
            absolutes.append(int(t))

    results = []
    for rt in ratios:
        for aa in absolutes:
            results.append(eval_policy(rows, ratio_threshold=rt, absolute_ante=aa))
    results.sort(key=lambda r: r["hit_rate"], reverse=True)

    out = {
        "glob": args.glob,
        "rows": len(rows),
        "target_winners": sorted(TARGET_WINNERS),
        "results": results,
        "best": results[0] if results else {},
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "rows": len(rows), "best": out.get("best"), "out": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
