from __future__ import annotations

import random
from collections import Counter
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


def _sell_candidate_order(
    cards: list[Card],
    policy: str,
    preserve_weight: float = 0.85,
) -> list[tuple[float, int]]:
    if not cards:
        return []
    base = _hand_score(cards, policy)
    suit_counts = Counter(s for _, s in cards)
    scored: list[tuple[float, int]] = []
    for idx, card in enumerate(cards):
        keep = cards[:idx] + cards[idx + 1 :]
        next_score = _hand_score(keep, policy)
        loss = max(0, base - next_score)
        # High rank cards generally attract stronger bids at human tables.
        market_appeal = (card[0] * 1200) + (suit_counts[card[1]] * 250)
        sell_score = market_appeal - (loss * preserve_weight)
        scored.append((sell_score, idx))
    scored.sort(reverse=True)
    return scored


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


@dataclass
class EquityAwareStrategy:
    bid_multiplier: float = 1.0
    delta_scale: float = 6200.0
    min_delta: int = 350
    max_stack_frac: float = 0.32
    max_pot_frac: float = 0.24
    house_multiplier: float = 1.15
    preserve_weight: float = 0.9
    sell_count_early: int = 2
    sell_count_late: int = 1
    tag: str = "equity_aware"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        if not ctx.my_cards:
            return [0]
        if len(ctx.my_cards) == 1:
            return [0]

        scored = _sell_candidate_order(
            ctx.my_cards,
            policy=ctx.ranking_policy,
            preserve_weight=self.preserve_weight,
        )
        sell_count = self.sell_count_early
        if ctx.round_num >= max(1, ctx.n_orbits - 1):
            sell_count = self.sell_count_late
        sell_count = max(1, min(sell_count, len(ctx.my_cards)))
        picks = [idx for _, idx in scored[:sell_count]]
        if not picks:
            picks = _weakest_indices(ctx.my_cards, sell_count)
        return sorted(set(picks))

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0:
            return 0

        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta <= self.min_delta:
            return 0

        fair = (delta / self.delta_scale) * ctx.pot
        if ctx.seller_idx == -1:
            fair *= self.house_multiplier

        # Late orbits are more urgent; convert equity slightly more aggressively.
        orbit_urgency = 1.0 + (0.20 * (ctx.round_num / max(1, ctx.n_orbits - 1)))

        opp_aggr_vals = [
            p.aggression for seat, p in ctx.player_profiles.items() if seat != ctx.seat
        ]
        opp_aggr = (sum(opp_aggr_vals) / len(opp_aggr_vals)) if opp_aggr_vals else 0.2
        # Aggressive tables increase overpay risk in first-price auctions.
        aggr_adjust = 1.0 - max(0.0, (opp_aggr - 0.2) * 0.7)
        aggr_adjust = max(0.65, min(1.15, aggr_adjust))

        avg_stack = max(1.0, sum(ctx.stacks) / len(ctx.stacks))
        stack_ratio = my_stack / avg_stack
        stack_adjust = max(0.8, min(1.2, 0.95 + ((stack_ratio - 1.0) * 0.35)))

        raw_target = fair * self.bid_multiplier * orbit_urgency * aggr_adjust * stack_adjust
        hard_cap = min(
            my_stack,
            int(my_stack * self.max_stack_frac),
            int(max(0, ctx.pot * self.max_pot_frac)),
        )
        hard_cap = max(0, hard_cap)
        return max(0, min(hard_cap, int(raw_target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class HouseHammerStrategy:
    tag: str = "house_hammer"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        scored = _sell_candidate_order(ctx.my_cards, ctx.ranking_policy, preserve_weight=1.1)
        picks = [idx for _, idx in scored[:1]]
        return sorted(set(picks or _weakest_indices(ctx.my_cards, 1)))

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if ctx.seller_idx == -1:
            # Overweight house auction for first-mover control.
            target = int((delta / 5200.0) * ctx.pot * 1.45)
            return max(0, min(my_stack, int(my_stack * 0.55), target))
        if delta <= 700:
            return 0
        target = int((delta / 7600.0) * ctx.pot * 0.9)
        return max(0, min(my_stack, int(my_stack * 0.2), target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class ConservativePlusStrategy:
    tag: str = "conservative_plus"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        scored = _sell_candidate_order(ctx.my_cards, ctx.ranking_policy, preserve_weight=1.15)
        picks = [idx for _, idx in scored[:1]]
        return sorted(set(picks or _weakest_indices(ctx.my_cards, 1)))

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta <= 520:
            return 0

        fair = (delta / 7800.0) * ctx.pot
        if ctx.seller_idx == -1:
            fair *= 1.22
        if ctx.round_num >= max(1, ctx.n_orbits - 1):
            fair *= 1.08

        target = int(fair)
        return max(0, min(my_stack, int(my_stack * 0.18), int(ctx.pot * 0.14), target))

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
        "equity_balanced": lambda: EquityAwareStrategy(
            bid_multiplier=1.0,
            delta_scale=6200.0,
            min_delta=300,
            max_stack_frac=0.32,
            max_pot_frac=0.24,
            preserve_weight=0.9,
            sell_count_early=2,
            sell_count_late=1,
            tag="equity_balanced",
        ),
        "equity_sniper": lambda: EquityAwareStrategy(
            bid_multiplier=0.82,
            delta_scale=6600.0,
            min_delta=650,
            max_stack_frac=0.22,
            max_pot_frac=0.16,
            preserve_weight=1.15,
            sell_count_early=1,
            sell_count_late=1,
            tag="equity_sniper",
        ),
        "equity_harvest": lambda: EquityAwareStrategy(
            bid_multiplier=0.95,
            delta_scale=6100.0,
            min_delta=420,
            max_stack_frac=0.30,
            max_pot_frac=0.22,
            preserve_weight=0.72,
            sell_count_early=2,
            sell_count_late=1,
            tag="equity_harvest",
        ),
        "house_hammer": lambda: HouseHammerStrategy(),
        "conservative_plus": lambda: ConservativePlusStrategy(),
        "equity_sniper_plus": lambda: EquityAwareStrategy(
            bid_multiplier=0.88,
            delta_scale=6400.0,
            min_delta=520,
            max_stack_frac=0.25,
            max_pot_frac=0.18,
            preserve_weight=1.05,
            sell_count_early=1,
            sell_count_late=1,
            tag="equity_sniper_plus",
        ),
        "equity_sniper_ultra": lambda: EquityAwareStrategy(
            bid_multiplier=0.75,
            delta_scale=6800.0,
            min_delta=820,
            max_stack_frac=0.19,
            max_pot_frac=0.14,
            preserve_weight=1.25,
            sell_count_early=1,
            sell_count_late=1,
            tag="equity_sniper_ultra",
        ),
        "equity_flex": lambda: EquityAwareStrategy(
            bid_multiplier=0.96,
            delta_scale=6000.0,
            min_delta=450,
            max_stack_frac=0.28,
            max_pot_frac=0.21,
            preserve_weight=0.95,
            sell_count_early=2,
            sell_count_late=1,
            tag="equity_flex",
        ),
    }


def build_strategy(tag: str):
    factories = built_in_strategy_factories()
    if tag not in factories:
        raise KeyError(f"Unknown strategy tag: {tag}")
    return factories[tag]()
