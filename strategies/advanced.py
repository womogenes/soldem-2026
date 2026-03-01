from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from game.utils import classify_hand
from strategies.base import Card, StrategyContext


def _hand_score(cards: list[Card], policy: str) -> int:
    key = classify_hand(cards, policy=policy)
    score = 0
    for part in key:
        score = (score * 20) + max(0, int(part))
    return score


def _best_delta(my_cards: list[Card], auction_cards: list[Card], policy: str) -> tuple[int, int]:
    if not auction_cards:
        return 0, 0
    base = _hand_score(my_cards, policy)
    best_idx = 0
    best_delta = -10**9
    for i, card in enumerate(auction_cards):
        nxt = _hand_score(my_cards + [card], policy)
        d = nxt - base
        if d > best_delta:
            best_delta = d
            best_idx = i
    return best_idx, best_delta


def _removal_cost(cards: list[Card], idx: int, policy: str) -> int:
    if not cards or not (0 <= idx < len(cards)):
        return 0
    base = _hand_score(cards, policy)
    trimmed = cards[:idx] + cards[idx + 1 :]
    nxt = _hand_score(trimmed, policy)
    return max(0, base - nxt)


def _market_value(card: Card) -> float:
    value, suit = card
    suit_bonus = 0.8 if suit == "X" else 0.0
    return (value / 10.0) + suit_bonus


def _opp_aggression(ctx: StrategyContext) -> float:
    vals = [
        prof.aggression
        for seat, prof in ctx.player_profiles.items()
        if seat != ctx.seat and prof.bid_count > 0
    ]
    return mean(vals) if vals else 0.22


def _objective_multiplier(objective: str) -> float:
    if objective == "first_place":
        return 1.18
    if objective == "robustness":
        return 0.82
    return 1.0


@dataclass
class ProbabilisticValueStrategy:
    bid_scale: float = 1.0
    sell_count: int = 2
    damage_weight: float = 0.75
    market_weight: float = 0.85
    aggression_weight: float = 0.55
    stack_cap_fraction: float = 0.6
    min_delta_to_bid: int = 400
    tag: str = "prob_value"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        if not ctx.my_cards:
            return [0]
        scores: list[tuple[float, int]] = []
        for idx, card in enumerate(ctx.my_cards):
            damage = _removal_cost(ctx.my_cards, idx, ctx.ranking_policy)
            market = _market_value(card)
            utility = (self.market_weight * market) - (
                self.damage_weight * (damage / 5000.0)
            )
            scores.append((utility, idx))

        scores.sort(reverse=True)
        k = max(1, min(self.sell_count, len(scores)))
        return sorted(idx for _, idx in scores[:k])

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = max(0, ctx.stacks[ctx.seat])
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta < self.min_delta_to_bid:
            return 0

        fair = (delta / 5000.0) * max(1, ctx.pot)
        progress = (ctx.round_num + 1) / max(1, ctx.n_orbits)
        objective_mult = _objective_multiplier(ctx.objective)
        aggression_mult = 1.0 + ((_opp_aggression(ctx) - 0.2) * self.aggression_weight)
        temporal_mult = 0.9 + (0.35 * progress)
        raw = fair * self.bid_scale * objective_mult * aggression_mult * temporal_mult

        cap = min(my_stack, int(my_stack * self.stack_cap_fraction))
        return max(0, min(cap, int(raw)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class RiskManagedSniperStrategy:
    bid_scale: float = 0.95
    trigger_delta: int = 2200
    late_round_bonus: float = 0.35
    stack_cap_fraction: float = 0.42
    sell_count: int = 1
    tag: str = "risk_sniper"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        if not ctx.my_cards:
            return [0]
        ranked = []
        for idx, card in enumerate(ctx.my_cards):
            damage = _removal_cost(ctx.my_cards, idx, ctx.ranking_policy)
            market = _market_value(card)
            ranked.append((((market * 1.2) - (damage / 5000.0)), idx))
        ranked.sort(reverse=True)
        k = max(1, min(self.sell_count, len(ranked)))
        return sorted(idx for _, idx in ranked[:k])

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = max(0, ctx.stacks[ctx.seat])
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta < self.trigger_delta:
            return 0

        fair = (delta / 5000.0) * max(1, ctx.pot)
        progress = (ctx.round_num + 1) / max(1, ctx.n_orbits)
        multiplier = _objective_multiplier(ctx.objective) * (
            1.0 + self.late_round_bonus * progress
        )
        target = fair * self.bid_scale * multiplier
        cap = min(my_stack, int(my_stack * self.stack_cap_fraction))
        return max(0, min(cap, int(target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class SellerExtractionStrategy:
    sell_count: int = 2
    reserve_bid_floor: float = 0.08
    opportunistic_delta: int = 3200
    tag: str = "seller_extraction"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        if not ctx.my_cards:
            return [0]
        ranked = []
        for idx, card in enumerate(ctx.my_cards):
            damage = _removal_cost(ctx.my_cards, idx, ctx.ranking_policy)
            market = _market_value(card)
            ranked.append((((market * 1.35) - (damage / 6000.0)), idx))
        ranked.sort(reverse=True)
        k = max(1, min(self.sell_count, len(ranked)))
        return sorted(idx for _, idx in ranked[:k])

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = max(0, ctx.stacks[ctx.seat])
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta < self.opportunistic_delta:
            return 0
        floor = int(ctx.pot * self.reserve_bid_floor)
        return max(0, min(my_stack, floor))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx
