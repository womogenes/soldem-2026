from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from itertools import product
from statistics import mean

from game.utils import classify_hand
from strategies.base import Card, StrategyContext

BASE_DECK = list(product(range(1, 11), "CDHSX"))


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


def _weakest_indices(cards: list[Card], count: int = 1) -> list[int]:
    ranked = sorted(enumerate(cards), key=lambda kv: (kv[1][0], kv[1][1]))
    return [idx for idx, _ in ranked[:count]]


def _hold_loss(cards: list[Card], idx: int, policy: str) -> int:
    if idx < 0 or idx >= len(cards) or len(cards) <= 1:
        return 0
    before = _hand_score(cards, policy)
    after = _hand_score([c for i, c in enumerate(cards) if i != idx], policy)
    return max(0, before - after)


def _least_costly_sales(
    cards: list[Card],
    policy: str,
    count: int = 1,
    prefer_high_value: bool = False,
) -> list[int]:
    rows: list[tuple[int, int, str, int]] = []
    for idx, card in enumerate(cards):
        loss = _hold_loss(cards, idx, policy)
        value = card[0]
        tie_value = -value if prefer_high_value else value
        rows.append((loss, tie_value, card[1], idx))
    rows.sort()
    return [idx for *_rest, idx in rows[: max(1, min(count, len(cards)))]]


def _avg_opp_aggression(ctx: StrategyContext) -> float:
    vals = [
        p.aggression
        for seat, p in ctx.player_profiles.items()
        if seat != ctx.seat and p.bid_count > 0
    ]
    return (sum(vals) / len(vals)) if vals else 0.22


def _ctx_seed(ctx: StrategyContext, extra: int = 0) -> int:
    sig = 0
    for v, s in sorted(ctx.my_cards + ctx.auction_cards):
        sig = (sig * 1315423911 + (v * 31) + ord(s)) & 0xFFFFFFFF
    return (
        (ctx.seat + 1) * 1000003
        + (ctx.round_num + 1) * 9176
        + (ctx.pot + 1) * 131
        + sig
        + extra
    ) & 0xFFFFFFFF


def _equity_vs_random(
    my_cards: list[Card],
    policy: str,
    n_players: int,
    samples: int,
    seed: int,
) -> float:
    if samples <= 0:
        return 0.0
    rng = random.Random(seed)
    deck = [c for c in BASE_DECK if c not in my_cards]
    need = (n_players - 1) * 5
    if len(deck) < need:
        return 0.0

    my_key = classify_hand(my_cards, policy=policy)
    wins = 0.0
    for _ in range(samples):
        draw = rng.sample(deck, need)
        opp_keys = [
            classify_hand(draw[(i * 5) : ((i + 1) * 5)], policy=policy)
            for i in range(n_players - 1)
        ]
        all_keys = [my_key, *opp_keys]
        best = max(all_keys)
        if my_key == best:
            ties = sum(1 for key in all_keys if key == best)
            wins += 1.0 / ties
    return wins / samples


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
        market_appeal = (card[0] * 1200) + (suit_counts[card[1]] * 250)
        sell_score = market_appeal - (loss * preserve_weight)
        scored.append((sell_score, idx))
    scored.sort(reverse=True)
    return scored


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


def _objective_multiplier(objective: str) -> float:
    if objective == "first_place":
        return 1.18
    if objective == "robustness":
        return 0.82
    return 1.0


@dataclass
class ElasticConservativeStrategy:
    max_pot_frac: float = 0.14
    delta_scale: float = 9000.0
    sell_count_early: int = 2
    house_discount: float = 0.55
    tag: str = "elastic_conservative"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        count = self.sell_count_early if ctx.round_num < max(1, ctx.n_orbits - 1) else 1
        return _least_costly_sales(
            ctx.my_cards,
            ctx.ranking_policy,
            count=count,
            prefer_high_value=True,
        )

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0:
            return 0

        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta <= 0:
            return 0

        fair = (delta / self.delta_scale) * ctx.pot
        cap_frac = self.max_pot_frac
        avg_aggr = _avg_opp_aggression(ctx)
        if avg_aggr > 0.40:
            cap_frac *= 0.82
        elif avg_aggr < 0.18:
            cap_frac *= 1.08

        if ctx.objective == "first_place":
            cap_frac *= 1.10
        elif ctx.objective == "robustness":
            cap_frac *= 0.86

        if ctx.seller_idx == -1:
            cap_frac *= self.house_discount

        if ctx.round_num >= max(1, ctx.n_orbits - 1):
            cap_frac *= 1.18

        target = min(ctx.pot * cap_frac, fair)
        return max(0, min(my_stack, int(target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class MarketMakerStrategy:
    reserve_frac: float = 0.11
    tag: str = "market_maker"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        count = 2 if ctx.round_num < max(1, ctx.n_orbits - 1) else 1
        return _least_costly_sales(
            ctx.my_cards,
            ctx.ranking_policy,
            count=count,
            prefer_high_value=True,
        )

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0:
            return 0
        _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if delta <= 0:
            return 0

        pressure = max(0.7, min(1.25, 1.0 - (_avg_opp_aggression(ctx) - 0.2)))
        fair = (delta / 12000.0) * ctx.pot
        cap = ctx.pot * self.reserve_frac * pressure
        if ctx.seller_idx == -1:
            cap *= 0.55
        target = min(cap, fair)
        return max(0, min(my_stack, int(target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class MonteCarloEdgeStrategy:
    mc_samples: int = 18
    max_pot_frac: float = 0.22
    tag: str = "mc_edge"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        count = 2 if ctx.round_num < max(1, ctx.n_orbits - 1) else 1
        return _least_costly_sales(ctx.my_cards, ctx.ranking_policy, count=count)

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0 or not ctx.auction_cards:
            return 0

        best_idx, score_delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if score_delta <= 0:
            return 0

        base_seed = _ctx_seed(ctx, extra=17)
        n_players = len(ctx.stacks)
        p_base = _equity_vs_random(
            ctx.my_cards,
            policy=ctx.ranking_policy,
            n_players=n_players,
            samples=self.mc_samples,
            seed=base_seed,
        )
        p_with = _equity_vs_random(
            ctx.my_cards + [ctx.auction_cards[best_idx]],
            policy=ctx.ranking_policy,
            n_players=n_players,
            samples=self.mc_samples,
            seed=base_seed + 91,
        )
        delta_p = max(0.0, p_with - p_base)
        fair = (delta_p * ctx.pot) + ((score_delta / 12000.0) * ctx.pot * 0.35)
        if fair <= 0:
            return 0

        cap_frac = self.max_pot_frac
        if ctx.objective == "first_place":
            cap_frac *= 1.15
        elif ctx.objective == "robustness":
            cap_frac *= 0.82
        if ctx.seller_idx == -1:
            cap_frac *= 0.60
        if _avg_opp_aggression(ctx) > 0.45:
            cap_frac *= 0.82
        if delta_p < 0.015 and score_delta < 1100:
            return 0

        target = min(ctx.pot * cap_frac, fair)
        return max(0, min(my_stack, int(target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class RegimeSwitchStrategy:
    reserve_base: float = 0.12
    reserve_min: float = 0.08
    reserve_max: float = 0.19
    eq_samples: int = 10
    jitter: float = 0.10
    tag: str = "regime_switch"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        count = 2 if ctx.round_num < max(1, ctx.n_orbits - 1) else 1
        return _least_costly_sales(
            ctx.my_cards,
            ctx.ranking_policy,
            count=count,
            prefer_high_value=True,
        )

    def bid_amount(self, ctx: StrategyContext) -> int:
        my_stack = ctx.stacks[ctx.seat]
        if my_stack <= 0 or not ctx.auction_cards:
            return 0

        best_idx, score_delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        if score_delta <= 0:
            return 0

        avg_stack = sum(ctx.stacks) / len(ctx.stacks)
        avg_aggr = _avg_opp_aggression(ctx)
        stack_ratio = my_stack / max(1.0, avg_stack)

        reserve = self.reserve_base
        if avg_aggr > 0.44:
            reserve *= 0.72
        elif avg_aggr < 0.18:
            reserve *= 1.16
        if stack_ratio < 0.90:
            reserve *= 1.12
        elif stack_ratio > 1.15:
            reserve *= 0.88
        if ctx.objective == "first_place":
            reserve *= 1.15
        elif ctx.objective == "robustness":
            reserve *= 0.78
        if ctx.round_num >= max(1, ctx.n_orbits - 1):
            reserve *= 1.12
        if ctx.seller_idx == -1:
            reserve *= 0.56
        reserve = max(self.reserve_min, min(self.reserve_max, reserve))

        base_seed = _ctx_seed(ctx, extra=313)
        p0 = _equity_vs_random(
            ctx.my_cards,
            policy=ctx.ranking_policy,
            n_players=len(ctx.stacks),
            samples=self.eq_samples,
            seed=base_seed,
        )
        p1 = _equity_vs_random(
            ctx.my_cards + [ctx.auction_cards[best_idx]],
            policy=ctx.ranking_policy,
            n_players=len(ctx.stacks),
            samples=self.eq_samples,
            seed=base_seed + 29,
        )
        delta_p = max(0.0, p1 - p0)

        fair = (delta_p * ctx.pot) + ((score_delta / 12000.0) * ctx.pot * 0.40)
        cap = ctx.pot * reserve

        rng = random.Random(base_seed + 101)
        jitter_mult = 1.0 + rng.uniform(-self.jitter, self.jitter)
        target = min(fair, cap) * jitter_mult
        if delta_p < 0.012 and score_delta < 900:
            return 0
        return max(0, min(my_stack, int(target)))

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
        if not ctx.my_cards or len(ctx.my_cards) == 1:
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

        orbit_urgency = 1.0 + (0.20 * (ctx.round_num / max(1, ctx.n_orbits - 1)))
        opp_aggr = _avg_opp_aggression(ctx)
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
        return max(0, min(max(0, hard_cap), int(raw_target)))

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


@dataclass
class V4MetaSwitchStrategy:
    tag: str = "meta_switch_v4"

    def __post_init__(self):
        self._conservative = ConservativePlusStrategy()
        self._sniper = EquityAwareStrategy(
            bid_multiplier=0.75,
            delta_scale=6800.0,
            min_delta=820,
            max_stack_frac=0.19,
            max_pot_frac=0.14,
            preserve_weight=1.25,
            sell_count_early=1,
            sell_count_late=1,
            tag="equity_sniper_ultra",
        )

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def _delegate(self, ctx: StrategyContext):
        vals = [
            p.aggression
            for seat, p in ctx.player_profiles.items()
            if seat != ctx.seat and p.bid_count > 0
        ]
        avg_aggr = (sum(vals) / len(vals)) if vals else 0.0
        if ctx.objective == "robustness":
            return self._conservative
        if len(vals) >= 2 and avg_aggr > 0.32:
            return self._conservative
        if len(vals) >= 2 and 0.16 <= avg_aggr <= 0.30:
            return self._sniper
        if ctx.objective == "first_place":
            if len(vals) >= 2 and avg_aggr <= 0.14:
                return None
            return self._sniper
        return self._conservative

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        d = self._delegate(ctx)
        if d is None:
            return _weakest_indices(ctx.my_cards, 1)
        return d.choose_sell_indices(ctx)

    def bid_amount(self, ctx: StrategyContext) -> int:
        d = self._delegate(ctx)
        if d is None:
            return max(0, min(ctx.stacks[ctx.seat], int(ctx.pot * 0.25)))
        return d.bid_amount(ctx)

    def choose_won_card(self, ctx: StrategyContext) -> int:
        d = self._delegate(ctx)
        if d is None:
            idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
            return idx
        return d.choose_won_card(ctx)


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
            utility = (self.market_weight * market) - (self.damage_weight * (damage / 5000.0))
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
        aggression_mult = 1.0 + ((_avg_opp_aggression(ctx) - 0.2) * self.aggression_weight)
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
        ranked: list[tuple[float, int]] = []
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
        mult = _objective_multiplier(ctx.objective) * (1.0 + self.late_round_bonus * progress)
        target = fair * self.bid_scale * mult
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
        ranked: list[tuple[float, int]] = []
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


__all__ = [
    "ConservativePlusStrategy",
    "ElasticConservativeStrategy",
    "EquityAwareStrategy",
    "HouseHammerStrategy",
    "MarketMakerStrategy",
    "MonteCarloEdgeStrategy",
    "ProbabilisticValueStrategy",
    "RegimeSwitchStrategy",
    "RiskManagedSniperStrategy",
    "SellerExtractionStrategy",
    "V4MetaSwitchStrategy",
]
