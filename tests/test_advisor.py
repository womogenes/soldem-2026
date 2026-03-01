import unittest

from game.advisor import recommend_action
from strategies import PlayerProfile


class AdvisorTests(unittest.TestCase):
    def test_recommendation_supports_parameterized_strategy_tag(self):
        profiles = {i: PlayerProfile(seat=i) for i in range(5)}
        rec = recommend_action(
            phase="bid",
            strategy_tag="seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2",
            seat=0,
            seller_idx=1,
            pot=220,
            stacks=[160, 160, 160, 160, 160],
            my_cards=[(7, "H"), (8, "H"), (9, "H"), (4, "C"), (4, "D")],
            auction_cards=[(10, "H"), (2, "S")],
            round_num=1,
            n_orbits=3,
            ranking_policy="rarity_50",
            objective="ev",
            output_mode="action_first",
            player_profiles=profiles,
            known_cards=[],
        )
        self.assertEqual(rec.phase, "bid")
        self.assertEqual(rec.primary_action["type"], "bid")


if __name__ == "__main__":
    unittest.main()
