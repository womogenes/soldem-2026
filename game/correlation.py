from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class PairCorr:
    pair: tuple[int, int]
    corr: float
    samples: int


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 3:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-9 or vy <= 1e-9:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return max(-1.0, min(1.0, cov / sqrt(vx * vy)))


def _extract_auctions(events: list[dict[str, Any]], n_players: int) -> list[dict[int, float]]:
    auctions: list[dict[int, float]] = []
    current: dict[int, float] = {}
    for ev in events:
        et = ev.get("event_type")
        if et == "bid":
            seat = ev.get("seat")
            amt = ev.get("amount")
            if isinstance(seat, int) and 0 <= seat < n_players and isinstance(amt, (int, float)):
                current[seat] = float(amt)
        elif et == "auction_result":
            if len(current) >= 2:
                auctions.append(dict(current))
            current = {}
    if len(current) >= 2:
        auctions.append(dict(current))
    return auctions


def infer_correlation_mode(events: list[dict[str, Any]], n_players: int = 5) -> dict[str, Any]:
    auctions = _extract_auctions(events, n_players=n_players)
    if len(auctions) < 4:
        return {
            "mode": "none",
            "strength": 0.0,
            "confidence": 0.0,
            "n_auctions": len(auctions),
            "pairwise": [],
        }

    seat_series: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for idx, auc in enumerate(auctions):
        for seat, amt in auc.items():
            seat_series[seat].append((idx, amt))

    pairwise: list[PairCorr] = []
    for i in range(n_players):
        for j in range(i + 1, n_players):
            map_i = {k: v for k, v in seat_series.get(i, [])}
            map_j = {k: v for k, v in seat_series.get(j, [])}
            common = sorted(set(map_i).intersection(map_j))
            if len(common) < 3:
                continue
            xs = [map_i[k] for k in common]
            ys = [map_j[k] for k in common]
            c = _pearson(xs, ys)
            pairwise.append(PairCorr(pair=(i, j), corr=c, samples=len(common)))

    if not pairwise:
        return {
            "mode": "none",
            "strength": 0.0,
            "confidence": 0.0,
            "n_auctions": len(auctions),
            "pairwise": [],
        }

    pairwise_sorted = sorted(pairwise, key=lambda r: r.corr, reverse=True)
    positive = [p for p in pairwise_sorted if p.corr > 0.2]
    high = [p for p in pairwise_sorted if p.corr > 0.35]
    top = pairwise_sorted[0]

    mode = "none"
    if high:
        # Two disjoint strongly correlated pairs indicate coalition/kingmaker dynamics.
        disjoint_found = False
        for i in range(len(high)):
            for j in range(i + 1, len(high)):
                a = set(high[i].pair)
                b = set(high[j].pair)
                if a.isdisjoint(b):
                    disjoint_found = True
                    break
            if disjoint_found:
                break

        if disjoint_found:
            mode = "kingmaker"
        else:
            dense_positive = len(positive) >= 4 and mean(p.corr for p in positive) > 0.28
            mode = "herd" if dense_positive else "respect"
    else:
        avg_pos = mean(p.corr for p in positive) if positive else 0.0
        if avg_pos > 0.25 and len(positive) >= 4:
            mode = "herd"
        else:
            mode = "none"

    strength = max(0.0, min(1.0, top.corr))
    confidence = max(0.0, min(1.0, min(1.0, top.samples / 10.0)))

    return {
        "mode": mode,
        "strength": strength,
        "confidence": confidence,
        "n_auctions": len(auctions),
        "pairwise": [
            {
                "pair": list(p.pair),
                "corr": p.corr,
                "samples": p.samples,
            }
            for p in pairwise_sorted[:8]
        ],
    }
