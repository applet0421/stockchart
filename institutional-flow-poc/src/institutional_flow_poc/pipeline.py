import math
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

from .config import OUTPUT_ROOT, PROCESSED_ROOT, RAW_ROOT, SOURCE_URLS
from .fetch import TwseAccessBlocked, request_json, weekday_candidates
from .metrics import DEFAULT_GROUPS, compute_sector_flows, compute_stock_flows
from .observation import build_institution_comparison, build_quality_observations, build_sector_observations
from .provenance import build_run_manifest, latest_rows
from .parsers import align_flow_to_market, parse_companies, parse_market, parse_t86
from .quality import validate_day
from .report import evaluate_decision, render_report
from .rotation import build_model_comparison, build_rotation_rows, build_signal_outcomes, build_transition_matrix
from .storage import read_json, write_csv, write_json
from .svg import render_basis_comparison_svg, render_model_comparison_svg, render_rotation_svg


def _now():
    return datetime.now(timezone.utc).isoformat()


def fetch_data(days=120, end_date=None, raw_root=RAW_ROOT, max_calendar_days=240):
    raw_root = Path(raw_root)
    company_payload, company_meta = request_json(SOURCE_URLS["companies"])
    companies = parse_companies(company_payload)
    if not companies:
        raise RuntimeError("TWSE company universe is empty")
    write_json(raw_root / "companies.json", company_payload)
    universe = {row["symbol"] for row in companies}
    cursor = date.fromisoformat(end_date) if end_date else date.today()
    successes, failures = [], []
    cached = set()
    for market_file in sorted((raw_root / "market").glob("*.json")):
        day = market_file.stem
        flow_file = raw_root / "t86" / market_file.name
        if not flow_file.exists() or day > cursor.isoformat():
            continue
        try:
            market_rows = parse_market(day, read_json(market_file), universe)
            flow_rows = parse_t86(day, read_json(flow_file), universe)
            quality = validate_day(day, market_rows, flow_rows)
            if quality["success"]:
                cached.add(day)
                successes.append({"date": day, "market": {"source": "cache"}, "t86": {"source": "cache"}, "quality": quality})
        except Exception:
            continue
    successes.sort(key=lambda item: item["date"], reverse=True)
    successes = successes[:days]
    blocked = None
    for day in weekday_candidates(cursor.isoformat(), max_calendar_days):
        if len(successes) >= days:
            break
        if day in cached:
            continue
        compact = day.replace("-", "")
        try:
            market_payload, market_meta = request_json(SOURCE_URLS["market"], {"date": compact, "type": "ALLBUT0999", "response": "json"})
            flow_payload, flow_meta = request_json(SOURCE_URLS["t86"], {"date": compact, "selectType": "ALL", "response": "json"})
            market_rows = parse_market(day, market_payload, universe)
            flow_rows = parse_t86(day, flow_payload, universe)
            quality = validate_day(day, market_rows, flow_rows)
            if not quality["success"]:
                failures.append({"date": day, "reason": "not_complete_trading_day", "market_stat": market_payload.get("stat"), "t86_stat": flow_payload.get("stat")})
                continue
            write_json(raw_root / "market" / f"{day}.json", market_payload)
            write_json(raw_root / "t86" / f"{day}.json", flow_payload)
            successes.append({"date": day, "market": market_meta, "t86": flow_meta, "quality": quality})
        except TwseAccessBlocked as error:
            blocked = str(error)
            failures.append({"date": day, "reason": blocked})
            break
        except Exception as error:
            failures.append({"date": day, "reason": f"{type(error).__name__}: {error}"})
    successes.sort(key=lambda item: item["date"])
    manifest = {
        "generated_at": _now(), "company_source": company_meta, "required_days": days,
        "successful_days": len(successes), "success": len(successes) == days,
        "success_records": successes, "failure_records": failures, "blocked": blocked,
    }
    write_json(raw_root / "fetch_manifest.json", manifest)
    if not manifest["success"]:
        raise RuntimeError(f"only {len(successes)} complete trading days found; required {days}")
    return manifest


def process_data(raw_root=RAW_ROOT, processed_root=PROCESSED_ROOT):
    raw_root, processed_root = Path(raw_root), Path(processed_root)
    manifest = read_json(raw_root / "fetch_manifest.json")
    companies = parse_companies(read_json(raw_root / "companies.json"))
    universe = {row["symbol"] for row in companies}
    market_rows, flow_rows, checks = [], [], []
    for record in manifest["success_records"]:
        day = record["date"]
        market = parse_market(day, read_json(raw_root / "market" / f"{day}.json"), universe)
        flow = parse_t86(day, read_json(raw_root / "t86" / f"{day}.json"), universe)
        checks.append(validate_day(day, market, flow))
        market_rows.extend(market)
        flow_rows.extend(align_flow_to_market(market, flow))
    duplicate_count = sum(len(row["duplicate_market"]) + len(row["duplicate_flow"]) for row in checks)
    arithmetic_count = sum(len(row["foreign_arithmetic_failures"]) + len(row["trust_arithmetic_failures"]) for row in checks)
    summary = {
        "generated_at": _now(), "required_days": manifest["required_days"], "successful_days": len(checks),
        "stock_count": len(companies), "market_row_count": len(market_rows), "flow_row_count": len(flow_rows),
        "duplicate_failure_count": duplicate_count, "arithmetic_failure_count": arithmetic_count,
        "missing_in_market_count": sum(len(row["missing_in_market"]) for row in checks),
        "missing_in_flow_count": sum(len(row["missing_in_flow"]) for row in checks),
        "success": len(checks) == manifest["required_days"] and all(row["success"] for row in checks),
        "failure": [row for row in checks if not row["success"]], "per_day": checks,
    }
    write_json(processed_root / "stocks.json", companies)
    write_json(processed_root / "daily_market.json", market_rows)
    write_json(processed_root / "institutional_flow.json", flow_rows)
    write_json(processed_root / "data_quality.json", summary)
    write_json(processed_root / "run.summary.json", {key: value for key, value in summary.items() if key != "per_day"})
    write_csv(processed_root / "stocks.csv", companies)
    write_csv(processed_root / "daily_market.csv", market_rows)
    write_csv(processed_root / "institutional_flow.csv", flow_rows)
    quality_observations = build_quality_observations(summary)
    write_json(processed_root / "quality_observation_daily.json", quality_observations)
    write_csv(processed_root / "quality_observation_daily.csv", quality_observations)
    return summary


def analyze_data(processed_root=PROCESSED_ROOT, output_root=OUTPUT_ROOT, groups=DEFAULT_GROUPS, basis="shares", compare_basis=None):
    processed_root, output_root = Path(processed_root), Path(output_root)
    stocks = read_json(processed_root / "stocks.json")
    market = read_json(processed_root / "daily_market.json")
    flows = read_json(processed_root / "institutional_flow.json")
    stock_rows = compute_stock_flows(market, flows, groups=groups, basis=basis)
    sector_rows = compute_sector_flows(stocks, market, flows, groups=groups, basis=basis)
    rotation_rows = build_rotation_rows(sector_rows)
    model_comparison = build_model_comparison(rotation_rows)
    basis_comparison = []
    if compare_basis and compare_basis != basis:
        alternate = build_rotation_rows(compute_sector_flows(stocks, market, flows, groups=groups, basis=compare_basis))
        alternate_index = {(row["date"], row["institution"], row["industry_code"]): row for row in alternate}
        for row in rotation_rows:
            other = alternate_index.get((row["date"], row["institution"], row["industry_code"]))
            if other:
                basis_comparison.append({"date": row["date"], "institution": row["institution"], "industry_code": row["industry_code"], "industry_name": row["industry_name"], f"{basis}_flow_5d": row["flow_5d"], f"{compare_basis}_flow_5d": other["flow_5d"], "delta_flow_5d": other["flow_5d"] - row["flow_5d"] if other["flow_5d"] is not None and row["flow_5d"] is not None else None})
    transitions = build_transition_matrix(rotation_rows)
    outcomes = build_signal_outcomes(rotation_rows)
    foreign = [row for row in rotation_rows if row["institution"] == "foreign"]
    trust = [row for row in rotation_rows if row["institution"] == "trust"]
    combined = [row for row in rotation_rows if row["institution"] == "combined"]
    write_json(processed_root / "stock_flow.json", stock_rows)
    write_json(processed_root / "sector_flow.json", sector_rows)
    write_csv(processed_root / "stock_flow.csv", stock_rows)
    from .storage import _atomic_text
    write_csv(processed_root / "sector_flow.csv", sector_rows)
    write_json(output_root / "rotation_model_comparison.json", model_comparison)
    write_csv(output_root / "rotation_model_comparison.csv", model_comparison)
    if basis_comparison:
        write_json(output_root / "basis_comparison.json", basis_comparison)
        write_csv(output_root / "basis_comparison.csv", basis_comparison)
        write_json(output_root / "latest_basis_comparison.json", latest_rows(basis_comparison))
        write_csv(output_root / "latest_basis_comparison.csv", latest_rows(basis_comparison))
        _atomic_text(output_root / "basis_comparison.svg", render_basis_comparison_svg(basis_comparison, basis, compare_basis))
    write_json(output_root / "latest_rotation_model_comparison.json", latest_rows(model_comparison))
    write_csv(output_root / "latest_rotation_model_comparison.csv", latest_rows(model_comparison))
    _atomic_text(output_root / "rotation_model_comparison.svg", render_model_comparison_svg(model_comparison))
    sector_observations = build_sector_observations(sector_rows)
    institution_comparison = build_institution_comparison(sector_rows)
    write_json(output_root / "sector_observation_daily.json", sector_observations)
    write_csv(output_root / "sector_observation_daily.csv", sector_observations)
    write_json(output_root / "institution_comparison_daily.json", institution_comparison)
    write_csv(output_root / "institution_comparison_daily.csv", institution_comparison)
    latest_sector = latest_rows(sector_observations)
    latest_comparison = latest_rows(institution_comparison)
    write_json(output_root / "latest_sector_observation.json", latest_sector)
    write_csv(output_root / "latest_sector_observation.csv", latest_sector)
    write_json(output_root / "latest_institution_comparison.json", latest_comparison)
    write_csv(output_root / "latest_institution_comparison.csv", latest_comparison)
    generated_at = _now()
    manifest_files = [output_root / "sector_observation_daily.csv", output_root / "institution_comparison_daily.csv", output_root / "rotation_model_comparison.csv", output_root / "latest_rotation_model_comparison.csv", processed_root / "quality_observation_daily.csv", output_root / "latest_sector_observation.csv", output_root / "latest_institution_comparison.csv"]
    if basis_comparison:
        manifest_files.extend([output_root / "basis_comparison.csv", output_root / "latest_basis_comparison.csv", output_root / "basis_comparison.svg"])
    manifest = build_run_manifest({
        "run_id": generated_at.replace(":", "").replace("+", "Z"), "generated_at": generated_at, "basis": basis,
        "source_urls": SOURCE_URLS, "date_min": min(row["date"] for row in sector_rows),
        "date_max": max(row["date"] for row in sector_rows),
        "basis": basis, "compare_basis": compare_basis,
        "row_counts": {"sector_observation_daily": len(sector_observations), "institution_comparison_daily": len(institution_comparison), "rotation_model_comparison": len(model_comparison), "quality_observation_daily": len(build_quality_observations(read_json(processed_root / "data_quality.json")))},
    }, manifest_files)
    write_json(output_root / "run_manifest.json", manifest)
    for group in groups:
        name = group.replace("+", "_")
        rows = [row for row in rotation_rows if row["institution"] == group]
        write_json(output_root / f"{name}_rotation.json", rows)
        write_csv(output_root / f"{name}_rotation.csv", rows)
        if group == "foreign+trust":
            write_json(output_root / "combined_rotation.json", rows)
            write_csv(output_root / "combined_rotation.csv", rows)
    for name, rows in (("transition_matrix", transitions), ("signal_outcomes", outcomes)):
        write_json(output_root / f"{name}.json", rows)
        write_csv(output_root / f"{name}.csv", rows)
    return {"stock_rows": len(stock_rows), "sector_rows": len(sector_rows), "rotation_rows": len(rotation_rows), "transition_rows": len(transitions), "outcome_rows": len(outcomes)}


def _pearson(pairs):
    if len(pairs) < 2:
        return 0.0
    xs, ys = zip(*pairs)
    mx, my = mean(xs), mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in pairs)
    denominator = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return numerator / denominator if denominator else 0.0


def _pattern_difference(rotation_rows):
    latest = max(row["date"] for row in rotation_rows)
    current = [row for row in rotation_rows if row["date"] == latest]
    by_inst = {inst: {row["industry_code"]: row for row in current if row["institution"] == inst} for inst in ("foreign", "trust")}
    top = {inst: set(sorted(rows, key=lambda code: by_inst[inst][code]["model_b_y"], reverse=True)[:5]) for inst, rows in ((inst, list(by_inst[inst])) for inst in by_inst)}
    union = top["foreign"] | top["trust"]
    pairs = [(by_inst["foreign"][code]["model_b_y"], by_inst["trust"][code]["model_b_y"]) for code in by_inst["foreign"].keys() & by_inst["trust"].keys()]
    return {"date": latest, "top5_overlap": len(top["foreign"] & top["trust"]) / len(union) if union else 0.0, "model_b_coordinate_correlation": _pearson(pairs)}


def report_data(processed_root=PROCESSED_ROOT, output_root=OUTPUT_ROOT):
    processed_root, output_root = Path(processed_root), Path(output_root)
    quality = read_json(processed_root / "data_quality.json")
    sector = read_json(processed_root / "sector_flow.json")
    foreign = read_json(output_root / "foreign_rotation.json")
    trust = read_json(output_root / "trust_rotation.json")
    combined = read_json(output_root / "combined_rotation.json")
    dealer = read_json(output_root / "dealer_rotation.json")
    all_institutions = read_json(output_root / "all_rotation.json")
    outcomes = read_json(output_root / "signal_outcomes.json")
    rotation = foreign + trust
    pattern = _pattern_difference(rotation)
    decision = evaluate_decision(quality, outcomes, sector, pattern)
    groups = defaultdict(list)
    for row in outcomes:
        groups[(row["institution"], row["model"])].append(row)
    outcome_summary = [{"institution": key[0], "model": key[1], "count": len(rows), "success_rate": mean(bool(row["success_5d"]) for row in rows), "persistence_rate": mean(bool(row["persistent_3d"]) for row in rows)} for key, rows in sorted(groups.items())]
    write_json(output_root / "decision.json", {"generated_at": _now(), **decision, "pattern_difference": pattern, "outcome_summary": outcome_summary})
    (output_root).mkdir(parents=True, exist_ok=True)
    from .storage import _atomic_text
    _atomic_text(output_root / "foreign_rotation_map.svg", render_rotation_svg(foreign, "foreign", "B"))
    _atomic_text(output_root / "trust_rotation_map.svg", render_rotation_svg(trust, "trust", "B"))
    _atomic_text(output_root / "combined_rotation_map.svg", render_rotation_svg(combined, "foreign_plus_trust", "B"))
    _atomic_text(output_root / "dealer_rotation_map.svg", render_rotation_svg(dealer, "dealer", "B"))
    _atomic_text(output_root / "all_rotation_map.svg", render_rotation_svg(all_institutions, "all", "B"))
    _atomic_text(output_root / "decision_report.md", render_report(decision, quality, pattern, outcome_summary, _now()))
    return decision
