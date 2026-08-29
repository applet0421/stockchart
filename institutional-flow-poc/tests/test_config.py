import unittest

from institutional_flow_poc.config import INDUSTRIES, SOURCE_URLS


class ConfigTests(unittest.TestCase):
    def test_official_sources_and_industries_are_complete(self):
        self.assertEqual(set(SOURCE_URLS), {"companies", "market", "t86"})
        self.assertTrue(all("twse.com.tw" in url for url in SOURCE_URLS.values()))
        self.assertEqual(len(INDUSTRIES), 33)
        self.assertEqual(INDUSTRIES["01"], "水泥工業")
        self.assertEqual(INDUSTRIES["38"], "居家生活")


if __name__ == "__main__":
    unittest.main()
