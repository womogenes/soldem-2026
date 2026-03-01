from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product

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
    if idx < 0 or idx >= len(cards):
        return 0
    if len(cards) <= 1:
        return 0
    before = _hand_score(cards, policy)
    after_cards = [c for i, c in enumerate(cards) if i != idx]
    after = _hand_score(after_cards, policy)
    return max(0, before - after)


def _least_costly_sales(
    cards: list[Card],
    policy: str,
    count: int = 1,
    prefer_high_value: bool = False,
) -> list[int]:
    rows = []
    for idx, card in enumerate(cards):
        loss = _hold_loss(cards, idx, policy)
        value = card[0]
        tie_value = -value if prefer_high_value else value
        rows.append((loss, tie_value, card[1], idx))
    rows.sort()
    return [idx for *_rest, idx in rows[: max(1, min(count, len(cards)))]]


def _avg_opp_aggression(ctx: StrategyContext) -> float:
    total = 0.0
    n = 0
    for seat, profile in ctx.player_profiles.items():
        if seat == ctx.seat:
            continue
        total += profile.aggression
        n += 1
    return (total / n) if n else 0.0


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
    if len(deck) < (n_players - 1) * 5:
        return 0.0

    my_key = classify_hand(my_cards, policy=policy)
    wins = 0.0
    need = (n_players - 1) * 5
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

        avg_aggr = _avg_opp_aggression(ctx)
        pressure = max(0.7, min(1.25, 1.0 - (avg_aggr - 0.2)))
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

        best_idx, score_delta = _best_delta(
            ctx.my_cards,
            ctx.auction_cards,
            ctx.ranking_policy,
        )
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
        with_card = ctx.my_cards + [ctx.auction_cards[best_idx]]
        p_with = _equity_vs_random(
            with_card,
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

        avg_aggr = _avg_opp_aggression(ctx)
        if avg_aggr > 0.45:
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
        # Early offers include two cards, but avoid giving away structurally key cards.
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

        best_idx, score_delta = _best_delta(
            ctx.my_cards,
            ctx.auction_cards,
            ctx.ranking_policy,
        )
        if score_delta <= 0:
            return 0

        avg_stack = sum(ctx.stacks) / len(ctx.stacks)
        avg_aggr = _avg_opp_aggression(ctx)
        stack_ratio = my_stack / max(1.0, avg_stack)

        # Regime selection: chase upside when behind/first-place objective, tighten if table is hot.
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

        # Small deterministic jitter to reduce exploitability from pure determinism.
        rng = random.Random(base_seed + 101)
        jitter_mult = 1.0 + rng.uniform(-self.jitter, self.jitter)

        target = min(fair, cap) * jitter_mult
        if delta_p < 0.012 and score_delta < 900:
            return 0
        return max(0, min(my_stack, int(target)))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


def built_in_strategy_factories() -> dict[str, callable]:
    return {
        "random": lambda: RandomStrategy(),
        "pot_fraction": lambda: PotFractionStrategy(0.25),
        "delta_value": lambda: DeltaValueStrategy(multiplier=1.0),
        "conservative": lambda: ConservativeStrategy(),
        "conservative_plus": lambda: ElasticConservativeStrategy(
            max_pot_frac=0.16,
            delta_scale=8200.0,
            sell_count_early=2,
            house_discount=0.58,
            tag="conservative_plus",
        ),
        "conservative_ultra": lambda: ElasticConservativeStrategy(
            max_pot_frac=0.12,
            delta_scale=9800.0,
            sell_count_early=2,
            house_discount=0.50,
            tag="conservative_ultra",
        ),
        "elastic_conservative": lambda: ElasticConservativeStrategy(),
        "bully": lambda: BullyStrategy(),
        "seller_profit": lambda: SellerProfitStrategy(),
        "adaptive_profile": lambda: AdaptiveProfileStrategy(),
        "market_maker": lambda: MarketMakerStrategy(),
        "market_maker_v2": lambda: MarketMakerStrategy(
            reserve_frac=0.09,
            tag="market_maker_v2",
        ),
        "market_maker_tight": lambda: MarketMakerStrategy(
            reserve_frac=0.095,
            tag="market_maker_tight",
        ),
        "market_maker_aggr": lambda: MarketMakerStrategy(
            reserve_frac=0.13,
            tag="market_maker_aggr",
        ),
        "regime_switch": lambda: RegimeSwitchStrategy(),
        "regime_switch_v2": lambda: RegimeSwitchStrategy(
            reserve_base=0.105,
            reserve_min=0.070,
            reserve_max=0.165,
            eq_samples=16,
            jitter=0.05,
            tag="regime_switch_v2",
        ),
        "regime_switch_robust": lambda: RegimeSwitchStrategy(
            reserve_base=0.105,
            reserve_min=0.07,
            reserve_max=0.155,
            eq_samples=12,
            jitter=0.08,
            tag="regime_switch_robust",
        ),
        "mc_edge": lambda: MonteCarloEdgeStrategy(),
    }


def build_strategy(tag: str):
    factories = built_in_strategy_factories()
    if tag not in factories:
        raise KeyError(f"Unknown strategy tag: {tag}")
    return factories[tag]()
