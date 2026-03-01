from __future__ import annotations

import unittest

from game.correlation import infer_correlation_mode


def _event_bid(seat: int, amount: int) -> dict:
    return {
        "event_type": "bid",
        "seat": seat,
        "amount": amount,
    }


def _event_close() -> dict:
    return {"event_type": "auction_result"}


class CorrelationInferenceTests(unittest.TestCase):
    def test_sparse_events_returns_none(self):
        events = [
            _event_bid(0, 40),
            _event_bid(1, 42),
            _event_close(),
        ]
        out = infer_correlation_mode(events, n_players=5)
        self.assertEqual(out["mode"], "none")
        self.assertEqual(out["strength"], 0.0)

    def test_single_strong_pair_maps_to_respect(self):
        events = []
        for k in range(8):
            events.extend(
                [
                    _event_bid(1, 30 + (4 * k)),
                    _event_bid(2, 31 + (4 * k)),
                    _event_bid(0, 85 - (3 * k)),
                    _event_bid(3, 12 + (k % 3)),
                    _event_close(),
                ]
            )
        out = infer_correlation_mode(events, n_players=5)
        self.assertEqual(out["mode"], "respect")
        self.assertGreater(out["strength"], 0.35)

    def test_two_disjoint_pairs_maps_to_kingmaker(self):
        events = []
        for k in range(9):
            events.extend(
                [
                    _event_bid(0, 18 + (3 * k)),
                    _event_bid(1, 20 + (3 * k)),
                    _event_bid(2, 70 - (2 * k)),
                    _event_bid(3, 69 - (2 * k)),
                    _event_bid(4, 40 + ((k * 7) % 9)),
                    _event_close(),
                ]
            )
        out = infer_correlation_mode(events, n_players=5)
        self.assertEqual(out["mode"], "kingmaker")
        self.assertGreater(out["strength"], 0.35)


if __name__ == "__main__":
    unittest.main()
