#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib import request


ROOT = Path(__file__).resolve().parents[1]


def post_json(url: str, payload: dict) -> dict:
    req = request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str) -> dict:
    req = request.Request(url=url, method="GET")
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_solver(
    rule_profile: str,
    overrides: dict,
    *,
    n_tables: int,
    n_games: int,
    seed: int,
) -> dict:
    solver = ROOT / "scripts" / "quick_variant_hero_solver.py"
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "solver_out.json"
        cmd = [
            sys.executable,
            str(solver),
            "--rule-profile",
            rule_profile,
            "--rule-overrides-json",
            json.dumps(overrides, separators=(",", ":")),
            "--n-tables",
            str(n_tables),
            "--n-games",
            str(n_games),
            "--seed",
            str(seed),
            "--out",
            str(out_path),
        ]
        subprocess.run(cmd, check=True)
        return json.loads(out_path.read_text(encoding="utf-8"))


def objective_winners(solver_out: dict) -> dict[str, str]:
    ow = solver_out.get("objective_winners", {})
    ev = str(ow.get("ev", {}).get("winner", "")).strip()
    fp = str(ow.get("first_place", {}).get("winner", "")).strip()
    rb = str(ow.get("robustness", {}).get("winner", "")).strip()
    if not ev or not fp or not rb:
        raise RuntimeError("Solver output missing objective winner(s)")
    return {"ev": ev, "first_place": fp, "robustness": rb}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run quick variant solver and patch API champions in one command"
    )
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--rule-profile", default="baseline_v1")
    ap.add_argument("--overrides-json", default="{}")
    ap.add_argument("--n-tables", type=int, default=12)
    ap.add_argument("--n-games", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--keep-dynamic", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    overrides = json.loads(args.overrides_json)
    solver_out = run_solver(
        args.rule_profile,
        overrides,
        n_tables=args.n_tables,
        n_games=args.n_games,
        seed=args.seed,
    )
    winners = objective_winners(solver_out)

    payload = {
        "profile_name": args.rule_profile,
        "overrides": overrides,
    }
    set_payload = {
        "ev": winners["ev"],
        "first_place": winners["first_place"],
        "robustness": winners["robustness"],
        "lock_manual": (not args.keep_dynamic),
    }

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "solver_budget": {
                        "n_tables": args.n_tables,
                        "n_games": args.n_games,
                        "seed": args.seed,
                    },
                    "rule_profile": args.rule_profile,
                    "overrides": overrides,
                    "winners": winners,
                    "apply_payload": payload,
                    "set_payload": set_payload,
                },
                indent=2,
            )
        )
        return

    apply_out = post_json(f"{args.api}/rules/apply_profile", payload)
    set_out = post_json(f"{args.api}/strategies/set_champions", set_payload)
    state = get_json(f"{args.api}/session/state")
    print(
        json.dumps(
            {
                "ok": True,
                "rule_applied": apply_out,
                "set_champions": set_out,
                "resolved_champions": state.get("resolved_champions", {}),
                "dynamic_resolution_enabled": state.get("dynamic_resolution_enabled"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
