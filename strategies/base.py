from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

Card = tuple[int, str]


@dataclass
class PlayerProfile:
    seat: int
    avg_bid: float = 0.0
    bid_count: int = 0
    aggression: float = 0.0


@dataclass
class StrategyContext:
    seat: int
    seller_idx: int
    pot: int
    round_num: int
    n_orbits: int
    stacks: list[int]
    my_cards: list[Card]
    auction_cards: list[Card]
    ranking_policy: str
    objective: str = "ev"
    player_profiles: dict[int, PlayerProfile] = field(default_factory=dict)


class Strategy(Protocol):
    tag: str

    def on_round_start(self, ctx: StrategyContext) -> None:
        ...

    def choose_sell_indices(self, ctx: StrategyContext) -> list[int]:
        ...

    def bid_amount(self, ctx: StrategyContext) -> int:
        ...

    def choose_won_card(self, ctx: StrategyContext) -> int:
        ...
