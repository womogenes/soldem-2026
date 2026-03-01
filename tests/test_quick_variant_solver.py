import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class QuickVariantSolverTests(unittest.TestCase):
    def test_solver_handles_non_default_player_count(self):
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "n6.json"
            cmd = [
                sys.executable,
                str(ROOT / "scripts" / "quick_variant_hero_solver.py"),
                "--rule-profile",
                "baseline_v1",
                "--rule-overrides-json",
                '{"n_players":6}',
                "--objectives",
                "first_place",
                "--n-tables",
                "1",
                "--n-games",
                "1",
                "--seed",
                "1",
                "--out",
                str(out_path),
            ]
            subprocess.run(cmd, check=True, cwd=ROOT)
            data = json.loads(out_path.read_text(encoding="utf-8"))
        winner = data["objective_winners"]["first_place"]["winner"]
        self.assertTrue(isinstance(winner, str) and len(winner) > 0)


if __name__ == "__main__":
    unittest.main()
