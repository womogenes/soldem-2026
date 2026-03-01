import json
import tempfile
import time
import unittest
from pathlib import Path

from game.champion_loader import (
    champions_from_summary_payload,
    find_latest_summary_path,
    load_champions_from_summary_file,
)


class ChampionLoaderTests(unittest.TestCase):
    def test_distributed_summary_sets_per_objective_champions(self):
        payload = {
            "winner_counts": {"a": 10, "b": 8},
            "winner_by_objective": {
                "ev": {"a": 7, "b": 2},
                "first_place": {"a": 2, "b": 6},
                "robustness": {"a": 5, "b": 4},
            },
        }
        champions, details = champions_from_summary_payload(payload, default_tag="z")
        self.assertEqual(champions["ev"], "a")
        self.assertEqual(champions["first_place"], "b")
        self.assertEqual(champions["robustness"], "a")
        self.assertEqual(details["source_type"], "distributed_counts")

    def test_param_sweep_summary_sets_objective_specific_champions(self):
        payload = {
            "candidate_summary": [
                {
                    "candidate": "x",
                    "mean_delta_vs_champion": 0.9,
                    "wins": 90,
                    "losses": 10,
                    "by_objective": {
                        "ev": {"mean_delta": 0.6, "wins": 30, "ties": 1},
                        "first_place": {"mean_delta": 0.4, "wins": 20, "ties": 2},
                    },
                },
                {
                    "candidate": "y",
                    "mean_delta_vs_champion": 0.8,
                    "wins": 80,
                    "losses": 20,
                    "by_objective": {
                        "ev": {"mean_delta": 0.7, "wins": 35, "ties": 1},
                        "first_place": {"mean_delta": 0.3, "wins": 18, "ties": 1},
                        "robustness": {"mean_delta": 0.9, "wins": 40, "ties": 0},
                    },
                },
            ]
        }
        champions, details = champions_from_summary_payload(payload, default_tag="z")
        self.assertEqual(champions["ev"], "y")
        self.assertEqual(champions["first_place"], "x")
        self.assertEqual(champions["robustness"], "y")
        self.assertEqual(details["source_type"], "param_sweep")

    def test_find_latest_summary_path_and_load_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            older = root / "distributed_master_summary_20260301.json"
            newer = root / "distributed_master_summary_20260302.json"
            older.write_text(json.dumps({"winner_counts": {"a": 1}}), encoding="utf-8")
            time.sleep(0.01)
            newer.write_text(json.dumps({"winner_counts": {"b": 1}}), encoding="utf-8")
            latest = find_latest_summary_path(root)
            self.assertEqual(latest, newer)

            champs, details = load_champions_from_summary_file(latest, default_tag="z")
            self.assertEqual(champs["ev"], "b")
            self.assertEqual(details["summary_path"], str(newer))

    def test_profile_objective_votes_format(self):
        payload = {
            "baseline_v1": {
                "ev": {"champion_tag": "x", "vote_count": 10},
                "first_place": {"champion_tag": "x", "vote_count": 3},
                "robustness": {"champion_tag": "y", "vote_count": 8},
            },
            "top2_split": {
                "ev": {"champion_tag": "y", "vote_count": 12},
                "first_place": {"champion_tag": "x", "vote_count": 11},
                "robustness": {"champion_tag": "y", "vote_count": 7},
            },
        }
        champions, details = champions_from_summary_payload(payload, default_tag="z")
        self.assertEqual(champions["ev"], "y")
        self.assertEqual(champions["first_place"], "x")
        self.assertEqual(champions["robustness"], "y")
        self.assertEqual(details["source_type"], "profile_objective_votes")

    def test_recommended_session_champions_format(self):
        payload = {
            "run_id": "abc",
            "n_scenarios": 216,
            "recommended_session_champions": {
                "ev": "a",
                "first_place": "b",
                "robustness": "c",
            },
        }
        champions, details = champions_from_summary_payload(payload, default_tag="z")
        self.assertEqual(champions, {"ev": "a", "first_place": "b", "robustness": "c"})
        self.assertEqual(details["source_type"], "recommended_session_champions")


if __name__ == "__main__":
    unittest.main()
