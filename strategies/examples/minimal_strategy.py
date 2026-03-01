"""Example external strategy file.

Usage:
python scripts/run_match.py strategies/examples/minimal_strategy.py random pot_fraction delta_value conservative --n-games 20
"""

from __future__ import annotations

from strategies.base import StrategyContext


class Strategy:
    tag = "minimal_external"

    def on_round_start(self, ctx: StrategyContext) -> None:
        return None

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        return [0]

    def bid_amount(self, ctx: StrategyContext) -> int:
        return min(ctx.stacks[ctx.seat], int(ctx.pot * 0.2))

    def choose_won_card(self, ctx: StrategyContext) -> int:
        return 0


def build() -> Strategy:
    return Strategy()
