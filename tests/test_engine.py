import unittest

from game.engine_base import Game


class EngineTests(unittest.TestCase):
    def test_defaults_match_rules(self):
        g = Game()
        s = g.reset(seed=1)
        self.assertEqual(g.ante_amt, 40)
        self.assertEqual(g.n_orbits, 3)
        self.assertEqual(s["pot"], 200)
        self.assertEqual(s["player_stacks"], [160, 160, 160, 160, 160])

    def test_tie_break_earliest_bid_wins(self):
        g = Game()
        g.reset(seed=2)
        for i in range(5):
            g.player_bid(i, 10, bid_ts=float(i))
        close = g.close_bids()
        self.assertEqual(close["winner"], 0)

    def test_seller_cannot_bid_on_own_auction_by_default(self):
        g = Game()
        g.reset(seed=3)
        for i in range(5):
            g.player_bid(i, 0, bid_ts=float(i))
        g.close_bids()
        g.win_card(0)
        seller = g.seller_idx
        self.assertIsNotNone(seller)
        with self.assertRaises(ValueError):
            g.player_bid(seller, 10)


if __name__ == "__main__":
    unittest.main()
