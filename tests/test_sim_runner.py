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

    def test_run_match_smoke_six_players(self):
        out = run_match(
            ["random", "pot_fraction", "delta_value", "conservative", "bully", "random"],
            n_games=1,
            seed=7,
            rule_overrides={"n_players": 6},
            correlation=CorrelationModel(mode="none", strength=0.0, pairs=[]),
        )
        self.assertEqual(len(out["games"]), 1)
        self.assertEqual(len(out["seat_avg_pnl"]), 6)
        self.assertEqual(len(out["strategy_tags"]), 6)


if __name__ == "__main__":
    unittest.main()
