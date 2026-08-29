import json
import time
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class TwseAccessBlocked(RuntimeError):
    """TWSE CDN security redirect; retrying immediately makes the block worse."""


def weekday_candidates(end_date, calendar_days):
    end = date.fromisoformat(end_date)
    return [(end - timedelta(days=offset)).isoformat() for offset in range(calendar_days) if (end - timedelta(days=offset)).weekday() < 5]


def request_json(url, params=None, opener=urlopen, sleep=time.sleep, attempts=3, timeout=30):
    target = url + (("?" + urlencode(params)) if params else "")
    errors = []
    for attempt in range(1, attempts + 1):
        try:
            request = Request(target, headers={"User-Agent": "institutional-flow-poc/0.1 (+official TWSE research PoC)", "Accept": "application/json"})
            with opener(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8-sig"))
            return payload, {"url": target, "attempts": attempt, "fetched_at": datetime.now(timezone.utc).isoformat()}
        except HTTPError as error:
            if error.code in {307, 308}:
                raise TwseAccessBlocked(f"TWSE CDN security redirect HTTP {error.code}: {target}") from error
            errors.append(f"HTTPError: {error}")
            if attempt < attempts:
                sleep(0.5 * attempt)
        except Exception as error:
            errors.append(f"{type(error).__name__}: {error}")
            if attempt < attempts:
                sleep(0.5 * attempt)
    raise RuntimeError(f"request failed after {attempts} attempts: {' | '.join(errors)}")
