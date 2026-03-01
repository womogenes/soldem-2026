"""Hand evaluation utilities for Sold 'Em.

Cards are represented as ``(value, suit)`` where values are 1-10 and suits are
``C D H S X``. The ``rarity_50`` policy ranks categories by exact rarity in the
50-card deck. ``standard_plus_five_kind`` keeps familiar poker ordering with
five-of-a-kind added above straight flush.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Literal

Card = tuple[int, str]
Category = Literal[
    "five_kind",
    "straight_flush",
    "four_kind",
    "full_house",
    "flush",
    "straight",
    "three_kind",
    "two_pair",
    "one_pair",
    "high_card",
]

CATEGORY_RARITY_COUNTS_50: dict[Category, int] = {
    "five_kind": 10,
    "straight_flush": 30,
    "flush": 1230,
    "four_kind": 2250,
    "full_house": 9000,
    "straight": 18720,
    "three_kind": 90000,
    "two_pair": 180000,
    "high_card": 767520,
    "one_pair": 1050000,
}

RARITY_ORDER_50: list[Category] = [
    name for name, _ in sorted(CATEGORY_RARITY_COUNTS_50.items(), key=lambda kv: kv[1])
]

STANDARD_ORDER: list[Category] = [
    "five_kind",
    "straight_flush",
    "four_kind",
    "full_house",
    "flush",
    "straight",
    "three_kind",
    "two_pair",
    "one_pair",
    "high_card",
]


def ranking_order(policy: str = "rarity_50") -> list[Category]:
    if policy == "standard_plus_five_kind":
        return STANDARD_ORDER
    if policy == "rarity_50":
        return RARITY_ORDER_50
    raise ValueError(f"Unknown ranking policy: {policy}")


def _category_rank_map(policy: str) -> dict[Category, int]:
    order = ranking_order(policy)
    return {cat: len(order) - i for i, cat in enumerate(order)}


def _is_straight(values_desc: list[int]) -> bool:
    uniq = sorted(set(values_desc))
    return len(uniq) == 5 and (max(uniq) - min(uniq) == 4)


def _evaluate_five(cards: list[Card]) -> tuple[Category, tuple[int, ...]]:
    values = sorted((v for v, _ in cards), reverse=True)
    suits = [s for _, s in cards]
    counts = Counter(values)
    # (count, value) sorted high count then high value for deterministic kickers.
    count_values = sorted(((cnt, val) for val, cnt in counts.items()), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = _is_straight(values)

    if count_values[0][0] == 5:
        return ("five_kind", (count_values[0][1],))

    if is_straight and is_flush:
        return ("straight_flush", (max(values),))

    if count_values[0][0] == 4:
        quad = count_values[0][1]
        kicker = max(v for v in values if v != quad)
        return ("four_kind", (quad, kicker))

    if count_values[0][0] == 3 and count_values[1][0] == 2:
        return ("full_house", (count_values[0][1], count_values[1][1]))

    if is_flush:
        return ("flush", tuple(values))

    if is_straight:
        return ("straight", (max(values),))

    if count_values[0][0] == 3:
        triple = count_values[0][1]
        kickers = tuple(sorted((v for v in values if v != triple), reverse=True))
        return ("three_kind", (triple, *kickers))

    if count_values[0][0] == 2 and count_values[1][0] == 2:
        p1 = count_values[0][1]
        p2 = count_values[1][1]
        pair_high = max(p1, p2)
        pair_low = min(p1, p2)
        kicker = max(v for v in values if v != pair_high and v != pair_low)
        return ("two_pair", (pair_high, pair_low, kicker))

    if count_values[0][0] == 2:
        pair = count_values[0][1]
        kickers = tuple(sorted((v for v in values if v != pair), reverse=True))
        return ("one_pair", (pair, *kickers))

    return ("high_card", tuple(values))


def classify_hand(
    a: list[Card],
    b: list[Card] | None = None,
    policy: str = "rarity_50",
) -> tuple[int, ...]:
    """Return an orderable tuple for the best 5-card subset.

    Signature keeps backward compatibility with legacy ``classify_hand(a, b)``.
    """
    cards = a if b is None else b
    if not cards:
        return (-1,)
    if len(cards) < 5:
        values = sorted((v for v, _ in cards), reverse=True)
        return (0, *values)

    rank_map = _category_rank_map(policy)

    def rank_key(five: list[Card]) -> tuple[int, ...]:
        cat, tie_break = _evaluate_five(five)
        return (rank_map[cat], *tie_break)

    if len(cards) == 5:
        return rank_key(cards)

    return max(rank_key(list(combo)) for combo in combinations(cards, 5))


def compare_hands(a: list[Card], b: list[Card], policy: str = "rarity_50") -> int:
    """Return 1 if a>b, -1 if a<b, 0 if equal under ``policy``."""
    sa = classify_hand(a, policy=policy)
    sb = classify_hand(b, policy=policy)
    if sa > sb:
        return 1
    if sa < sb:
        return -1
    return 0


def rarity_table_50() -> list[tuple[Category, int]]:
    return [(cat, CATEGORY_RARITY_COUNTS_50[cat]) for cat in RARITY_ORDER_50]
