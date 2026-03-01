from __future__ import annotations

from statistics import mean


def cvar(values: list[float], alpha: float = 0.1) -> float:
    if not values:
        return 0.0
    k = max(1, int(len(values) * alpha))
    return mean(sorted(values)[:k])


def first_place_rate(rank_positions: list[int]) -> float:
    if not rank_positions:
        return 0.0
    return sum(1 for r in rank_positions if r == 1) / len(rank_positions)


def robustness_score(pnls: list[float]) -> float:
    # Higher is better; penalizes downside tail.
    if not pnls:
        return 0.0
    ev = mean(pnls)
    tail = cvar(pnls, alpha=0.2)
    penalty = max(0.0, -tail)
    return ev - penalty


def composite_score(
    expected_pnl: float,
    first_rate: float,
    robustness: float,
    weights: tuple[float, float, float],
) -> float:
    w_ev, w_first, w_rob = weights
    # Scale first-place to pnl-like range.
    return (w_ev * expected_pnl) + (w_first * first_rate * 100.0) + (w_rob * robustness)


def composite_profiles() -> dict[str, tuple[float, float, float]]:
    return {
        "balanced_50_30_20": (0.50, 0.30, 0.20),
        "upside_60_30_10": (0.60, 0.30, 0.10),
        "robust_40_20_40": (0.40, 0.20, 0.40),
    }
