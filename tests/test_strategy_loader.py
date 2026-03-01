import unittest

from sim import CorrelationModel, run_match
from strategies.loader import load_strategy


class StrategyLoaderTests(unittest.TestCase):
    def test_can_load_parameterized_builtin(self):
        strategy = load_strategy(
            "prob_value:bid_scale=0.9,sell_count=1,min_delta_to_bid=500,stack_cap_fraction=0.5"
        )
        self.assertEqual(strategy.sell_count, 1)
        self.assertAlmostEqual(strategy.bid_scale, 0.9)
        self.assertEqual(strategy.min_delta_to_bid, 500)
        self.assertEqual(
            strategy.tag,
            "prob_value:bid_scale=0.9,min_delta_to_bid=500,sell_count=1,stack_cap_fraction=0.5",
        )

    def test_parameterized_strategy_runs_in_match(self):
        out = run_match(
            [
                "prob_value:bid_scale=1.05,sell_count=2,min_delta_to_bid=300",
                "conservative",
                "bully",
                "random",
                "risk_sniper:trigger_delta=2400",
            ],
            n_games=1,
            seed=13,
            correlation=CorrelationModel(mode="none", strength=0.0, pairs=[]),
        )
        self.assertEqual(len(out["games"]), 1)
        self.assertEqual(len(out["strategy_tags"]), 5)


if __name__ == "__main__":
    unittest.main()
