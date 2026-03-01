from __future__ import annotations

import random
from dataclasses import dataclass

from game.utils import classify_hand
from strategies.base import Card, StrategyContext


def _hand_score(cards: list[Card], policy: str) -> int:
    key = classify_hand(cards, policy=policy)
    score = 0
    for part in key:
        score = (score * 20) + max(0, int(part))
    return score


def _best_delta(my_cards: list[Card], auction_cards: list[Card], policy: str) -> tuple[int, int]:
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


def _weakest_indices(cards: list[Card], count: int = 1) -> list[int]:
    ranked = sorted(enumerate(cards), key=lambda kv: (kv[1][0], kv[1][1]))
    return [idx for idx, _ in ranked[:count]]


@dataclass
class RandomStrategy:
    seed: int = 0
    tag: str = "random"

    def __post_init__(self):
        self.rng = random.Random(self.seed)

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        n = len(ctx.my_cards)
        if n <= 1:
            return [0]
        k = self.rng.randint(1, min(2, n))
        return sorted(self.rng.sample(range(n), k))

    def bid_amount(self, ctx: StrategyContext) -> int:
        cap = max(0, ctx.stacks[ctx.seat])
        return self.rng.randint(0, cap)

    def choose_won_card(self, ctx: StrategyContext) -> int:
        return self.rng.randrange(len(ctx.auction_cards))


@dataclass
class PotFractionStrategy:
    fraction: float = 0.25
    tag: str = "pot_fraction"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        max_bid = ctx.stacks[ctx.seat]
        target = int(ctx.pot * self.fraction)
        return max(0, min(max_bid, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class DeltaValueStrategy:
    multiplier: float = 1.0
    floor: int = 0
    tag: str = "delta_value"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        # Sell low-impact cards first.
        return _weakest_indices(ctx.my_cards, 2)

    def bid_amount(self, ctx: StrategyContext) -> int:
        max_bid = ctx.stacks[ctx.seat]
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        fair = int((delta / 5000.0) * ctx.pot)
        target = int(max(self.floor, fair) * self.multiplier)
        return max(0, min(max_bid, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class ConservativeStrategy:
    tag: str = "conservative"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        max_bid = ctx.stacks[ctx.seat]
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta <= 0:
            return 0
        target = int(min(ctx.pot * 0.15, delta / 7000.0 * ctx.pot))
        return max(0, min(max_bid, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class BullyStrategy:
    pressure: float = 0.45
    tag: str = "bully"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        avg_stack = sum(ctx.stacks) / len(ctx.stacks)
        base = int(ctx.pot * self.pressure)
        if my_stack >= avg_stack:
            base = int(base * 1.2)
        else:
            base = int(base * 0.8)
        return max(0, min(my_stack, base))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class SellerProfitStrategy:
    reserve_ratio: float = 0.3
    tag: str = "seller_profit"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        # Offer two lower cards to improve chance of extracting chips.
        return _weakest_indices(ctx.my_cards, 2)

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        target = int(ctx.pot * self.reserve_ratio)
        return max(0, min(my_stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class AdaptiveProfileStrategy:
    base_fraction: float = 0.25
    tag: str = "adaptive_profile"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        avg_opp_aggr = 0.0
        n = 0
        for seat, profile in ctx.player_profiles.items():
            if seat == ctx.seat:
                continue
            avg_opp_aggr += profile.aggression
            n += 1
        if n:
            avg_opp_aggr /= n

        frac = self.base_fraction
        if avg_opp_aggr > 0.4:
            frac *= 0.85
        elif avg_opp_aggr < 0.2:
            frac *= 1.2

        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        delta_term = max(0.0, min(0.3, delta / 12000.0))
        target = int(ctx.pot * (frac + delta_term))
        return max(0, min(my_stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


def built_in_strategy_factories() -> dict[str, callable]:
    return {
        "random": lambda: RandomStrategy(),
        "pot_fraction": lambda: PotFractionStrategy(0.25),
        "delta_value": lambda: DeltaValueStrategy(multiplier=1.0),
        "conservative": lambda: ConservativeStrategy(),
        "bully": lambda: BullyStrategy(),
        "seller_profit": lambda: SellerProfitStrategy(),
        "adaptive_profile": lambda: AdaptiveProfileStrategy(),
    }


def build_strategy(tag: str):
    factories = built_in_strategy_factories()
    if tag not in factories:
        raise KeyError(f"Unknown strategy tag: {tag}")
    return factories[tag]()
