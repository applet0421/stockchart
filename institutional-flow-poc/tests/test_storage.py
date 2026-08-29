import tempfile
import unittest
from pathlib import Path

from institutional_flow_poc.storage import read_json, write_csv, write_json


class StorageTests(unittest.TestCase):
    def test_json_and_csv_outputs_are_created_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_json(root / "nested" / "value.json", {"success": True})
            write_csv(root / "rows.csv", [{"a": 1, "b": None}], ["a", "b"])
            self.assertEqual(read_json(root / "nested" / "value.json"), {"success": True})
            self.assertEqual((root / "rows.csv").read_text().splitlines(), ["a,b", "1,"])
            self.assertFalse(list(root.rglob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
