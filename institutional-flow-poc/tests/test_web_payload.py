import unittest

from institutional_flow_poc.web_payload import build_model_a_payload


SECTOR_ROWS = [
    {
        "date": "2026-08-28",
        "institution": "all",
        "industry_code": "01",
        "sector": "水泥工業",
        "flow_1d": 0.1,
        "flow_5d": 0.2,
        "flow_20d": 0.3,
        "breadth_5d": 0.5,
        "top1_concentration_5d": 0.6,
        "top3_concentration_5d": 0.8,
        "stock_count_5d": 7,
    }
]
SECTOR_ROWS_WITH_NULLS = [{**SECTOR_ROWS[0], "flow_5d": None}]
ROTATION_ROWS = [
    {
        "date": "2026-08-28",
        "institution": "all",
        "industry_code": "01",
        "industry_name": "水泥工業",
        "model_a_x": 0.2,
        "model_a_y": 0.1,
        "model_a_quadrant": "ACCUMULATING",
    }
]
INSTITUTION_ROWS = [
    {
        "date": "2026-08-28",
        "sector": "水泥工業",
        "industry_code": "01",
        "all_flow_5d": 0.2,
        "all_breadth_5d": 0.5,
        "all_top3_concentration_5d": 0.8,
    }
]
QUALITY = {
    "generated_at": "2026-08-29T00:00:00+00:00",
    "required_days": 120,
    "successful_days": 120,
    "success": True,
    "failure": [],
}
STOCK_FLOW_ROWS = [
    {"date": "2026-08-28", "symbol": "1101", "name": "台泥", "all_flow_1d": 0.1, "all_flow_5d": 0.2, "all_flow_20d": 0.3, "foreign_flow_1d": 0.1, "foreign_flow_5d": 0.2, "foreign_flow_20d": 0.3, "foreign_net": 10, "trust_net": 2, "dealer_net": -1, "source_missing": False},
    {"date": "2026-08-28", "symbol": "1102", "name": "亞泥", "all_flow_1d": None, "all_flow_5d": None, "all_flow_20d": None, "foreign_flow_1d": None, "foreign_flow_5d": None, "foreign_flow_20d": None, "foreign_net": None, "trust_net": None, "dealer_net": None, "source_missing": True},
]
STOCK_MASTER_ROWS = [
    {"symbol": "1101", "name": "台泥", "industry_code": "01", "industry_name": "水泥工業"},
    {"symbol": "1102", "name": "亞泥", "industry_code": "01", "industry_name": "水泥工業"},
]


class WebPayloadTests(unittest.TestCase):
    def test_build_model_a_payload_has_model_a_axes_and_quality(self):
        payload = build_model_a_payload(SECTOR_ROWS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY)
        self.assertEqual(payload["meta"]["model"], "A")
        self.assertEqual(payload["meta"]["x_metric"], "flow_5d")
        self.assertEqual(payload["meta"]["y_metric"], "flow_1d")
        self.assertTrue(payload["quality"]["success"])

    def test_missing_window_values_remain_null(self):
        payload = build_model_a_payload(SECTOR_ROWS_WITH_NULLS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY)
        row = next(item for item in payload["latest"] if item["industry_code"] == "01")
        self.assertIsNone(row["flow_5d"])

    def test_unsupported_model_or_basis_is_rejected(self):
        with self.assertRaises(ValueError):
            build_model_a_payload(SECTOR_ROWS, [{**ROTATION_ROWS[0], "model": "B"}], INSTITUTION_ROWS, QUALITY)
        with self.assertRaises(ValueError):
            build_model_a_payload(SECTOR_ROWS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY, basis="points")

    def test_stock_drilldown_preserves_nulls_and_contribution(self):
        payload = build_model_a_payload(
            SECTOR_ROWS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY,
            stock_flow_rows=STOCK_FLOW_ROWS, stock_master_rows=STOCK_MASTER_ROWS,
        )
        rows = payload["stocks_by_sector"]["all"]
        first = next(row for row in rows if row["symbol"] == "1101")
        missing = next(row for row in rows if row["symbol"] == "1102")
        self.assertAlmostEqual(first["contribution_share"], 1.0)
        self.assertTrue(missing["source_missing"])
        self.assertIsNone(missing["flow_5d"])
        self.assertEqual(payload["topic_mapping"]["version"], "sector-v1")
