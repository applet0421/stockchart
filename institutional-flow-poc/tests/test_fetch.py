import unittest
from urllib.error import HTTPError

from institutional_flow_poc.fetch import TwseAccessBlocked, weekday_candidates, request_json


class _Response:
    def __init__(self, body):
        self.body = body
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return self.body


class FetchTests(unittest.TestCase):
    def test_request_retries_and_returns_attempt_count(self):
        calls = []
        def opener(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1:
                raise OSError("temporary")
            return _Response(b'{"stat":"OK"}')
        payload, metadata = request_json("https://example.test/data", {"date": "20260828"}, opener=opener, sleep=lambda _: None)
        self.assertEqual(payload, {"stat": "OK"})
        self.assertEqual(metadata["attempts"], 2)

    def test_security_redirect_stops_without_retries(self):
        calls = []
        def opener(request, timeout):
            calls.append(request.full_url)
            raise HTTPError(request.full_url, 307, "security block", {}, None)
        with self.assertRaises(TwseAccessBlocked):
            request_json("https://www.twse.com.tw/data", opener=opener, sleep=lambda _: None)
        self.assertEqual(len(calls), 1)

    def test_candidate_dates_skip_weekends(self):
        self.assertEqual(weekday_candidates("2026-08-31", 4), ["2026-08-31", "2026-08-28"])


if __name__ == "__main__":
    unittest.main()
