import unittest

from institutional_flow_poc.quality import validate_day


class QualityTests(unittest.TestCase):
    def test_detects_duplicates_arithmetic_and_missing_symbols(self):
        market = [{"date": "2026-08-28", "symbol": "1101"}, {"date": "2026-08-28", "symbol": "1101"}, {"date": "2026-08-28", "symbol": "2330"}]
        flow = [{"date": "2026-08-28", "symbol": "1101", "foreign_buy": 10, "foreign_sell": 2, "foreign_net": 7, "trust_buy": 4, "trust_sell": 1, "trust_net": 3}]
        result = validate_day("2026-08-28", market, flow)
        self.assertFalse(result["success"])
        self.assertEqual(result["duplicate_market"], ["1101"])
        self.assertEqual(result["foreign_arithmetic_failures"], ["1101"])
        self.assertEqual(result["missing_in_flow"], ["2330"])


if __name__ == "__main__":
    unittest.main()
