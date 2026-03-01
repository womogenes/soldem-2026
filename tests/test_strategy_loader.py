import unittest

from strategies.loader import load_strategy


class StrategyLoaderTests(unittest.TestCase):
    def test_load_builtin_with_overrides(self):
        s = load_strategy("level_k|level=3|l0_fraction=0.22|tag=levelk_custom")
        self.assertEqual(getattr(s, "tag", ""), "levelk_custom")
        self.assertEqual(getattr(s, "level", 0), 3)
        self.assertAlmostEqual(getattr(s, "l0_fraction", 0.0), 0.22, places=6)


if __name__ == "__main__":
    unittest.main()
