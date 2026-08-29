from collections import defaultdict


SECTOR_FIELDS = (
    "date", "institution", "industry_code", "sector", "flow_1d", "flow_5d", "flow_20d",
    "breadth_5d", "top1_concentration_5d", "top3_concentration_5d", "stock_count_5d",
)


def build_sector_observations(sector_rows):
    result = []
    for row in sector_rows:
        item = {field: row.get(field) for field in SECTOR_FIELDS}
        item["sector"] = row.get("industry_name")
        result.append(item)
    return result


def build_institution_comparison(sector_rows):
    grouped = defaultdict(dict)
    names = {}
    for row in sector_rows:
        key = (row["date"], row["industry_code"])
        grouped[key][row["institution"]] = row
        names[key] = row["industry_name"]
    result = []
    for (day, code), institutions in sorted(grouped.items()):
        foreign, trust = institutions.get("foreign", {}), institutions.get("trust", {})
        item = {
            "date": day, "sector": names[(day, code)], "industry_code": code,
            "foreign_flow_5d": foreign.get("flow_5d"), "trust_flow_5d": trust.get("flow_5d"),
            "foreign_breadth_5d": foreign.get("breadth_5d"), "trust_breadth_5d": trust.get("breadth_5d"),
            "foreign_top3_concentration_5d": foreign.get("top3_concentration_5d"),
            "trust_top3_concentration_5d": trust.get("top3_concentration_5d"),
        }
        for group in ("dealer", "foreign+trust", "all"):
            row = institutions.get(group, {})
            item.update({f"{group}_flow_5d": row.get("flow_5d"), f"{group}_breadth_5d": row.get("breadth_5d"), f"{group}_top3_concentration_5d": row.get("top3_concentration_5d")})
        combined = institutions.get("combined", institutions.get("foreign+trust", {}))
        item.update({"combined_flow_5d": combined.get("flow_5d"), "combined_breadth_5d": combined.get("breadth_5d"), "combined_top3_concentration_5d": combined.get("top3_concentration_5d")})
        result.append(item)
    return result


def build_quality_observations(quality):
    result = []
    for row in quality.get("per_day", []):
        result.append({
            "date": row["date"], "market_row_count": row["market_row_count"], "flow_row_count": row["flow_row_count"],
            "missing_in_flow_count": len(row.get("missing_in_flow", [])),
            "duplicate_count": len(row.get("duplicate_market", [])) + len(row.get("duplicate_flow", [])),
            "arithmetic_failure_count": len(row.get("foreign_arithmetic_failures", [])) + len(row.get("trust_arithmetic_failures", [])),
            "success": row.get("success", False),
        })
    return result
