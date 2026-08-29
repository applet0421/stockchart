import unittest

from institutional_flow_poc.metrics import compute_stock_flows, compute_sector_flows


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.stocks = [
            {"symbol": "1101", "industry_code": "01", "industry_name": "水泥工業"},
            {"symbol": "1102", "industry_code": "01", "industry_name": "水泥工業"},
        ]
        self.market = []
        self.flows = []
        for day, a, b in [("2026-08-24", 10, -5), ("2026-08-25", 20, -5), ("2026-08-26", 30, -5), ("2026-08-27", 40, -5), ("2026-08-28", 50, -5)]:
            for symbol, net in [("1101", a), ("1102", b)]:
                self.market.append({"date": day, "symbol": symbol, "volume": 100})
                self.flows.append({"date": day, "symbol": symbol, "foreign_buy": max(net, 0), "foreign_sell": max(-net, 0), "foreign_net": net, "trust_buy": 0, "trust_sell": 0, "trust_net": 0})

    def test_stock_window_ratio_uses_sum_net_over_sum_volume(self):
        rows = compute_stock_flows(self.market, self.flows)
        latest = next(r for r in rows if r["date"] == "2026-08-28" and r["symbol"] == "1101")
        self.assertEqual(latest["foreign_flow_1d"], 0.5)
        self.assertEqual(latest["foreign_flow_5d"], 0.3)
        self.assertIsNone(latest["foreign_flow_20d"])
        self.assertEqual(latest["combined_flow_1d"], 0.5)

    def test_sector_aggregation_and_concentration_are_hand_calculated(self):
        rows = compute_sector_flows(self.stocks, self.market, self.flows)
        latest = next(r for r in rows if r["date"] == "2026-08-28" and r["institution"] == "foreign")
        self.assertAlmostEqual(latest["flow_5d"], 12.5 / 100)
        self.assertEqual(latest["breadth_5d"], 0.5)
        self.assertAlmostEqual(latest["top1_concentration_5d"], 150 / 175)
        self.assertEqual(latest["top3_concentration_5d"], 1.0)

    def test_sector_combined_ratio_adds_foreign_and_trust_net(self):
        rows = compute_sector_flows(
            [{"symbol": "1101", "industry_code": "01", "industry_name": "水泥工業"}],
            [{"date": "2026-08-28", "symbol": "1101", "volume": 100}],
            [{"date": "2026-08-28", "symbol": "1101", "foreign_net": 10, "trust_net": 20}],
        )
        combined = next(r for r in rows if r["institution"] == "combined")
        self.assertEqual(combined["flow_1d"], 0.3)

    def test_custom_group_adds_dealer_net(self):
        rows = compute_stock_flows(
            [{"date": "2026-08-28", "symbol": "1101", "volume": 100}],
            [{"date": "2026-08-28", "symbol": "1101", "foreign_net": 10, "trust_net": 20, "dealer_net": 30}],
            groups=("foreign+dealer",),
        )
        self.assertEqual(rows[0]["foreign+dealer_flow_1d"], 0.4)

    def test_amount_basis_uses_close_price_weighting(self):
        market = [{"date": "2026-08-28", "symbol": "1101", "volume": 100, "close": 10}]
        flows = [{"date": "2026-08-28", "symbol": "1101", "foreign_net": 10}]
        rows = compute_stock_flows(market, flows, groups=("foreign",), basis="amount")
        self.assertEqual(rows[0]["foreign_flow_1d"], 0.1)


if __name__ == "__main__":
    unittest.main()
