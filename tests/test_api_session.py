import unittest

from game.api import Session, SessionEventReq


class ApiSessionTests(unittest.TestCase):
    def test_passive_table_can_trigger_risk_on_first_place(self):
        s = Session()
        for _ in range(12):
            s.record_event(
                SessionEventReq(
                    event_type="bid",
                    seat=1,
                    amount=0,
                )
            )
        read = s.infer_table_read()
        self.assertEqual(read["mode"], "passive")
        self.assertGreaterEqual(read["confidence"], 0.7)
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_correlated_pair_bias_switches_ev_to_sniper(self):
        s = Session()
        events = [
            (0, 1),
            (1, 0),
            (0, 1),
            (1, 0),
            (2, 3),
            (3, 4),
            (0, 1),
            (1, 0),
        ]
        for seller, winner in events:
            s.record_event(
                SessionEventReq(
                    event_type="auction_result",
                    seller_idx=seller,
                    winner_idx=winner,
                )
            )
        read = s.infer_table_read()
        self.assertEqual(read["mode"], "correlated_pair")
        self.assertEqual(s.resolve_champion("ev"), "equity_sniper_ultra")

    def test_rule_profile_override_still_takes_precedence(self):
        s = Session()
        s.apply_profile("high_low_split", {})
        self.assertEqual(s.resolve_champion("ev"), "conservative_plus")

    def test_competitive_mode_switches_ev_to_sniper(self):
        s = Session()
        # Moderate, consistent bidding with few zero-bids.
        bids = [38, 42, 35, 41, 36, 39, 44, 33, 40, 37, 34, 43]
        for i, amt in enumerate(bids):
            s.record_event(
                SessionEventReq(
                    event_type="bid",
                    seat=i % 5,
                    amount=amt,
                )
            )
        read = s.infer_table_read()
        self.assertEqual(read["mode"], "competitive")
        self.assertEqual(s.resolve_champion("ev"), "equity_sniper_ultra")


if __name__ == "__main__":
    unittest.main()
