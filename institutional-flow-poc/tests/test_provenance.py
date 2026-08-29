import tempfile
import unittest
from pathlib import Path

from institutional_flow_poc.provenance import build_run_manifest, latest_rows


class ProvenanceTests(unittest.TestCase):
    def test_latest_rows_selects_latest_date_without_adding_labels(self):
        rows = [{"date": "2026-08-27", "sector": "食品工業"}, {"date": "2026-08-28", "sector": "半導體業"}]
        result = latest_rows(rows)
        self.assertEqual(result, [{"date": "2026-08-28", "sector": "半導體業"}])
        self.assertNotIn("trend", result[0])

    def test_manifest_contains_source_and_file_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "snapshot.csv"
            file_path.write_text("a,b\n1,2\n", encoding="utf-8")
            result = build_run_manifest({"generated_at": "2026-08-29T00:00:00+00:00", "source_urls": {"t86": "https://www.twse.com.tw/rwd/zh/fund/T86"}, "date_min": "2026-08-28", "date_max": "2026-08-28", "row_counts": {"snapshot": 1}}, [file_path])
            self.assertEqual(result["source_urls"]["t86"], "https://www.twse.com.tw/rwd/zh/fund/T86")
            self.assertEqual(result["files"][0]["path"], "snapshot.csv")
            self.assertEqual(result["files"][0]["sha256"], "492d5ea496056f1a6a6592241032fab764c321596317930b4fa0e1e8bc3b7470")


if __name__ == "__main__":
    unittest.main()
