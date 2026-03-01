import unittest

from sim import CorrelationModel, run_match


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


if __name__ == "__main__":
    unittest.main()
