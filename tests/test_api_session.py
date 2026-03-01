import unittest
from unittest.mock import patch

from game import api as api_module
from game.api import (
    Session,
    SessionEventReq,
    SetChampionsReq,
    RecomputeChampionsReq,
    RecommendationReq,
    advisor_recommend,
    normalize_round_request,
    resolver_reason_text,
)
from game.rules import resolve_profile


class ApiSessionTests(unittest.TestCase):
    def test_advisor_recommend_includes_normalized_round_single_mode(self):
        api_module.session.apply_profile(
            "baseline_v1",
            {"n_players": 6, "start_chips": 200},
        )
        api_module.session.reset()
        try:
            out = advisor_recommend(
                RecommendationReq(
                    phase="bid",
                    output_mode="metrics",
                    objective="ev",
                    seat=99,
                    seller_idx=99,
                    round_num=-4,
                    n_orbits=0,
                    pot=-3,
                    stacks=[100, -5, 50],
                    my_cards=[(14, "spades"), (10, "hearts")],
                    auction_cards=[(13, "clubs")],
                )
            )
            self.assertIn("normalized_round", out)
            norm = out["normalized_round"]
            self.assertEqual(norm["seat"], 5)
            self.assertEqual(norm["seller_idx"], 5)
            self.assertEqual(norm["round_num"], 0)
            self.assertEqual(norm["n_orbits"], 1)
            self.assertEqual(norm["pot"], 0)
            self.assertEqual(norm["stacks"], [100, 0, 50, 200, 200, 200])
            self.assertEqual(out["rule_profile"]["n_players"], 6)
        finally:
            api_module.session.apply_profile("baseline_v1", {})
            api_module.session.reset()

    def test_advisor_recommend_includes_normalized_round_all_mode(self):
        api_module.session.apply_profile("baseline_v1", {})
        api_module.session.reset()
        try:
            out = advisor_recommend(
                RecommendationReq(
                    phase="bid",
                    output_mode="all",
                    objective="first_place",
                    seat=-2,
                    seller_idx=-3,
                    round_num=1,
                    n_orbits=3,
                    pot=50,
                    stacks=[10, 20, 30, 40, 50, 999],
                    my_cards=[(12, "diamonds"), (7, "clubs")],
                    auction_cards=[(13, "spades")],
                )
            )
            self.assertIn("normalized_round", out)
            self.assertIn("modes", out)
            self.assertIn("action_first", out["modes"])
            self.assertIn("metrics", out["modes"])
            self.assertIn("top3", out["modes"])
            norm = out["normalized_round"]
            self.assertEqual(norm["seat"], 0)
            self.assertEqual(norm["seller_idx"], -1)
            self.assertEqual(norm["stacks"], [10, 20, 30, 40, 50])
        finally:
            api_module.session.apply_profile("baseline_v1", {})
            api_module.session.reset()

    def test_normalize_round_request_pads_and_clamps_for_six_players(self):
        profile = resolve_profile("baseline_v1", n_players=6, start_chips=200)
        norm = normalize_round_request(
            seat=9,
            seller_idx=8,
            stacks=[100, -5, 50],
            round_num=-3,
            n_orbits=0,
            pot=-20,
            rule_profile=profile,
        )
        self.assertEqual(norm["seat"], 5)
        self.assertEqual(norm["seller_idx"], 5)
        self.assertEqual(norm["round_num"], 0)
        self.assertEqual(norm["n_orbits"], 1)
        self.assertEqual(norm["pot"], 0)
        self.assertEqual(norm["stacks"], [100, 0, 50, 200, 200, 200])

    def test_normalize_round_request_trims_extra_stacks(self):
        profile = resolve_profile("baseline_v1", n_players=5, start_chips=160)
        norm = normalize_round_request(
            seat=-2,
            seller_idx=-9,
            stacks=[10, 20, 30, 40, 50, 999, 111],
            round_num=2,
            n_orbits=3,
            pot=100,
            rule_profile=profile,
        )
        self.assertEqual(norm["seat"], 0)
        self.assertEqual(norm["seller_idx"], -1)
        self.assertEqual(norm["stacks"], [10, 20, 30, 40, 50])

    def test_resolver_reason_text_helper(self):
        self.assertEqual(
            resolver_reason_text("high_ante_pressure_first_place"),
            "High-ante winner-takes-all pressure: first-place routing moved to pot_fraction.",
        )
        self.assertEqual(
            resolver_reason_text("correlated_pair_defensive_first_place"),
            "Correlated-pair table read with high confidence: first-place routing moved to equity_evolved_v1.",
        )
        self.assertEqual(resolver_reason_text(""), "No resolver reason available.")
        self.assertEqual(resolver_reason_text("unknown_reason"), "unknown_reason")

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

    def test_absolute_ante_trigger_prefers_pot_fraction_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 200,
                "ante_amt": 50,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_ratio_trigger_prefers_pot_fraction_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 3,
                "start_chips": 160,
                "ante_amt": 42,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_non_sprint_low_ante_wta_prefers_pot_fraction_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 140,
                "ante_amt": 35,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "pot_fraction")

    def test_non_sprint_mid_ante_wta_prefers_meta_switch_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 160,
                "ante_amt": 35,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "meta_switch")

    def test_high_stack_low_ante_wta_prefers_evolved_first_place(self):
        s = Session()
        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 200,
                "ante_amt": 35,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        self.assertEqual(s.resolve_champion("first_place"), "equity_evolved_v1")

    def test_first_place_policy_cues_export(self):
        s = Session()
        base = s.first_place_policy_cues()
        self.assertTrue(base["exact_baseline"])
        self.assertEqual(base["default_first_place"], "meta_switch")

        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 140,
                "ante_amt": 50,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        high = s.first_place_policy_cues()
        self.assertTrue(high["high_ante_pressure"])
        self.assertEqual(high["default_first_place"], "pot_fraction")

        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 200,
                "ante_amt": 50,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        high_abs = s.first_place_policy_cues()
        self.assertTrue(high_abs["high_ante_pressure"])
        self.assertEqual(high_abs["default_first_place"], "pot_fraction")

        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 4,
                "start_chips": 200,
                "ante_amt": 35,
                "pot_distribution_policy": "winner_takes_all",
            },
        )
        relief = s.first_place_policy_cues()
        self.assertTrue(relief["high_stack_low_ante_relief"])
        self.assertEqual(relief["default_first_place"], "equity_evolved_v1")

        s.apply_profile(
            "baseline_v1",
            {
                "n_orbits": 2,
                "start_chips": 140,
                "ante_amt": 30,
                "pot_distribution_policy": "high_low_split",
            },
        )
        split = s.first_place_policy_cues()
        self.assertTrue(split["sprint_profile"])
        self.assertFalse(split["winner_takes_all"])
        self.assertEqual(split["default_first_place"], "equity_evolved_v1")

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
        tag, reason = s.resolve_champion_with_reason("first_place")
        self.assertEqual(tag, "equity_evolved_v1")
        self.assertEqual(reason, "correlated_pair_defensive_first_place")

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
        self.assertEqual(out["resolved_champion_reasons"]["first_place"], "manual_lock")
        self.assertEqual(
            out["resolved_champion_reason_texts"]["first_place"],
            "Manual lock is active; dynamic routing is disabled.",
        )

    def test_session_state_exports_reason_texts(self):
        s = Session()
        state = s.state()
        self.assertIn("resolved_champion_reasons", state)
        self.assertIn("resolved_champion_reason_texts", state)
        self.assertIn("resolver_reason_text_map", state)
        self.assertEqual(
            state["resolved_champion_reason_texts"]["first_place"],
            "Exact baseline rules: first-place default is meta_switch.",
        )

    def test_profile_resize_to_six_players_updates_profiles_and_state(self):
        s = Session()
        s.apply_profile("baseline_v1", {"n_players": 6})
        self.assertEqual(len(s.player_profiles), 6)

        s.record_event(
            SessionEventReq(
                event_type="bid",
                seat=5,
                amount=40,
            )
        )
        self.assertEqual(s.player_profiles[5].bid_count, 1)

        state = s.state()
        self.assertEqual(state["rule_profile"]["n_players"], 6)
        self.assertEqual(len(state["player_profiles"]), 6)
        self.assertIn(5, state["player_profiles"])

    def test_infer_table_read_ignores_out_of_range_auction_events(self):
        s = Session()
        s.apply_profile("baseline_v1", {"n_players": 6})
        s.record_event(
            SessionEventReq(
                event_type="auction_result",
                seller_idx=9,
                winner_idx=1,
            )
        )
        s.record_event(
            SessionEventReq(
                event_type="auction_result",
                seller_idx=2,
                winner_idx=3,
            )
        )
        read = s.infer_table_read()
        self.assertEqual(read["n_auction_results"], 1)

    def test_recompute_champions_uses_active_rule_overrides(self):
        s = Session()
        s.apply_profile(
            "top2_split",
            {
                "n_players": 6,
                "start_chips": 220,
                "ante_amt": 33,
                "n_orbits": 4,
            },
        )
        board = [
            {
                "tag": "equity_evolved_v1",
                "expected_pnl": 1.0,
                "first_place_rate": 0.2,
                "robustness": 0.1,
                "composites": {},
            },
            {
                "tag": "meta_switch",
                "expected_pnl": 0.9,
                "first_place_rate": 0.1,
                "robustness": 0.05,
                "composites": {},
            },
        ]
        with patch("game.api.run_population_tournament", return_value={"leaderboard": board}) as mocked:
            s.recompute_champions(
                RecomputeChampionsReq(
                    n_matches=2,
                    n_games_per_match=2,
                    seed=7,
                )
            )
        self.assertEqual(mocked.call_count, 3)
        for call in mocked.call_args_list:
            kwargs = call.kwargs
            self.assertEqual(kwargs["rule_profile"], "top2_split")
            self.assertEqual(kwargs["rule_overrides"]["n_players"], 6)
            self.assertEqual(kwargs["rule_overrides"]["start_chips"], 220)
            self.assertEqual(kwargs["rule_overrides"]["ante_amt"], 33)
            self.assertEqual(kwargs["rule_overrides"]["n_orbits"], 4)


if __name__ == "__main__":
    unittest.main()
