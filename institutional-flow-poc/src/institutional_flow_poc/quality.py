from collections import Counter


def _duplicates(rows):
    counts = Counter(row["symbol"] for row in rows)
    return sorted(symbol for symbol, count in counts.items() if count > 1)


def validate_day(request_date, market_rows, flow_rows):
    market_symbols = {row["symbol"] for row in market_rows}
    flow_symbols = {row["symbol"] for row in flow_rows}
    result = {
        "date": request_date,
        "market_row_count": len(market_rows), "flow_row_count": len(flow_rows),
        "duplicate_market": _duplicates(market_rows), "duplicate_flow": _duplicates(flow_rows),
        "foreign_arithmetic_failures": sorted(row["symbol"] for row in flow_rows if row["foreign_buy"] - row["foreign_sell"] != row["foreign_net"]),
        "trust_arithmetic_failures": sorted(row["symbol"] for row in flow_rows if row["trust_buy"] - row["trust_sell"] != row["trust_net"]),
        "missing_in_market": sorted(flow_symbols - market_symbols),
        "missing_in_flow": sorted(market_symbols - flow_symbols),
    }
    result["success"] = bool(market_rows and flow_rows) and not any(result[key] for key in (
        "duplicate_market", "duplicate_flow", "foreign_arithmetic_failures", "trust_arithmetic_failures"
    ))
    return result
