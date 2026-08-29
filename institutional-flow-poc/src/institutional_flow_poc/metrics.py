from collections import defaultdict, deque


WINDOWS = (1, 5, 20)
DEFAULT_GROUPS = ("foreign", "trust", "dealer", "combined", "all")


def _group_net(row, group):
    if group == "all":
        members = ("foreign", "trust", "dealer")
    elif group == "combined":
        members = ("foreign", "trust")
    else:
        members = tuple(group.split("+"))
    return sum(row.get(f"{member}_net", 0) for member in members)


def _ratio(net, volume):
    return net / volume if volume else None


def _basis_values(row, net, basis):
    if basis == "shares":
        return net, row.get("volume")
    close = row.get("close")
    volume = row.get("volume")
    if close is None or volume is None:
        return None, None
    return net * close, volume * close


def _joined_series(market_rows, flow_rows):
    flow = {(row["date"], row["symbol"]): row for row in flow_rows}
    grouped = defaultdict(list)
    for market in market_rows:
        item = flow.get((market["date"], market["symbol"]))
        if item is not None and market.get("volume") is not None:
            grouped[market["symbol"]].append({**market, **item})
    for values in grouped.values():
        values.sort(key=lambda row: row["date"])
    return grouped


def compute_stock_flows(market_rows, flow_rows, groups=DEFAULT_GROUPS, basis="shares"):
    result = []
    for symbol, values in _joined_series(market_rows, flow_rows).items():
        history = deque(maxlen=20)
        for row in values:
            history.append(row)
            output = dict(row)
            for institution in groups:
                for window in WINDOWS:
                    selected = list(history)[-window:]
                    values = [_basis_values(item, _group_net(item, institution), basis) for item in selected]
                    numerators = [item[0] for item in values if item[0] is not None]
                    denominators = [item[1] for item in values if item[1] is not None]
                    output[f"{institution}_flow_{window}d"] = _ratio(sum(numerators), sum(denominators)) if len(selected) == window and len(values) == len(numerators) else None
            result.append(output)
    return sorted(result, key=lambda row: (row["date"], row["symbol"]))


def compute_sector_flows(stocks, market_rows, flow_rows, groups=DEFAULT_GROUPS, basis="shares"):
    stock_map = {row["symbol"]: row for row in stocks}
    series = _joined_series(market_rows, flow_rows)
    dates = sorted({row["date"] for row in market_rows})
    by_key = {(row["date"], row["symbol"]): index for symbol, values in series.items() for index, row in enumerate(values)}
    sectors = defaultdict(list)
    for symbol in series:
        if symbol in stock_map:
            sectors[stock_map[symbol]["industry_code"]].append(symbol)
    result = []
    for day in dates:
        for code, symbols in sectors.items():
            for institution in groups:
                output = {"date": day, "industry_code": code, "industry_name": stock_map[symbols[0]]["industry_name"], "institution": institution}
                for window in WINDOWS:
                    stock_nets, total_volume = [], 0
                    for symbol in symbols:
                        index = by_key.get((day, symbol))
                        if index is None or index + 1 < window:
                            continue
                        selected = series[symbol][index + 1 - window:index + 1]
                        if len(selected) != window:
                            continue
                        selected_values = [_basis_values(row, _group_net(row, institution), basis) for row in selected]
                        if any(value[0] is None for value in selected_values):
                            continue
                        stock_nets.append(sum(value[0] for value in selected_values))
                        total_volume += sum(value[1] for value in selected_values)
                    absolute = sum(abs(value) for value in stock_nets)
                    ranked = sorted((abs(value) for value in stock_nets), reverse=True)
                    output[f"flow_{window}d"] = _ratio(sum(stock_nets), total_volume) if stock_nets else None
                    output[f"breadth_{window}d"] = sum(value > 0 for value in stock_nets) / len(stock_nets) if stock_nets else None
                    output[f"top1_concentration_{window}d"] = sum(ranked[:1]) / absolute if absolute else 0.0 if stock_nets else None
                    output[f"top3_concentration_{window}d"] = sum(ranked[:3]) / absolute if absolute else 0.0 if stock_nets else None
                    output[f"stock_count_{window}d"] = len(stock_nets)
                result.append(output)
    return sorted(result, key=lambda row: (row["date"], row["industry_code"], row["institution"]))
