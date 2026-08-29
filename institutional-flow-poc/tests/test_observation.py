import unittest

from institutional_flow_poc.observation import build_institution_comparison, build_sector_observations, build_quality_observations


class ObservationTests(unittest.TestCase):
    def setUp(self):
        base = {"date": "2026-08-28", "industry_code": "01", "industry_name": "水泥工業"}
        self.rows = [
            {**base, "institution": "foreign", "flow_1d": 0.1, "flow_5d": 0.2, "flow_20d": 0.3, "breadth_5d": 0.6, "top1_concentration_5d": 0.7, "top3_concentration_5d": 0.9, "stock_count_5d": 7},
            {**base, "institution": "trust", "flow_1d": -0.1, "flow_5d": -0.2, "flow_20d": -0.3, "breadth_5d": 0.2, "top1_concentration_5d": 0.8, "top3_concentration_5d": 1.0, "stock_count_5d": 7},
        ]

    def test_sector_observation_keeps_daily_descriptive_fields(self):
        rows = build_sector_observations(self.rows)
        self.assertEqual(rows[0]["sector"], "水泥工業")
        self.assertEqual(rows[0]["flow_5d"], 0.2)
        self.assertNotIn("signal", rows[0])

    def test_institution_comparison_joins_same_sector_date(self):
        rows = build_institution_comparison(self.rows)
        self.assertEqual(rows, [{
            "date": "2026-08-28", "sector": "水泥工業", "industry_code": "01",
            "foreign_flow_5d": 0.2, "trust_flow_5d": -0.2,
            "foreign_breadth_5d": 0.6, "trust_breadth_5d": 0.2,
            "foreign_top3_concentration_5d": 0.9, "trust_top3_concentration_5d": 1.0,
            "combined_flow_5d": None, "combined_breadth_5d": None,
            "combined_top3_concentration_5d": None,
            "dealer_flow_5d": None, "dealer_breadth_5d": None,
            "dealer_top3_concentration_5d": None,
            "foreign+trust_flow_5d": None, "foreign+trust_breadth_5d": None,
            "foreign+trust_top3_concentration_5d": None,
            "all_flow_5d": None, "all_breadth_5d": None,
            "all_top3_concentration_5d": None,
        }])

    def test_institution_comparison_includes_combined_flow(self):
        rows = build_institution_comparison(self.rows)
        self.assertIn("combined_flow_5d", rows[0])

    def test_quality_observation_exposes_source_counts(self):
        rows = build_quality_observations({"per_day": [{"date": "2026-08-28", "market_row_count": 3, "flow_row_count": 2, "missing_in_flow": ["1101"], "duplicate_market": [], "duplicate_flow": [], "foreign_arithmetic_failures": [], "trust_arithmetic_failures": [], "success": True}]})
        self.assertEqual(rows[0], {"date": "2026-08-28", "market_row_count": 3, "flow_row_count": 2, "missing_in_flow_count": 1, "duplicate_count": 0, "arithmetic_failure_count": 0, "success": True})


if __name__ == "__main__":
    unittest.main()
