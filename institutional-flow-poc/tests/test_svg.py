import unittest

from institutional_flow_poc.svg import render_basis_comparison_svg, render_model_comparison_svg, render_rotation_svg


class SvgTests(unittest.TestCase):
    def test_renderer_outputs_svg_with_trails_and_labels(self):
        rows = [{"date": "2026-08-28", "industry_code": "01", "industry_name": "水泥工業", "model_b_x": 0.1, "model_b_y": 0.2}]
        svg = render_rotation_svg(rows, "foreign", "B")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("水泥工業", svg)
        self.assertIn("polyline", svg)

    def test_model_comparison_renderer_has_two_panels(self):
        rows = [{"date": "2026-08-28", "institution": "foreign", "industry_code": "01", "industry_name": "水泥工業", "model_a_x": 0.2, "model_a_y": 0.1, "model_b_x": 0.3, "model_b_y": 0.2}]
        svg = render_model_comparison_svg(rows)
        self.assertIn("Model A", svg)
        self.assertIn("Model B", svg)

    def test_basis_renderer_labels_bases(self):
        svg = render_basis_comparison_svg([{"date": "2026-08-28", "institution": "foreign", "industry_name": "水泥工業", "shares_flow_5d": 0.1, "amount_flow_5d": 0.2, "delta_flow_5d": 0.1}], "shares", "amount")
        self.assertIn("shares", svg)
        self.assertIn("amount", svg)


if __name__ == "__main__":
    unittest.main()
