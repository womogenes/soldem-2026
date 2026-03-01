from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass
class CorrelationModel:
    mode: str = "none"
    strength: float = 0.0
    pairs: list[tuple[int, int]] = field(default_factory=list)

    def normalized_pairs(self) -> set[tuple[int, int]]:
        return {tuple(sorted(p)) for p in self.pairs}


def _in_pair(a: int, b: int, pairs: set[tuple[int, int]]) -> bool:
    return tuple(sorted((a, b))) in pairs


def adjust_bid(
    seat: int,
    seller: int,
    raw_bid: int,
    bids: dict[int, int],
    stacks: list[int],
    model: CorrelationModel,
    rng: random.Random,
) -> int:
    if model.mode == "none" or model.strength <= 0:
        return max(0, min(stacks[seat], raw_bid))

    pairs = model.normalized_pairs()
    out = float(raw_bid)

    if model.mode == "respect":
        # Players in a pair bid less against each other, increasing coordination risk.
        if seller >= 0 and _in_pair(seat, seller, pairs):
            out *= max(0.0, 1.0 - model.strength)

    elif model.mode == "herd":
        # Paired players tend to move together and follow partner bid direction.
        for a, b in pairs:
            if seat == a and b in bids:
                out = (1.0 - model.strength) * out + model.strength * bids[b]
            elif seat == b and a in bids:
                out = (1.0 - model.strength) * out + model.strength * bids[a]
        out += rng.uniform(-1, 1) * model.strength

    elif model.mode == "kingmaker":
        # Paired players support partner's selling turn by suppressing own bids.
        if seller >= 0 and _in_pair(seat, seller, pairs):
            out *= max(0.0, 1.0 - (model.strength * 1.25))

    return max(0, min(stacks[seat], int(out)))
