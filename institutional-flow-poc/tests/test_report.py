import unittest

from institutional_flow_poc.report import evaluate_decision


class ReportTests(unittest.TestCase):
    def test_report_is_observation_only_even_when_quality_is_incomplete(self):
        result = evaluate_decision({"success": False}, [], [])
        self.assertEqual(result["mode"], "observation_only")
        self.assertNotIn("decision", result)

    def test_observation_reports_empirical_rates_without_threshold_judgment(self):
        outcomes = [{"success_5d": False, "persistent_3d": False}] * 30
        sector = [{"top3_concentration_5d": 0.9}]
        result = evaluate_decision({"success": True, "successful_days": 120}, outcomes, sector)
        self.assertAlmostEqual(result["success_5d_rate"], 0.0)

    def test_observation_does_not_turn_strong_rates_into_go(self):
        outcomes = [{"success_5d": True, "persistent_3d": True}] * 30
        sector = [{"top3_concentration_5d": 0.5}]
        result = evaluate_decision({"success": True, "successful_days": 120}, outcomes, sector, pattern_difference={"top5_overlap": 0.4})
        self.assertEqual(result["mode"], "observation_only")
        self.assertNotIn("decision", result)

    def test_partial_run_is_reported_as_observation_only(self):
        result = evaluate_decision({"success": True, "successful_days": 35}, [], [])
        self.assertEqual(result["mode"], "observation_only")


if __name__ == "__main__":
    unittest.main()
