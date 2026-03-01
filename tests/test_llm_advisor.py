import unittest

from game.llm_advisor import _normalize_hint, _safe_json


class LlmAdvisorTests(unittest.TestCase):
    def test_safe_json_parses_code_fence(self):
        txt = "```json\n{\"bid\": 12, \"confidence\": 0.8, \"mode\": \"balanced\", \"rationale\": \"ok\"}\n```"
        out = _safe_json(txt)
        self.assertEqual(out["bid"], 12)
        self.assertEqual(out["mode"], "balanced")

    def test_safe_json_extracts_embedded_object(self):
        txt = "Answer: {\"bid\": 20, \"confidence\": 0.6, \"mode\": \"aggressive\", \"rationale\": \"push\"} end"
        out = _safe_json(txt)
        self.assertEqual(out["bid"], 20)
        self.assertEqual(out["mode"], "aggressive")

    def test_normalize_hint_clamps_fields(self):
        raw = {
            "bid": 9999,
            "confidence": 1.7,
            "mode": "wild",
            "rationale": "",
        }
        state = {"stack": 120, "fair_bid": 35}
        out = _normalize_hint(raw, state)
        self.assertEqual(out["bid"], 120)
        self.assertEqual(out["confidence"], 1.0)
        self.assertEqual(out["mode"], "balanced")
        self.assertTrue(out["rationale"])


if __name__ == "__main__":
    unittest.main()
