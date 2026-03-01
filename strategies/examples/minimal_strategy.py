from __future__ import annotations

from game.utils import classify_hand
from strategies.base import StrategyContext


class Strategy:
    tag = "minimal_example"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        if not ctx.my_cards:
            return [0]
        ranked = sorted(enumerate(ctx.my_cards), key=lambda kv: (kv[1][0], kv[1][1]))
        return [ranked[0][0]]

    def bid_amount(self, ctx: StrategyContext) -> int:
        # Minimal fair-value proxy from one-card hand-strength delta.
        if not ctx.auction_cards:
            return 0
        base = classify_hand(ctx.my_cards, policy=ctx.ranking_policy)
        best_delta = 0
        for card in ctx.auction_cards:
            nxt = classify_hand(ctx.my_cards + [card], policy=ctx.ranking_policy)
            best_delta = max(best_delta, 1 if nxt > base else 0)
        if best_delta <= 0:
            return 0
        return min(ctx.stacks[ctx.seat], int(ctx.pot * 0.1))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        if not ctx.auction_cards:
            return 0
        best_i = 0
        best_key = classify_hand(ctx.my_cards + [ctx.auction_cards[0]], policy=ctx.ranking_policy)
        for i, card in enumerate(ctx.auction_cards[1:], start=1):
            key = classify_hand(ctx.my_cards + [card], policy=ctx.ranking_policy)
            if key > best_key:
                best_key = key
                best_i = i
        return best_i
