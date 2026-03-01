from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from game.utils import classify_hand
from strategies.base import Card, StrategyContext
from strategies.cross_branch import (
    ConservativePlusStrategy,
    ElasticConservativeStrategy,
    EquityAwareStrategy,
    HouseHammerStrategy,
    MarketMakerStrategy,
    MonteCarloEdgeStrategy,
    ProbabilisticValueStrategy,
    RegimeSwitchStrategy,
    RiskManagedSniperStrategy,
    SellerExtractionStrategy,
    V4MetaSwitchStrategy,
)


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


def _estimate_fair_bid(ctx: StrategyContext, value_scale: float = 5000.0) -> int:
    _, delta = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
    return max(0, int((delta / value_scale) * max(0, ctx.pot)))


def _avg_opponent_bid(ctx: StrategyContext, fallback: int) -> int:
    vals = [
        int(p.avg_bid)
        for seat, p in ctx.player_profiles.items()
        if seat != ctx.seat and p.bid_count > 0
    ]
    if vals:
        return max(0, int(sum(vals) / len(vals)))
    return max(0, fallback)


def _profile_for_seat(ctx: StrategyContext, seat: int):
    return ctx.player_profiles.get(seat)


def _bid_grid(stack: int, pot: int, fair_bid: int) -> list[int]:
    pts = [
        0,
        int(pot * 0.08),
        int(pot * 0.15),
        int(pot * 0.25),
        fair_bid,
        int(fair_bid * 1.25),
        int(pot * 0.45),
        int(stack * 0.5),
        stack,
    ]
    return sorted({max(0, min(stack, p)) for p in pts})


def _p_win(bid: int, opp_ref: int, n_opp: int, noise: float = 18.0) -> float:
    z = (bid - opp_ref) / max(1.0, noise)
    z = max(-50.0, min(50.0, z))
    p_single = 1.0 / (1.0 + math.exp(-z))
    p = p_single**max(1, n_opp)
    return max(0.01, min(0.99, p))


def _expected_bid_utility(bid: int, fair_bid: int, opp_ref: int, n_opp: int, noise: float) -> float:
    p = _p_win(bid, opp_ref, n_opp, noise=noise)
    return p * (fair_bid - bid)


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
        return _weakest_indices(ctx.my_cards, 2)

    def bid_amount(self, ctx: StrategyContext) -> int:
        max_bid = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
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
        fair = _estimate_fair_bid(ctx, value_scale=7000.0)
        target = int(min(ctx.pot * 0.15, fair))
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

        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        delta_term = max(0.0, min(0.3, fair / max(1, ctx.pot)))
        target = int(ctx.pot * (frac + delta_term))
        return max(0, min(my_stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class LevelKStrategy:
    """Cognitive hierarchy / level-k approximation for first-price bidding."""

    level: int = 2
    l0_fraction: float = 0.28
    tag: str = "level_k"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        opp_count = len(ctx.stacks) - 1

        l0_ref = int(ctx.pot * self.l0_fraction)
        prof_ref = _avg_opponent_bid(ctx, fallback=l0_ref)

        if self.level <= 0:
            opp_ref = l0_ref
            noise = 30.0
        elif self.level == 1:
            opp_ref = int((l0_ref + prof_ref) / 2)
            noise = 22.0
        else:
            # Level-2 best-responds to opponents that themselves overbid with L1 shading.
            opp_ref = int((0.65 * prof_ref) + (0.35 * fair))
            noise = 16.0

        best_bid = 0
        best_u = -10**18
        for bid in _bid_grid(stack, ctx.pot, fair):
            u = _expected_bid_utility(bid, fair, opp_ref, opp_count, noise)
            if u > best_u:
                best_u = u
                best_bid = bid
        return best_bid

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class QuantalResponseStrategy:
    """McKelvey-Palfrey style quantal response on discrete bid grid."""

    lam: float = 0.06
    seed: int = 17
    tag: str = "quantal_response"

    def __post_init__(self):
        self.rng = random.Random(self.seed)

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        opp_ref = _avg_opponent_bid(ctx, fallback=int(ctx.pot * 0.25))
        opp_count = len(ctx.stacks) - 1

        bids = _bid_grid(stack, ctx.pot, fair)
        utils = [
            _expected_bid_utility(b, fair, opp_ref, opp_count, noise=18.0)
            for b in bids
        ]
        max_u = max(utils) if utils else 0.0
        exps = [math.exp(self.lam * (u - max_u)) for u in utils]
        total = sum(exps) or 1.0
        probs = [x / total for x in exps]

        draw = self.rng.random()
        acc = 0.0
        for bid, p in zip(bids, probs):
            acc += p
            if draw <= acc:
                return bid
        return bids[-1] if bids else 0

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class EWAAttractionStrategy:
    """Experience-weighted attraction approximation over bid multipliers."""

    phi: float = 0.1
    delta: float = 0.8
    lam: float = 0.08
    seed: int = 29
    tag: str = "ewa_attraction"
    multipliers: list[float] = field(default_factory=lambda: [0.08, 0.16, 0.28, 0.4, 0.6])

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.attractions = [0.0 for _ in self.multipliers]
        self.experience = 1.0

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        opp_ref = _avg_opponent_bid(ctx, fallback=int(ctx.pot * 0.25))
        opp_count = len(ctx.stacks) - 1

        bids = [max(0, min(stack, int(ctx.pot * m))) for m in self.multipliers]
        payoffs = [
            _expected_bid_utility(b, fair, opp_ref, opp_count, noise=20.0)
            for b in bids
        ]

        self.experience = (1 - self.phi) * self.experience + 1.0
        for i in range(len(self.attractions)):
            self.attractions[i] = (
                ((1 - self.phi) * self.experience * self.attractions[i])
                + (self.delta * payoffs[i])
            ) / max(1e-9, self.experience)

        max_a = max(self.attractions) if self.attractions else 0.0
        exps = [math.exp(self.lam * (a - max_a)) for a in self.attractions]
        total = sum(exps) or 1.0
        probs = [x / total for x in exps]

        draw = self.rng.random()
        acc = 0.0
        for bid, p in zip(bids, probs):
            acc += p
            if draw <= acc:
                return bid
        return bids[-1] if bids else 0

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class SafeExploitStrategy:
    """Safe exploitation blend inspired by nested subgame safe solving."""

    exploit_weight: float = 0.65
    tag: str = "safe_exploit"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        # Keep strongest cards and expose weaker assets unless opponents are very passive.
        avg_aggr = 0.0
        n = 0
        for seat, profile in ctx.player_profiles.items():
            if seat == ctx.seat:
                continue
            avg_aggr += profile.aggression
            n += 1
        avg_aggr = avg_aggr / n if n else 0.0
        if avg_aggr < 0.18:
            return _weakest_indices(ctx.my_cards, 2)
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)

        conservative = int(min(ctx.pot * 0.14, fair * 0.7))
        exploit = int(min(stack, max(fair, ctx.pot * 0.30)))

        w = self.exploit_weight
        if ctx.objective == "robustness":
            w = 0.35
        elif ctx.objective == "first_place":
            w = 0.8

        target = int((w * exploit) + ((1 - w) * conservative))
        return max(0, min(stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class MetaSwitchStrategy:
    """Policy-switching strategy that routes to robust/aggressive sub-policies."""

    aggro_threshold: float = 0.20
    tag: str = "meta_switch"
    _cons: ConservativeStrategy = field(default_factory=ConservativeStrategy)
    _lk: LevelKStrategy = field(default_factory=LevelKStrategy)
    _pot: PotFractionStrategy = field(default_factory=lambda: PotFractionStrategy(0.28))

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def _avg_opp_aggr(self, ctx: StrategyContext) -> float:
        vals = [
            p.aggression
            for seat, p in ctx.player_profiles.items()
            if seat != ctx.seat and p.bid_count > 0
        ]
        return (sum(vals) / len(vals)) if vals else 0.22

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        avg_aggr = self._avg_opp_aggr(ctx)
        my_stack = ctx.stacks[ctx.seat]
        avg_stack = sum(ctx.stacks) / len(ctx.stacks)

        if ctx.objective == "robustness":
            return self._cons.bid_amount(ctx)

        if avg_aggr >= (self.aggro_threshold + 0.10):
            return self._cons.bid_amount(ctx)

        # If we are behind in chips in a softer table, increase pressure.
        if my_stack < (0.92 * avg_stack) and avg_aggr <= self.aggro_threshold:
            return self._pot.bid_amount(ctx)

        return self._lk.bid_amount(ctx)

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class WinnersCurseAwareStrategy:
    """Kagel-Levin style bid shading under common-value uncertainty."""

    base_shade: float = 0.62
    tag: str = "winners_curse_aware"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        if fair <= 0:
            return 0

        deltas = []
        base = _hand_score(ctx.my_cards, ctx.ranking_policy)
        for card in ctx.auction_cards:
            deltas.append(_hand_score(ctx.my_cards + [card], ctx.ranking_policy) - base)
        if deltas:
            hi = max(deltas)
            lo = min(deltas)
            spread_ratio = (hi - lo) / max(1, abs(hi))
        else:
            spread_ratio = 0.0

        avg_opp_aggr = 0.22
        vals = [
            p.aggression
            for s, p in ctx.player_profiles.items()
            if s != ctx.seat and p.bid_count > 0
        ]
        if vals:
            avg_opp_aggr = sum(vals) / len(vals)

        # More uncertainty + higher aggression => stronger shading.
        shade = self.base_shade
        shade -= min(0.22, spread_ratio * 0.22)
        shade -= min(0.15, max(0.0, avg_opp_aggr - 0.2))
        if ctx.objective == "first_place":
            shade += 0.08
        elif ctx.objective == "robustness":
            shade -= 0.08

        target = int(fair * max(0.20, min(0.95, shade)))
        target = min(target, int(max(0, ctx.pot) * 0.40))
        return max(0, min(stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class ReciprocityProbeStrategy:
    """Reciprocity-aware bidding that adjusts by seller interaction profile."""

    tag: str = "reciprocity_probe"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        # Offer weaker pair to attract bids while preserving best hand core.
        return _weakest_indices(ctx.my_cards, 2)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5200.0)
        mkt = _avg_opponent_bid(ctx, fallback=int(ctx.pot * 0.24))
        seller = ctx.seller_idx
        seller_prof = _profile_for_seat(ctx, seller)

        adj = 1.0
        if seller_prof is not None and seller_prof.sell_count > 0:
            # If seller extracts high prices repeatedly, assume tougher dynamic.
            if seller_prof.avg_sell_price > (ctx.pot * 0.30):
                adj -= 0.18
            elif seller_prof.avg_sell_price < (ctx.pot * 0.18):
                adj += 0.10

        if ctx.objective == "robustness":
            adj -= 0.10
        elif ctx.objective == "first_place":
            adj += 0.08

        target = int((0.65 * fair + 0.35 * mkt) * max(0.35, min(1.2, adj)))
        return max(0, min(stack, target))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        idx, _ = _best_delta(ctx.my_cards, ctx.auction_cards, ctx.ranking_policy)
        return idx


@dataclass
class HorizonPushStrategy:
    """Short-horizon match strategy with late-stage aggression ramps."""

    base_frac: float = 0.18
    late_frac: float = 0.34
    tag: str = "horizon_push"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        stage = (ctx.match_game_index + 1) / max(1, ctx.match_n_games)
        if stage > 0.7 and ctx.objective == "first_place":
            return _weakest_indices(ctx.my_cards, 2)
        return _weakest_indices(ctx.my_cards, 1)

    def bid_amount(self, ctx: StrategyContext) -> int:
        stack = ctx.stacks[ctx.seat]
        fair = _estimate_fair_bid(ctx, value_scale=5000.0)
        stage = (ctx.match_game_index + 1) / max(1, ctx.match_n_games)

        frac = self.base_frac + ((self.late_frac - self.base_frac) * stage)
        if ctx.objective == "robustness":
            frac *= 0.8
        elif ctx.objective == "first_place":
            frac *= 1.15

        target = int(max(fair * 0.6, ctx.pot * frac))
        return max(0, min(stack, target))

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
        "level_k": lambda: LevelKStrategy(),
        "level_k_l1": lambda: LevelKStrategy(level=1, l0_fraction=0.30, tag="level_k_l1"),
        "level_k_l3": lambda: LevelKStrategy(level=3, l0_fraction=0.24, tag="level_k_l3"),
        "quantal_response": lambda: QuantalResponseStrategy(),
        "quantal_cold": lambda: QuantalResponseStrategy(lam=0.12, seed=19, tag="quantal_cold"),
        "quantal_hot": lambda: QuantalResponseStrategy(lam=0.03, seed=23, tag="quantal_hot"),
        "ewa_attraction": lambda: EWAAttractionStrategy(),
        "ewa_slow": lambda: EWAAttractionStrategy(phi=0.05, delta=0.9, lam=0.06, seed=31, tag="ewa_slow"),
        "ewa_fast": lambda: EWAAttractionStrategy(phi=0.2, delta=0.6, lam=0.10, seed=37, tag="ewa_fast"),
        "safe_exploit": lambda: SafeExploitStrategy(),
        "safe_exploit_robust": lambda: SafeExploitStrategy(exploit_weight=0.45, tag="safe_exploit_robust"),
        "safe_exploit_aggro": lambda: SafeExploitStrategy(exploit_weight=0.78, tag="safe_exploit_aggro"),
        "meta_switch": lambda: MetaSwitchStrategy(),
        "meta_switch_soft": lambda: MetaSwitchStrategy(aggro_threshold=0.15, tag="meta_switch_soft"),
        "winners_curse_aware": lambda: WinnersCurseAwareStrategy(),
        "reciprocity_probe": lambda: ReciprocityProbeStrategy(),
        "horizon_push": lambda: HorizonPushStrategy(),
        "horizon_push_late": lambda: HorizonPushStrategy(base_frac=0.16, late_frac=0.40, tag="horizon_push_late"),
        # Cross-branch imports from v3/v4/v5.
        "elastic_conservative": lambda: ElasticConservativeStrategy(),
        "conservative_plus": lambda: ConservativePlusStrategy(),
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
        "mc_edge": lambda: MonteCarloEdgeStrategy(),
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
        "equity_evolved_v1": lambda: EquityAwareStrategy(
            bid_multiplier=0.984,
            delta_scale=6057.7,
            min_delta=781,
            max_stack_frac=0.265,
            max_pot_frac=0.106,
            house_multiplier=1.303,
            preserve_weight=1.245,
            sell_count_early=2,
            sell_count_late=1,
            tag="equity_evolved_v1",
        ),
        "house_hammer": lambda: HouseHammerStrategy(),
        "meta_switch_v4": lambda: V4MetaSwitchStrategy(),
        "prob_value": lambda: ProbabilisticValueStrategy(),
        "risk_sniper": lambda: RiskManagedSniperStrategy(),
        "seller_extraction": lambda: SellerExtractionStrategy(),
    }


def build_strategy(tag: str, overrides: dict | None = None):
    factories = built_in_strategy_factories()
    if tag not in factories:
        raise KeyError(f"Unknown strategy tag: {tag}")
    strategy = factories[tag]()
    if overrides:
        for key, value in overrides.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
    return strategy
