import unittest

from game.utils import compare_hands, ranking_order


class HandRankingTests(unittest.TestCase):
    def test_rarity_order_has_flush_above_four_kind(self):
        order = ranking_order("rarity_50")
        self.assertLess(order.index("flush"), order.index("four_kind"))

    def test_high_card_beats_pair_under_rarity_policy(self):
        high_card = [(10, "C"), (8, "D"), (6, "H"), (4, "S"), (2, "X")]
        one_pair = [(9, "C"), (9, "D"), (7, "H"), (5, "S"), (3, "X")]
        self.assertEqual(compare_hands(high_card, one_pair, policy="rarity_50"), 1)

    def test_pair_beats_high_card_under_standard_policy(self):
        high_card = [(10, "C"), (8, "D"), (6, "H"), (4, "S"), (2, "X")]
        one_pair = [(9, "C"), (9, "D"), (7, "H"), (5, "S"), (3, "X")]
        self.assertEqual(
            compare_hands(high_card, one_pair, policy="standard_plus_five_kind"), -1
        )


if __name__ == "__main__":
    unittest.main()
