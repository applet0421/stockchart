import unittest

from institutional_flow_poc.parsers import align_flow_to_market, parse_companies, parse_market, parse_t86


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.universe = {"1101", "2330"}

    def test_company_parser_keeps_four_digit_common_stock_universe(self):
        payload = [
            {"出表日期": "1150828", "公司代號": "1101", "公司簡稱": "台泥", "產業別": "01", "上市日期": "19620209", "已發行普通股數或TDR原股發行股數": "7,523,181,742"},
            {"出表日期": "1150828", "公司代號": "00919", "公司簡稱": "ETF", "產業別": "00"},
        ]
        rows = parse_companies(payload)
        self.assertEqual(rows, [{
            "symbol": "1101", "name": "台泥", "industry_code": "01",
            "industry_name": "水泥工業", "market": "TWSE", "listed_date": "1962-02-09",
            "issued_common_shares": 7523181742, "source_report_date": "2026-08-28",
        }])

    def test_market_parser_selects_daily_table_and_normalizes_numbers(self):
        payload = {"stat": "OK", "date": "20260828", "tables": [{
            "title": "115年08月28日 每日收盤行情(全部(不含權證))",
            "fields": ["證券代號", "證券名稱", "成交股數", "成交筆數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌(+/-)", "漲跌價差", "最後揭示買價", "最後揭示買量", "最後揭示賣價", "最後揭示賣量", "本益比"],
            "data": [["1101", "台泥", "1,000", "20", "50,000", "50.0", "51", "49", "--", "+", "1", "", "", "", "", "15.2"], ["0050", "ETF", "9", "1", "9", "1", "1", "1", "1", "+", "0", "", "", "", "", "0"]],
        }]}
        rows = parse_market("2026-08-28", payload, self.universe)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["volume"], 1000)
        self.assertIsNone(rows[0]["close"])

    def test_t86_parser_maps_foreign_and_trust(self):
        payload = {"stat": "OK", "date": "20260828", "fields": ["證券代號", "證券名稱", "外陸資買進股數(不含外資自營商)", "外陸資賣出股數(不含外資自營商)", "外陸資買賣超股數(不含外資自營商)", "外資自營商買進股數", "外資自營商賣出股數", "外資自營商買賣超股數", "投信買進股數", "投信賣出股數", "投信買賣超股數"], "data": [["2330", "台積電", "1,200", "200", "1,000", "0", "0", "0", "500", "100", "400"]]}
        self.assertEqual(parse_t86("2026-08-28", payload, self.universe)[0]["trust_net"], 400)
        self.assertEqual(parse_t86("2026-08-28", payload, self.universe)[0]["dealer_net"], 0)

    def test_missing_t86_symbol_is_zero_filled_without_hiding_source_gap(self):
        market = [{"date": "2026-08-28", "symbol": "1101", "name": "台泥"}]
        rows = align_flow_to_market(market, [])
        self.assertEqual(rows[0]["foreign_net"], 0)
        self.assertEqual(rows[0]["trust_net"], 0)
        self.assertTrue(rows[0]["source_missing"])


if __name__ == "__main__":
    unittest.main()
