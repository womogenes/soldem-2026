from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product

from game.utils import classify_hand
from strategies import PlayerProfile, StrategyContext
from strategies.loader import load_strategy

Card = tuple[int, str]
BASE_DECK = list(product(range(1, 11), "CDHSX"))


@dataclass
class Recommendation:
    phase: str
    strategy_tag: str
    primary_action: dict
    top_actions: list[dict]
    metrics: dict
    rationale: str

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "strategy_tag": self.strategy_tag,
            "primary_action": self.primary_action,
            "top_actions": self.top_actions,
            "metrics": self.metrics,
            "rationale": self.rationale,
        }


def _score_key(cards: list[Card], policy: str) -> int:
    key = classify_hand(cards, policy=policy)
    score = 0
    for part in key:
        score = (score * 20) + max(0, int(part))
    return score


def _best_delta_card(my_cards: list[Card], auction_cards: list[Card], policy: str) -> tuple[int, int]:
    if not auction_cards:
        return 0, 0
    base = _score_key(my_cards, policy)
    best_idx = 0
    best_delta = -10**9
    for i, card in enumerate(auction_cards):
        score = _score_key(my_cards + [card], policy)
        delta = score - base
        if delta > best_delta:
            best_delta = delta
            best_idx = i
    return best_idx, best_delta


def _dedupe_cards(cards: list[Card]) -> list[Card]:
    out: list[Card] = []
    seen: set[Card] = set()
    for card in cards:
        if card in seen:
            continue
        seen.add(card)
        out.append(card)
    return out


def _normalize_known_cards_by_seat(
    *,
    known_cards_by_seat: dict[int, list[Card]] | None,
    my_cards: list[Card],
    n_players: int,
) -> dict[int, list[Card]]:
    known_cards_by_seat = known_cards_by_seat or {}
    blocked = set(_dedupe_cards(my_cards))
    out: dict[int, list[Card]] = {i: [] for i in range(n_players)}
    for seat, cards in known_cards_by_seat.items():
        if seat < 0 or seat >= n_players:
            continue
        fixed: list[Card] = []
        for card in cards:
            if card in blocked:
                continue
            blocked.add(card)
            fixed.append(card)
            if len(fixed) >= 5:
                break
        out[seat] = fixed
    return out


def _flatten_known_by_seat(known_cards_by_seat: dict[int, list[Card]]) -> list[Card]:
    all_cards: list[Card] = []
    for cards in known_cards_by_seat.values():
        all_cards.extend(cards)
    return _dedupe_cards(all_cards)


def _estimate_showdown_win_prob(
    my_cards: list[Card],
    known_cards: list[Card],
    n_players: int,
    policy: str,
    samples: int = 300,
    seed: int = 0,
) -> float:
    rng = random.Random(seed)
    deck = [c for c in BASE_DECK if c not in known_cards and c not in my_cards]
    if len(my_cards) < 5:
        return 0.0

    my_key = classify_hand(my_cards, policy=policy)
    wins = 0.0
    for _ in range(samples):
        rng.shuffle(deck)
        ptr = 0
        opp_keys = []
        for _opp in range(n_players - 1):
            opp_cards = deck[ptr : ptr + 5]
            ptr += 5
            opp_keys.append(classify_hand(opp_cards, policy=policy))

        all_keys = [my_key] + opp_keys
        best = max(all_keys)
        winners = [i for i, key in enumerate(all_keys) if key == best]
        if 0 in winners:
            wins += 1.0 / len(winners)
    return wins / samples


def _estimate_showdown_win_prob_conditioned(
    *,
    my_cards: list[Card],
    my_seat: int,
    known_cards: list[Card],
    known_cards_by_seat: dict[int, list[Card]],
    n_players: int,
    policy: str,
    samples: int = 220,
    seed: int = 0,
) -> float:
    if len(my_cards) < 5:
        return 0.0

    normalized = _normalize_known_cards_by_seat(
        known_cards_by_seat=known_cards_by_seat,
        my_cards=my_cards,
        n_players=n_players,
    )
    dead = set(_dedupe_cards(my_cards + known_cards + _flatten_known_by_seat(normalized)))
    deck = [c for c in BASE_DECK if c not in dead]
    if not deck:
        return 0.0

    rng = random.Random(seed)
    my_key = classify_hand(my_cards, policy=policy)
    wins = 0.0
    for _ in range(samples):
        rng.shuffle(deck)
        ptr = 0
        all_keys = [my_key]
        for opp_seat in range(n_players):
            if opp_seat == my_seat:
                continue
            fixed = list(normalized.get(opp_seat, []))
            need = max(0, 5 - len(fixed))
            draw = deck[ptr : ptr + need]
            ptr += need
            cards = fixed + draw
            if len(cards) < 5:
                continue
            all_keys.append(classify_hand(cards, policy=policy))
        best = max(all_keys)
        winners = [i for i, key in enumerate(all_keys) if key == best]
        if 0 in winners:
            wins += 1.0 / len(winners)
    return wins / max(1, samples)


def _objective_multiplier(objective: str) -> float:
    if objective == "first_place":
        return 1.2
    if objective == "robustness":
        return 0.8
    return 1.0


def _candidate_bids(stack: int, fair_bid: int) -> list[int]:
    pts = [0, int(fair_bid * 0.6), fair_bid, int(fair_bid * 1.25), int(stack * 0.5)]
    out = sorted({max(0, min(stack, p)) for p in pts})
    if not out:
        return [0]
    return out


def _opponent_card_pressure(known_cards_by_seat: dict[int, list[Card]], seat: int) -> float:
    pressure = 0.0
    for opp_seat, cards in known_cards_by_seat.items():
        if opp_seat == seat:
            continue
        high = sum(1 for v, _s in cards if v >= 8)
        pressure += (0.05 * high) + (0.03 * max(0, len(cards) - 1))
    return max(0.0, min(0.45, pressure))


def _estimate_bid_win_prob(
    bid: int,
    stacks: list[int],
    profiles: dict[int, PlayerProfile],
    seat: int,
    known_pressure: float = 0.0,
) -> float:
    table_scale = max(1.0, (sum(stacks) / len(stacks)) * 0.35)
    base = min(0.95, max(0.02, bid / table_scale))
    opp_aggr = [p.aggression for s, p in profiles.items() if s != seat]
    if opp_aggr:
        base *= max(0.65, min(1.35, 1.0 - (sum(opp_aggr) / len(opp_aggr) - 0.2)))
    base *= max(0.55, min(1.0, 1.0 - known_pressure))
    return max(0.01, min(0.99, base))


def recommend_action(
    *,
    phase: str,
    strategy_tag: str,
    seat: int,
    seller_idx: int,
    pot: int,
    stacks: list[int],
    my_cards: list[Card],
    auction_cards: list[Card],
    round_num: int,
    n_orbits: int,
    ranking_policy: str,
    objective: str,
    output_mode: str,
    player_profiles: dict[int, PlayerProfile],
    known_cards: list[Card] | None = None,
    known_cards_by_seat: dict[int, list[Card]] | None = None,
) -> Recommendation:
    known_cards_raw = _dedupe_cards(known_cards or [])
    known_cards_by_seat = _normalize_known_cards_by_seat(
        known_cards_by_seat=known_cards_by_seat or {},
        my_cards=my_cards,
        n_players=len(stacks),
    )
    known_cards = _dedupe_cards(known_cards_raw + _flatten_known_by_seat(known_cards_by_seat))
    strategy = load_strategy(strategy_tag)
    ctx = StrategyContext(
        seat=seat,
        seller_idx=seller_idx,
        pot=pot,
        round_num=round_num,
        n_orbits=n_orbits,
        stacks=stacks,
        my_cards=my_cards,
        auction_cards=auction_cards,
        ranking_policy=ranking_policy,
        objective=objective,
        player_profiles=player_profiles,
        known_cards=known_cards,
        known_cards_by_seat=known_cards_by_seat,
    )

    best_idx, delta = _best_delta_card(my_cards, auction_cards, ranking_policy)
    base_prob = _estimate_showdown_win_prob_conditioned(
        my_cards=my_cards,
        my_seat=seat,
        known_cards=known_cards,
        known_cards_by_seat=known_cards_by_seat,
        n_players=len(stacks),
        policy=ranking_policy,
        samples=220,
        seed=((round_num + 1) * 1337) + seat,
    )

    best_with_prob = base_prob
    for card in auction_cards:
        with_prob = _estimate_showdown_win_prob_conditioned(
            my_cards=my_cards + [card],
            my_seat=seat,
            known_cards=known_cards,
            known_cards_by_seat=known_cards_by_seat,
            n_players=len(stacks),
            policy=ranking_policy,
            samples=140,
            seed=((round_num + 1) * 2111) + seat + (card[0] * 13),
        )
        if with_prob > best_with_prob:
            best_with_prob = with_prob

    delta_prob = max(0.0, best_with_prob - base_prob)
    score_edge = max(0.0, (delta / 5000.0) * pot)
    equity_edge = max(0.0, delta_prob * pot * 1.8)
    fair_bid = int(max(0.0, (0.58 * score_edge) + (0.92 * equity_edge)) * _objective_multiplier(objective))
    fair_bid = max(0, min(stacks[seat], fair_bid))
    known_pressure = _opponent_card_pressure(known_cards_by_seat, seat)

    mc_prob = base_prob

    top_actions: list[dict] = []
    primary_action: dict

    if phase == "sell":
        sell_indices = strategy.choose_sell_indices(ctx)
        primary_action = {"type": "sell", "indices": sell_indices}
        top_actions = [{"type": "sell", "indices": sell_indices, "score": delta}]

    elif phase == "choose":
        primary_action = {"type": "choose", "index": best_idx}
        top_actions = [{"type": "choose", "index": best_idx, "score": delta}]

    elif phase == "bid":
        bids = _candidate_bids(stacks[seat], fair_bid)
        scored = []
        for bid in bids:
            p_win = _estimate_bid_win_prob(
                bid,
                stacks,
                player_profiles,
                seat,
                known_pressure=known_pressure,
            )
            ev = p_win * (max(score_edge, equity_edge) - bid)
            scored.append({"type": "bid", "amount": bid, "score": ev, "p_win": p_win})
        scored.sort(key=lambda row: row["score"], reverse=True)
        top_actions = scored[:3]
        if output_mode == "metrics":
            bid = strategy.bid_amount(ctx)
            primary_action = {"type": "bid", "amount": max(0, min(stacks[seat], bid))}
        else:
            primary_action = {"type": "bid", "amount": top_actions[0]["amount"] if top_actions else 0}

    else:
        primary_action = {"type": "hold"}
        top_actions = [{"type": "hold", "score": 0.0}]

    rationale = (
        f"Best-card delta={delta}, fair_bid={fair_bid}, "
        f"showdown_win_prob~{mc_prob:.3f}, delta_prob~{delta_prob:.3f}, "
        f"known_cards={len(known_cards)} under {objective} objective"
    )

    metrics = {
        "delta_score": delta,
        "delta_prob": delta_prob,
        "fair_bid": fair_bid,
        "showdown_win_prob": mc_prob,
        "known_cards_count": len(known_cards),
        "known_pressure": known_pressure,
        "mode": output_mode,
        "objective": objective,
    }
    return Recommendation(
        phase=phase,
        strategy_tag=strategy_tag,
        primary_action=primary_action,
        top_actions=top_actions,
        metrics=metrics,
        rationale=rationale,
    )
