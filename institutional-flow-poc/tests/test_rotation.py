import unittest

from institutional_flow_poc.rotation import build_model_comparison, build_rotation_rows, build_transition_matrix, build_signal_outcomes


class RotationTests(unittest.TestCase):
    def test_models_and_quadrants(self):
        sector = [{"date": "2026-08-28", "industry_code": "01", "industry_name": "水泥工業", "institution": "foreign", "flow_1d": 0.1, "flow_5d": -0.2, "flow_20d": 0.3}]
        rows = build_rotation_rows(sector)
        self.assertEqual(rows[0]["model_a_quadrant"], "REVERSING")
        self.assertEqual(rows[0]["model_b_quadrant"], "WEAKENING")

    def test_model_comparison_keeps_both_model_coordinates(self):
        rows = build_model_comparison([{
            "date": "2026-08-28", "institution": "foreign", "industry_code": "01", "industry_name": "水泥工業",
            "model_a_x": 0.2, "model_a_y": -0.1, "model_a_quadrant": "WEAKENING",
            "model_b_x": 0.3, "model_b_y": 0.2, "model_b_quadrant": "ACCUMULATING",
        }])
        self.assertEqual(rows[0]["model_a_quadrant"], "WEAKENING")
        self.assertEqual(rows[0]["model_b_quadrant"], "ACCUMULATING")

    def test_transition_probability(self):
        rows = [
            {"date": "2026-08-27", "industry_code": "01", "institution": "foreign", "model_a_quadrant": "REVERSING", "model_b_quadrant": "ACCUMULATING"},
            {"date": "2026-08-28", "industry_code": "01", "institution": "foreign", "model_a_quadrant": "ACCUMULATING", "model_b_quadrant": "ACCUMULATING"},
        ]
        matrix = build_transition_matrix(rows)
        item = next(x for x in matrix if x["model"] == "A")
        self.assertEqual((item["count"], item["probability"]), (1, 1.0))

    def test_reversal_outcome_uses_future_values(self):
        rows = []
        for i, flow in enumerate([-0.1, 0.1, 0.2, -0.1, 0.2, 0.3, 0.4]):
            rows.append({"date": f"2026-08-{20+i:02d}", "industry_code": "01", "industry_name": "水泥工業", "institution": "foreign", "flow_1d": flow, "flow_5d": flow, "flow_20d": -0.2 if i == 0 else flow, "model_a_quadrant": "REVERSING" if i == 0 else "ACCUMULATING", "model_b_quadrant": "REVERSING" if i == 0 else "ACCUMULATING"})
        outcomes = build_signal_outcomes(rows)
        first = next(x for x in outcomes if x["model"] == "A")
        self.assertAlmostEqual(first["future_3d_direction_rate"], 2 / 3)
        self.assertTrue(first["success_5d"])


if __name__ == "__main__":
    unittest.main()
