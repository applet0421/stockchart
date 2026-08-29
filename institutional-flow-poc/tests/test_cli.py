import unittest

from institutional_flow_poc.cli import build_parser


class CliTests(unittest.TestCase):
    def test_run_command_accepts_days_and_end_date(self):
        args = build_parser().parse_args(["run", "--days", "120", "--end-date", "2026-08-28"])
        self.assertEqual((args.command, args.days, args.end_date), ("run", 120, "2026-08-28"))

    def test_analyze_accepts_amount_basis(self):
        args = build_parser().parse_args(["analyze", "--basis", "amount"])
        self.assertEqual(args.basis, "amount")

    def test_analyze_accepts_compare_basis(self):
        args = build_parser().parse_args(["analyze", "--compare-basis", "amount"])
        self.assertEqual(args.compare_basis, "amount")


if __name__ == "__main__":
    unittest.main()
