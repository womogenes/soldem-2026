"""
Comparator for hands. Cards are represented (value, suit), e.g. (1, "H")
"""
from itertools import combinations
from collections import Counter

def _score_five(cards: list[tuple[int, str]]) -> tuple:
    values = sorted((v for v, _ in cards), reverse=True)
    suits = [s for _, s in cards]
    value_counts = Counter(values)
    count_values = sorted(
        ((cnt, val) for val, cnt in value_counts.items()),
        key=lambda x: (x[0], x[1]),
        reverse=True,
    )

    is_flush = len(set(suits)) == 1
    uniq_vals = sorted(set(values))
    is_straight = len(uniq_vals) == 5 and (max(uniq_vals) - min(uniq_vals) == 4)

    if count_values[0][0] == 5:
        return (9, count_values[0][1])
    if is_straight and is_flush:
        return (8, max(values))
    if count_values[0][0] == 4:
        quad = count_values[0][1]
        kicker = max(v for v in values if v != quad)
        return (7, quad, kicker)
    if count_values[0][0] == 3 and count_values[1][0] == 2:
        return (6, count_values[0][1], count_values[1][1])
    if is_flush:
        return (5, *values)
    if is_straight:
        return (4, max(values))
    if count_values[0][0] == 3:
        triple = count_values[0][1]
        kickers = sorted((v for v in values if v != triple), reverse=True)
        return (3, triple, *kickers)
    if count_values[0][0] == 2 and count_values[1][0] == 2:
        pair_high = max(count_values[0][1], count_values[1][1])
        pair_low = min(count_values[0][1], count_values[1][1])
        kicker = max(v for v in values if v != pair_high and v != pair_low)
        return (2, pair_high, pair_low, kicker)
    if count_values[0][0] == 2:
        pair = count_values[0][1]
        kickers = sorted((v for v in values if v != pair), reverse=True)
        return (1, pair, *kickers)
    return (0, *values)


def classify_hand(a: list[tuple], b: list[tuple] | None = None) -> tuple:
    """
    Return value of a hand. In order: 
      - five of a kind
      - straight flush
      - four of a kind
      - full house
      - flush
      - straight
      - three of a kind
      - two pair
      - one pair
      - high card
    """
    cards = a if b is None else b
    if len(cards) == 5:
        return _score_five(cards)
    return max(_score_five(list(combo)) for combo in combinations(cards, 5))

def compare_hands(a: list[tuple], b: list[tuple]):
    """
    Determine whether a>b, a==b, or a<b. Return 1, 0, or -1.
    """
    sa = classify_hand(a)
    sb = classify_hand(b)
    if sa > sb:
        return 1
    if sa < sb:
        return -1
    return 0
