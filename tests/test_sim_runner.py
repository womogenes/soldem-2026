import unittest

from sim import CorrelationModel, run_match
from strategies.builtin import built_in_strategy_factories


class SimRunnerTests(unittest.TestCase):
    def test_run_match_smoke(self):
        out = run_match(
            ["random", "pot_fraction", "delta_value", "conservative", "bully"],
            n_games=2,
            seed=5,
            correlation=CorrelationModel(mode="none", strength=0.0, pairs=[]),
        )
        self.assertEqual(len(out["games"]), 2)
        self.assertEqual(len(out["seat_avg_pnl"]), 5)
        self.assertEqual(len(out["strategy_tags"]), 5)

    def test_new_strategy_tags_registered(self):
        tags = built_in_strategy_factories().keys()
        self.assertIn("market_maker", tags)
        self.assertIn("market_maker_tight", tags)
        self.assertIn("conservative_ultra", tags)
        self.assertIn("elastic_conservative", tags)
        self.assertIn("regime_switch_robust", tags)

    def test_run_match_with_new_strategies(self):
        out = run_match(
            [
                "market_maker",
                "conservative_ultra",
                "conservative",
                "elastic_conservative",
                "mc_edge",
            ],
            n_games=2,
            seed=11,
            correlation=CorrelationModel(mode="none", strength=0.0, pairs=[]),
        )
        self.assertEqual(len(out["games"]), 2)


if __name__ == "__main__":
    unittest.main()
