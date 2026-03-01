from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBJECTIVES = ("ev", "first_place", "robustness")


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _pick_top(counter: dict[str, Any]) -> str | None:
    scored: list[tuple[str, float]] = []
    for tag, value in counter.items():
        if not isinstance(tag, str) or not tag:
            continue
        num = _as_number(value)
        if num is None:
            continue
        scored.append((tag, num))
    if not scored:
        return None
    scored.sort(key=lambda item: (item[1], item[0]), reverse=True)
    return scored[0][0]


def _champions_from_distributed_summary(
    payload: dict[str, Any], default_tag: str
) -> tuple[dict[str, str], dict[str, Any]]:
    winners = payload.get("winner_counts")
    if not isinstance(winners, dict) or not winners:
        raise ValueError("missing winner_counts")

    overall = _pick_top(winners) or default_tag
    champions = {objective: overall for objective in OBJECTIVES}

    by_objective = payload.get("winner_by_objective")
    if isinstance(by_objective, dict):
        for objective in OBJECTIVES:
            maybe_counter = by_objective.get(objective)
            if isinstance(maybe_counter, dict):
                picked = _pick_top(maybe_counter)
                if picked:
                    champions[objective] = picked

    details = {
        "source_type": "distributed_counts",
        "total_scenarios": payload.get("total_scenarios", payload.get("n_scenarios")),
        "winner_counts": winners,
    }
    return champions, details


def _champions_from_param_sweep_summary(
    payload: dict[str, Any], default_tag: str
) -> tuple[dict[str, str], dict[str, Any]]:
    rows = payload.get("candidate_summary")
    if not isinstance(rows, list) or not rows:
        raise ValueError("missing candidate_summary")

    def row_sort_key(row: dict[str, Any]) -> tuple[float, float, float]:
        mean_delta = _as_number(row.get("mean_delta_vs_champion")) or -1e18
        wins = _as_number(row.get("wins")) or 0.0
        losses = _as_number(row.get("losses")) or 0.0
        return (mean_delta, wins, -losses)

    valid_rows = [row for row in rows if isinstance(row, dict) and isinstance(row.get("candidate"), str)]
    if not valid_rows:
        raise ValueError("candidate_summary has no valid rows")

    best_overall = max(valid_rows, key=row_sort_key)
    overall = best_overall.get("candidate") or default_tag
    champions = {objective: overall for objective in OBJECTIVES}

    for objective in OBJECTIVES:
        best_obj_tag = overall
        best_obj_key: tuple[float, float, float] | None = None
        for row in valid_rows:
            by_obj = row.get("by_objective")
            if not isinstance(by_obj, dict):
                continue
            obj_stats = by_obj.get(objective)
            if not isinstance(obj_stats, dict):
                continue
            key = (
                _as_number(obj_stats.get("mean_delta")) or -1e18,
                _as_number(obj_stats.get("wins")) or 0.0,
                -(_as_number(obj_stats.get("ties")) or 0.0),
            )
            if best_obj_key is None or key > best_obj_key:
                best_obj_key = key
                best_obj_tag = row.get("candidate") or best_obj_tag
        champions[objective] = best_obj_tag

    details = {
        "source_type": "param_sweep",
        "run_id": payload.get("run_id"),
        "n_candidates": payload.get("n_candidates"),
    }
    return champions, details


def _champions_from_profile_objective_summary(
    payload: dict[str, Any], default_tag: str
) -> tuple[dict[str, str], dict[str, Any]]:
    objective_votes: dict[str, dict[str, float]] = {obj: {} for obj in OBJECTIVES}
    for _profile_name, profile_data in payload.items():
        if not isinstance(profile_data, dict):
            continue
        for objective in OBJECTIVES:
            obj_data = profile_data.get(objective)
            if not isinstance(obj_data, dict):
                continue
            tag = obj_data.get("champion_tag")
            if not isinstance(tag, str) or not tag:
                continue
            votes = _as_number(obj_data.get("vote_count"))
            if votes is None:
                votes = 1.0
            objective_votes[objective][tag] = objective_votes[objective].get(tag, 0.0) + votes

    champions = {obj: default_tag for obj in OBJECTIVES}
    for objective in OBJECTIVES:
        picked = _pick_top(objective_votes[objective])
        if picked:
            champions[objective] = picked

    details = {
        "source_type": "profile_objective_votes",
        "winner_by_objective": objective_votes,
    }
    return champions, details


def champions_from_summary_payload(
    payload: dict[str, Any], default_tag: str
) -> tuple[dict[str, str], dict[str, Any]]:
    manual = payload.get("recommended_session_champions")
    if isinstance(manual, dict):
        champions = {objective: default_tag for objective in OBJECTIVES}
        for objective in OBJECTIVES:
            tag = manual.get(objective)
            if isinstance(tag, str) and tag:
                champions[objective] = tag
        details = {
            "source_type": "recommended_session_champions",
            "run_id": payload.get("run_id"),
            "n_scenarios": payload.get("n_scenarios"),
        }
        return champions, details
    if "winner_counts" in payload:
        return _champions_from_distributed_summary(payload, default_tag)
    if "candidate_summary" in payload:
        return _champions_from_param_sweep_summary(payload, default_tag)
    if payload and isinstance(next(iter(payload.values())), dict):
        sample = next(iter(payload.values()))
        if any(obj in sample for obj in OBJECTIVES):
            return _champions_from_profile_objective_summary(payload, default_tag)
    raise ValueError("unrecognized summary payload format")


def load_champions_from_summary_file(
    path: Path | str, default_tag: str
) -> tuple[dict[str, str], dict[str, Any]]:
    summary_path = Path(path)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    champions, details = champions_from_summary_payload(payload, default_tag)
    details = {
        **details,
        "summary_path": str(summary_path),
    }
    return champions, details


def find_latest_summary_path(base_dir: Path | str) -> Path | None:
    root = Path(base_dir)
    patterns = [
        "distributed_upgrade_validation_*.json",
        "distributed_master_summary_*.json",
        "distributed_precomputed_variation_champions_*.json",
        "param_sweep_*/aggregate_summary.json",
    ]
    for pattern in patterns:
        candidates = list(root.glob(pattern))
        if candidates:
            return max(candidates, key=lambda p: (p.stat().st_mtime, p.name))
    return None
