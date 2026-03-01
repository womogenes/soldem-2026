#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from statistics import mean
from pathlib import Path

OBJECTIVES = ("ev", "first_place", "robustness")


def pick_top(counter: Counter[str]) -> tuple[str, int]:
    if not counter:
        return ("", 0)
    tag, votes = max(counter.items(), key=lambda kv: (kv[1], kv[0]))
    return tag, int(votes)


def build_profile_objective_summary(rows: list[dict]) -> dict:
    by_profile_objective: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    for row in rows:
        profile = row.get("profile")
        objective = row.get("objective")
        winner = row.get("winner_tag")
        if not isinstance(profile, str) or not profile:
            continue
        if objective not in OBJECTIVES:
            continue
        if not isinstance(winner, str) or not winner:
            continue
        by_profile_objective[profile][objective][winner] += 1

    out: dict[str, dict] = {}
    for profile, objective_map in sorted(by_profile_objective.items()):
        out[profile] = {}
        for objective in OBJECTIVES:
            counter = objective_map.get(objective, Counter())
            champ, votes = pick_top(counter)
            out[profile][objective] = {
                "champion_tag": champ,
                "vote_count": votes,
                "n_scenarios": int(sum(counter.values())),
                "top1_vote_counts": dict(counter),
            }
    return out


def build_upgrade_validation(summary: dict) -> dict:
    winner_counts = Counter(summary.get("winner_counts", {}))
    rows = summary.get("rows", [])
    run_id = summary.get("run_id", "")
    n_scenarios = int(summary.get("n_scenarios", len(rows)))

    objective_rows: dict[str, Counter[str]] = {obj: Counter() for obj in OBJECTIVES}
    for row in rows:
        objective = row.get("objective")
        winner = row.get("winner_tag")
        if objective in OBJECTIVES and isinstance(winner, str) and winner:
            objective_rows[objective][winner] += 1

    objective_champions: dict[str, dict] = {}
    recommended: dict[str, str] = {}
    for objective in OBJECTIVES:
        champ, votes = pick_top(objective_rows[objective])
        objective_champions[objective] = {
            "champion_tag": champ,
            "win_count": votes,
            "total": int(sum(objective_rows[objective].values())),
        }
        recommended[objective] = champ

    return {
        "run_id": run_id,
        "n_scenarios": n_scenarios,
        "winner_counts": dict(winner_counts),
        "objective_champions": objective_champions,
        "objective_strength": build_objective_strength(rows),
        "recommended_session_champions": recommended,
        "notes": "Auto-generated from distributed aggregate summary.",
    }


def _safe_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def build_objective_strength(rows: list[dict]) -> dict:
    # Adds signal beyond winner-count voting:
    # - mean rank points across all scenarios (1.0 top rank, 0.0 bottom rank)
    # - normalized winner margin to runner-up when tag wins
    per_obj_rank_points: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    per_obj_win_margins: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for row in rows:
        objective = row.get("objective")
        if objective not in OBJECTIVES:
            continue
        metric_key = row.get("metric_key")
        if not isinstance(metric_key, str) or not metric_key:
            continue
        leaderboard = row.get("leaderboard")
        if not isinstance(leaderboard, list):
            continue

        scored: list[tuple[str, float]] = []
        for entry in leaderboard:
            if not isinstance(entry, dict):
                continue
            tag = entry.get("tag")
            if not isinstance(tag, str) or not tag:
                continue
            score = _safe_float(entry.get(metric_key))
            if score is None:
                continue
            scored.append((tag, score))

        if len(scored) < 2:
            continue
        scored.sort(key=lambda it: it[1], reverse=True)

        n = len(scored)
        best_score = scored[0][1]
        second_score = scored[1][1]
        denom = max(1.0, abs(best_score), abs(second_score))

        for rank, (tag, _score) in enumerate(scored):
            rank_points = float((n - rank - 1) / (n - 1))
            per_obj_rank_points[objective][tag].append(rank_points)

        winner_tag = scored[0][0]
        margin = float((best_score - second_score) / denom)
        per_obj_win_margins[objective][winner_tag].append(margin)

    out: dict[str, dict] = {}
    for objective in OBJECTIVES:
        rank_map = per_obj_rank_points.get(objective, {})
        margin_map = per_obj_win_margins.get(objective, {})

        rank_mean = {
            tag: mean(vals)
            for tag, vals in rank_map.items()
            if vals
        }
        margin_mean = {
            tag: mean(vals)
            for tag, vals in margin_map.items()
            if vals
        }

        rank_sorted = sorted(
            rank_mean.items(),
            key=lambda kv: (kv[1], kv[0]),
            reverse=True,
        )
        margin_sorted = sorted(
            margin_mean.items(),
            key=lambda kv: (kv[1], kv[0]),
            reverse=True,
        )

        out[objective] = {
            "rank_champion_tag": rank_sorted[0][0] if rank_sorted else "",
            "rank_champion_score": rank_sorted[0][1] if rank_sorted else 0.0,
            "margin_champion_tag": margin_sorted[0][0] if margin_sorted else "",
            "margin_champion_score": margin_sorted[0][1] if margin_sorted else 0.0,
            "top_rank_mean": [
                {
                    "tag": tag,
                    "mean_rank_points": score,
                    "n_scenarios": len(rank_map.get(tag, [])),
                }
                for tag, score in rank_sorted[:5]
            ],
            "top_margin_mean": [
                {
                    "tag": tag,
                    "mean_win_margin_norm": score,
                    "n_wins": len(margin_map.get(tag, [])),
                }
                for tag, score in margin_sorted[:5]
            ],
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate distributed champion summary artifacts from aggregate summary"
    )
    ap.add_argument("--aggregate", required=True, help="Path to distributed aggregate_summary.json")
    ap.add_argument("--precomputed-out", default="")
    ap.add_argument("--upgrade-out", default="")
    ap.add_argument(
        "--promote-upgrade",
        action="store_true",
        help="Write upgrade artifact with distributed_upgrade_validation_<run_id>.json naming",
    )
    args = ap.parse_args()

    aggregate_path = Path(args.aggregate)
    summary = json.loads(aggregate_path.read_text(encoding="utf-8"))
    run_id = str(summary.get("run_id", "")).strip()

    root = aggregate_path.parents[1] if len(aggregate_path.parents) > 1 else aggregate_path.parent
    precomputed_out = (
        Path(args.precomputed_out)
        if args.precomputed_out
        else root / f"distributed_precomputed_variation_champions_{run_id}.json"
    )
    upgrade_out = (
        Path(args.upgrade_out)
        if args.upgrade_out
        else (
            root / f"distributed_upgrade_validation_{run_id}.json"
            if args.promote_upgrade
            else root / f"upgrade_validation_candidate_{run_id}.json"
        )
    )

    rows = summary.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("aggregate summary missing rows[]")

    precomputed = build_profile_objective_summary(rows)
    upgrade = build_upgrade_validation(summary)

    precomputed_out.write_text(json.dumps(precomputed, indent=2), encoding="utf-8")
    upgrade_out.write_text(json.dumps(upgrade, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "aggregate": str(aggregate_path),
                "precomputed_out": str(precomputed_out),
                "upgrade_out": str(upgrade_out),
                "recommended_session_champions": upgrade["recommended_session_champions"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
