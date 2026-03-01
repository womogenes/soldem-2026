"""Rule profiles for Sold 'Em.

RULES.md is the source of truth. This module captures a canonical baseline and
explicit toggles for variant handling.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Literal

HandRankingPolicy = Literal["rarity_50", "standard_plus_five_kind"]
PotDistributionPolicy = Literal["winner_takes_all", "top2_split", "high_low_split"]


@dataclass(frozen=True)
class RuleProfile:
    name: str = "baseline_v1"
    n_players: int = 5
    cards_per_player: int = 5
    start_chips: int = 200
    ante_amt: int = 40
    n_orbits: int = 3
    allow_multi_card_sell: bool = True
    seller_can_bid_own_card: bool = False
    tie_break_first_bid_wins: bool = True
    hand_ranking_policy: HandRankingPolicy = "rarity_50"
    pot_distribution_policy: PotDistributionPolicy = "winner_takes_all"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_overrides(self, **overrides: Any) -> "RuleProfile":
        return replace(self, **overrides)


BASELINE_PROFILE = RuleProfile()


def built_in_profiles() -> dict[str, RuleProfile]:
    base = BASELINE_PROFILE
    return {
        base.name: base,
        "standard_rankings": base.with_overrides(
            name="standard_rankings",
            hand_ranking_policy="standard_plus_five_kind",
        ),
        "seller_self_bid": base.with_overrides(
            name="seller_self_bid",
            seller_can_bid_own_card=True,
        ),
        "top2_split": base.with_overrides(
            name="top2_split",
            pot_distribution_policy="top2_split",
        ),
        "high_low_split": base.with_overrides(
            name="high_low_split",
            pot_distribution_policy="high_low_split",
        ),
        "single_card_sell": base.with_overrides(
            name="single_card_sell",
            allow_multi_card_sell=False,
        ),
    }


def resolve_profile(name: str | None = None, **overrides: Any) -> RuleProfile:
    catalog = built_in_profiles()
    profile = catalog.get(name or BASELINE_PROFILE.name, BASELINE_PROFILE)
    if overrides:
        profile = profile.with_overrides(**overrides)
    return profile
