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


def prior_champions(rule_profile: str, overrides: dict) -> dict[str, str]:
    n_orbits = int(overrides.get("n_orbits", 3))
    start_chips = int(overrides.get("start_chips", 200))
    sprint_profile = n_orbits <= 2 and start_chips <= 150

    first_place = "equity_evolved_v1"
    if sprint_profile:
        first_place = "pot_fraction"
    elif rule_profile == "baseline_v1":
        first_place = "meta_switch"

    return {
        "ev": "equity_evolved_v1",
        "first_place": first_place,
        "robustness": "equity_evolved_v1",
    }


def stabilized_winners(
    solver_out: dict,
    priors: dict[str, str],
    *,
    ev_gap: float,
    first_gap: float,
    robustness_gap: float,
) -> tuple[dict[str, str], dict[str, dict]]:
    gaps = {
        "ev": ev_gap,
        "first_place": first_gap,
        "robustness": robustness_gap,
    }
    detail: dict[str, dict] = {}
    selected = dict(priors)
    ow = solver_out.get("objective_winners", {})
    for objective in ["ev", "first_place", "robustness"]:
        rec = ow.get(objective, {})
        ranking = rec.get("ranking", [])
        if not ranking:
            detail[objective] = {
                "decision": "prior_no_ranking",
                "winner": priors[objective],
            }
            continue

        top = ranking[0]
        top_tag = str(top.get("tag", "")).strip()
        top_metric = float(top.get("mean_metric_value", 0.0))
        second_metric = (
            float(ranking[1].get("mean_metric_value", 0.0))
            if len(ranking) > 1
            else top_metric
        )
        gap = top_metric - second_metric
        prior = priors[objective]

        if top_tag and (top_tag == prior or gap >= gaps[objective]):
            selected[objective] = top_tag
            decision = "solver_top"
        else:
            selected[objective] = prior
            decision = "prior_guardrail"

        detail[objective] = {
            "prior": prior,
            "solver_top": top_tag,
            "solver_gap": gap,
            "threshold": gaps[objective],
            "decision": decision,
            "selected": selected[objective],
        }

    return selected, detail


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
    ap.add_argument("--ev-gap", type=float, default=12.0)
    ap.add_argument("--first-gap", type=float, default=0.04)
    ap.add_argument("--robustness-gap", type=float, default=20.0)
    ap.add_argument("--no-prior-guardrail", action="store_true")
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
    solver_winners = objective_winners(solver_out)
    priors = prior_champions(args.rule_profile, overrides)
    if args.no_prior_guardrail:
        winners = solver_winners
        detail = {
            k: {
                "decision": "solver_top_no_guardrail",
                "solver_top": solver_winners[k],
                "selected": solver_winners[k],
            }
            for k in ["ev", "first_place", "robustness"]
        }
    else:
        winners, detail = stabilized_winners(
            solver_out,
            priors,
            ev_gap=args.ev_gap,
            first_gap=args.first_gap,
            robustness_gap=args.robustness_gap,
        )

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
                    "priors": priors,
                    "solver_winners": solver_winners,
                    "winners": winners,
                    "winner_decisions": detail,
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
