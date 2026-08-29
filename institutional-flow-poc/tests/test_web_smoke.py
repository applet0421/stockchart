import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebSmokeTests(unittest.TestCase):
    def test_static_shell_and_payload_exist(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        payload = json.loads((ROOT / "web" / "data" / "model-a.json").read_text(encoding="utf-8"))
        self.assertIn('src="./src/main.js"', html)
        self.assertEqual(payload["meta"]["model"], "A")
        self.assertTrue(payload["latest"])
        self.assertTrue(payload["history"])
        self.assertIn("stocks_by_sector", payload)
        self.assertIn("stock_history_compact", payload)
        self.assertEqual(payload["topic_mapping"]["version"], "sector-v1")

    def test_core_navigation_labels_are_present_once(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        main = (ROOT / "web" / "src" / "main.js").read_text(encoding="utf-8")
        for label in ("今日觀察", "Model A", "法人排行", "追蹤產業", "資料品質"):
            self.assertEqual(main.count(label), 1, label)


if __name__ == "__main__":
    unittest.main()
