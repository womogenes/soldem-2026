import unittest

from game.api import Session, SessionEventReq, SetChampionsReq


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

    def test_baseline_first_place_prefers_meta_switch(self):
        s = Session()
        self.assertEqual(s.rule_profile.name, "baseline_v1")
        self.assertEqual(s.resolve_champion("first_place"), "meta_switch")

    def test_baseline_ev_prefers_evolved(self):
        s = Session()
        self.assertEqual(s.resolve_champion("ev"), "equity_evolved_v1")

    def test_aggressive_mode_keeps_ev_on_evolved(self):
        s = Session()
        for i, amt in enumerate([90, 100, 95, 105, 98, 93, 101, 96, 110, 92, 99]):
            s.record_event(
                SessionEventReq(
                    event_type="bid",
                    seat=i % 5,
                    amount=amt,
                )
            )
        read = s.infer_table_read()
        self.assertEqual(read["mode"], "aggressive")
        self.assertEqual(s.resolve_champion("ev"), "equity_evolved_v1")

    def test_sprint_profile_first_place_prefers_pot_fraction(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {"n_orbits": 2, "start_chips": 140, "ante_amt": 30},
        )
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_sprint_split_pot_profile_uses_evolved_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 2,
                "start_chips": 140,
                "ante_amt": 30,
                "pot_distribution_policy": "high_low_split",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "equity_evolved_v1")

    def test_high_ante_pressure_prefers_pot_fraction_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 140,
                "ante_amt": 50,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_correlated_pair_bias_switches_ev_to_evolved(self):
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
        self.assertEqual(s.resolve_champion("ev"), "equity_evolved_v1")
        self.assertEqual(s.resolve_champion("first_place"), "meta_switch")

    def test_rule_profile_override_still_takes_precedence(self):
        s = Session()
        s.apply_profile("high_low_split", {})
        self.assertEqual(s.resolve_champion("ev"), "equity_evolved_v1")

    def test_baseline_name_with_nonbaseline_overrides_uses_evolved_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "pot_distribution_policy": "top2_split",
                "allow_multi_card_sell": False,
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "equity_evolved_v1")

    def test_competitive_mode_switches_ev_to_evolved(self):
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
        self.assertEqual(s.resolve_champion("ev"), "equity_evolved_v1")
        self.assertEqual(s.resolve_champion("first_place"), "meta_switch")

    def test_manual_champion_override(self):
        s = Session()
        out = s.set_champions(
            SetChampionsReq(
                ev="equity_sniper_ultra",
                first_place="meta_switch",
                robustness="conservative_plus",
                lock_manual=True,
            )
        )
        self.assertEqual(out["champions"]["ev"], "equity_sniper_ultra")
        self.assertEqual(out["champions"]["first_place"], "meta_switch")
        self.assertFalse(out["dynamic_resolution_enabled"])
        self.assertEqual(out["resolved_champions"]["first_place"], "meta_switch")


if __name__ == "__main__":
    unittest.main()
