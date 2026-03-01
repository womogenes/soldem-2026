from __future__ import annotations

import copy
import random
import time
from itertools import product
from typing import Any

from game.rules import BASELINE_PROFILE, RuleProfile, resolve_profile
from game.utils import classify_hand

N_PLAYERS = BASELINE_PROFILE.n_players
N_PLAYER_CARDS = BASELINE_PROFILE.cards_per_player
BASE_DECK = list(product(range(1, 11), "CDHSX"))


class Game:
    def __init__(
        self,
        start_chips: int | None = None,
        ante_amt: int | None = None,
        n_orbits: int | None = None,
        rule_profile: RuleProfile | str | None = None,
    ):
        if isinstance(rule_profile, RuleProfile):
            profile = rule_profile
        else:
            profile = resolve_profile(rule_profile)

        overrides: dict[str, Any] = {}
        if start_chips is not None:
            overrides["start_chips"] = start_chips
        if ante_amt is not None:
            overrides["ante_amt"] = ante_amt
        if n_orbits is not None:
            overrides["n_orbits"] = n_orbits
        if overrides:
            profile = profile.with_overrides(**overrides)

        self.rules = profile
        self.start_chips = profile.start_chips
        self.ante_amt = profile.ante_amt
        self.n_orbits = profile.n_orbits

        self.player_stacks = [self.start_chips] * self.rules.n_players
        self.player_cards: list[list[tuple[int, str]]] = [
            [] for _ in range(self.rules.n_players)
        ]

        self.round_num: int | None = None
        self.seller_idx: int | None = None
        self.player_bids: list[tuple[int, float] | None] = [None] * self.rules.n_players

        self.auc_cards: list[tuple[int, str]] = []
        self.pot = 0
        self.last_winner_idx: int | None = None
        self.last_win_amt = 0
        self.turns_in_orbit = 0
        self._deck: list[tuple[int, str]] = []

    def state(self) -> dict[str, Any]:
        return {
            "game_over": False,
            "seller_idx": self.seller_idx,
            "round_num": self.round_num,
            "player_cards": copy.deepcopy(self.player_cards),
            "player_stacks": list(self.player_stacks),
            "pot": self.pot,
            "auc_cards": list(self.auc_cards),
            "rules": self.rules.to_dict(),
        }

    def reset(self, seed: int | None = None):
        rng = random.Random(seed)
        deck = list(BASE_DECK)
        rng.shuffle(deck)
        self._deck = list(deck)

        self.player_cards = [[] for _ in range(self.rules.n_players)]
        for i in range(self.rules.n_players):
            self.player_cards[i] = deck[: self.rules.cards_per_player]
            deck = deck[self.rules.cards_per_player :]

        self.player_stacks = [self.start_chips - self.ante_amt] * self.rules.n_players
        self.pot = self.ante_amt * self.rules.n_players

        self.auc_cards = [deck.pop(0)]
        self.player_bids = [None] * self.rules.n_players
        self.last_winner_idx = None
        self.last_win_amt = 0
        self.turns_in_orbit = 0

        self.round_num = 0
        self.seller_idx = -1
        return self.state()

    def eligible_bidders(self) -> list[int]:
        if self.seller_idx == -1:
            return list(range(self.rules.n_players))
        if self.rules.seller_can_bid_own_card:
            return list(range(self.rules.n_players))
        return [i for i in range(self.rules.n_players) if i != self.seller_idx]

    def prepare_auction(
        self,
        card_indices: list[int] | None = None,
        cards: list[tuple[int, str]] | None = None,
    ):
        if self.seller_idx is None:
            raise RuntimeError("Game has not started")
        if self.seller_idx < 0:
            return

        seller_cards = self.player_cards[self.seller_idx]
        if cards is not None:
            picks = [c for c in cards if c in seller_cards]
        elif card_indices:
            picks = [
                seller_cards[i]
                for i in sorted(set(card_indices))
                if 0 <= i < len(seller_cards)
            ]
        else:
            picks = list(seller_cards)

        if not picks:
            picks = [seller_cards[0]]

        if not self.rules.allow_multi_card_sell:
            picks = [picks[0]]

        self.auc_cards = picks

    def player_bid(self, player_idx: int, amt: int, bid_ts: float | None = None):
        if player_idx < 0 or player_idx >= self.rules.n_players:
            raise ValueError(f"Invalid player index {player_idx}")
        if player_idx not in self.eligible_bidders():
            raise ValueError(f"Player {player_idx} is not eligible to bid now")

        amt = max(0, min(self.player_stacks[player_idx], int(amt)))
        self.player_bids[player_idx] = (amt, time.time() if bid_ts is None else bid_ts)

    def close_bids(self):
        if not self.auc_cards:
            raise RuntimeError("No auction cards are set")

        bidders = self.eligible_bidders()
        now = time.time()
        valid: list[tuple[int, int, float]] = []
        for idx in bidders:
            bid = self.player_bids[idx]
            if bid is None:
                valid.append((idx, 0, now + (idx * 1e-6)))
            else:
                valid.append((idx, bid[0], bid[1]))

        winner_idx, amt, _ = max(valid, key=lambda x: (x[1], -x[2]))
        self.last_winner_idx = winner_idx
        self.last_win_amt = amt

        self.player_stacks[winner_idx] -= amt
        if self.seller_idx == -1:
            self.pot += amt
        else:
            self.player_stacks[self.seller_idx] += amt

        return {
            "winner": winner_idx,
            "bid_price": amt,
            "won_cards": list(self.auc_cards),
            "player_stacks": list(self.player_stacks),
        }

    def _split_amount(self, amount: int, winners: list[int]) -> dict[int, int]:
        if not winners:
            return {}
        base = amount // len(winners)
        rem = amount % len(winners)
        out = {w: base for w in winners}
        for w in winners[:rem]:
            out[w] += 1
        return out

    def _resolve_showdown(self) -> dict[str, Any]:
        ranks = [
            classify_hand(cards, policy=self.rules.hand_ranking_policy)
            for cards in self.player_cards
        ]

        payouts = [0] * self.rules.n_players
        if self.rules.pot_distribution_policy == "winner_takes_all":
            best = max(ranks)
            winners = [i for i, r in enumerate(ranks) if r == best]
            for idx, amt in self._split_amount(self.pot, winners).items():
                payouts[idx] += amt

        elif self.rules.pot_distribution_policy == "top2_split":
            ranked_unique = sorted(set(ranks), reverse=True)
            top_rank = ranked_unique[0]
            second_rank = ranked_unique[1] if len(ranked_unique) > 1 else ranked_unique[0]
            top_winners = [i for i, r in enumerate(ranks) if r == top_rank]
            second_winners = [i for i, r in enumerate(ranks) if r == second_rank]
            high_pot = self.pot // 2
            low_pot = self.pot - high_pot
            for idx, amt in self._split_amount(high_pot, top_winners).items():
                payouts[idx] += amt
            for idx, amt in self._split_amount(low_pot, second_winners).items():
                payouts[idx] += amt

        elif self.rules.pot_distribution_policy == "high_low_split":
            top_rank = max(ranks)
            low_rank = min(ranks)
            high_winners = [i for i, r in enumerate(ranks) if r == top_rank]
            low_winners = [i for i, r in enumerate(ranks) if r == low_rank]
            high_pot = self.pot // 2
            low_pot = self.pot - high_pot
            for idx, amt in self._split_amount(high_pot, high_winners).items():
                payouts[idx] += amt
            for idx, amt in self._split_amount(low_pot, low_winners).items():
                payouts[idx] += amt

        else:
            raise ValueError(f"Unknown pot policy: {self.rules.pot_distribution_policy}")

        for i, amt in enumerate(payouts):
            self.player_stacks[i] += amt

        self.pot = 0
        top_payout = max(payouts)
        winner_idxs = [i for i, amt in enumerate(payouts) if amt == top_payout]
        return {
            "game_over": True,
            "winner_idx": winner_idxs[0],
            "winner_idxs": winner_idxs,
            "payouts": payouts,
            "player_cards": copy.deepcopy(self.player_cards),
            "player_stacks": list(self.player_stacks),
            "pot": self.pot,
            "hand_ranks": ranks,
        }

    def win_card(self, card_choice: int | tuple[int, str] | None = None):
        if self.last_winner_idx is None:
            raise RuntimeError("close_bids must be called before win_card")

        if card_choice is None:
            chosen = self.auc_cards[0]
        elif isinstance(card_choice, int):
            chosen = self.auc_cards[card_choice]
        else:
            chosen = card_choice

        winner_idx = self.last_winner_idx
        self.player_cards[winner_idx].append(chosen)

        if self.seller_idx is not None and self.seller_idx >= 0:
            if chosen in self.player_cards[self.seller_idx]:
                self.player_cards[self.seller_idx].remove(chosen)

        if self.seller_idx == -1:
            self.seller_idx = winner_idx
        else:
            self.turns_in_orbit += 1
            if self.turns_in_orbit >= self.rules.n_players:
                self.round_num = (self.round_num or 0) + 1
                self.turns_in_orbit = 0
            self.seller_idx = (self.seller_idx + 1) % self.rules.n_players

        if self.round_num is not None and self.round_num >= self.n_orbits:
            return self._resolve_showdown()

        self.prepare_auction()
        self.player_bids = [None] * self.rules.n_players
        return self.state()
