import re
from datetime import date

from .config import INDUSTRIES


def _number(value, integer=False):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text in {"", "--", "---", "X", "除權", "除息"}:
        return None
    try:
        number = float(text)
        return int(number) if integer else number
    except ValueError:
        return None


def _roc_date(value):
    text = str(value or "").strip()
    if len(text) == 7 and text.isdigit():
        return date(int(text[:3]) + 1911, int(text[3:5]), int(text[5:])).isoformat()
    if len(text) == 8 and text.isdigit():
        return date(int(text[:4]), int(text[4:6]), int(text[6:])).isoformat()
    return ""


def parse_companies(payload):
    rows = []
    for source in payload:
        symbol = str(source.get("公司代號", "")).strip()
        code = str(source.get("產業別", "")).strip().zfill(2)
        if not re.fullmatch(r"\d{4}", symbol) or code not in INDUSTRIES:
            continue
        rows.append({
            "symbol": symbol,
            "name": str(source.get("公司簡稱", "")).strip(),
            "industry_code": code,
            "industry_name": INDUSTRIES[code],
            "market": "TWSE",
            "listed_date": _roc_date(source.get("上市日期")),
            "issued_common_shares": _number(source.get("已發行普通股數或TDR原股發行股數"), True),
            "source_report_date": _roc_date(source.get("出表日期")),
        })
    return sorted(rows, key=lambda row: row["symbol"])


def _records(fields, data):
    return [dict(zip(fields, row)) for row in data]


def parse_market(request_date, payload, universe):
    if payload.get("stat") != "OK" or _roc_date(payload.get("date")) != request_date:
        return []
    table = next((item for item in payload.get("tables", []) if "每日收盤行情" in str(item.get("title"))), None)
    if not table:
        return []
    result = []
    for source in _records(table["fields"], table["data"]):
        symbol = str(source.get("證券代號", "")).strip()
        if symbol not in universe:
            continue
        result.append({
            "date": request_date, "symbol": symbol, "name": str(source.get("證券名稱", "")).strip(),
            "volume": _number(source.get("成交股數"), True), "trade_count": _number(source.get("成交筆數"), True),
            "turnover": _number(source.get("成交金額"), True), "open": _number(source.get("開盤價")),
            "high": _number(source.get("最高價")), "low": _number(source.get("最低價")), "close": _number(source.get("收盤價")),
            "price_change": _number(source.get("漲跌價差")), "pe_ratio": _number(source.get("本益比")),
        })
    return result


def parse_t86(request_date, payload, universe):
    if payload.get("stat") != "OK" or _roc_date(payload.get("date")) != request_date:
        return []
    result = []
    for source in _records(payload.get("fields", []), payload.get("data", [])):
        symbol = str(source.get("證券代號", "")).strip()
        if symbol not in universe:
            continue
        result.append({
            "date": request_date, "symbol": symbol, "name": str(source.get("證券名稱", "")).strip(),
            "foreign_buy": _number(source.get("外陸資買進股數(不含外資自營商)"), True) or 0,
            "foreign_sell": _number(source.get("外陸資賣出股數(不含外資自營商)"), True) or 0,
            "foreign_net": _number(source.get("外陸資買賣超股數(不含外資自營商)"), True) or 0,
            "trust_buy": _number(source.get("投信買進股數"), True) or 0,
            "trust_sell": _number(source.get("投信賣出股數"), True) or 0,
            "trust_net": _number(source.get("投信買賣超股數"), True) or 0,
            "dealer_buy": _number(source.get("自營商買進股數"), True) or 0,
            "dealer_sell": _number(source.get("自營商賣出股數"), True) or 0,
            "dealer_net": _number(source.get("自營商買賣超股數"), True) or 0,
            "source_missing": False,
        })
    return result


def align_flow_to_market(market_rows, flow_rows):
    """Make T86 sparse rows explicit while preserving a source-gap marker."""
    indexed = {(row["date"], row["symbol"]): row for row in flow_rows}
    result = []
    for market in market_rows:
        key = (market["date"], market["symbol"])
        if key in indexed:
            result.append(indexed[key])
        else:
            result.append({
                "date": market["date"], "symbol": market["symbol"], "name": market.get("name", ""),
                "foreign_buy": 0, "foreign_sell": 0, "foreign_net": 0,
                "trust_buy": 0, "trust_sell": 0, "trust_net": 0, "source_missing": True,
                "dealer_buy": 0, "dealer_sell": 0, "dealer_net": 0,
            })
    return result
