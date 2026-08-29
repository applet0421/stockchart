"""Build the single, observation-only payload consumed by the web UI."""

from pathlib import Path

from .storage import read_json, write_json


_SUPPORTED_BASES = {"shares", "amount"}
_METRICS = ("flow_1d", "flow_5d", "flow_20d", "breadth_5d", "top1_concentration_5d", "top3_concentration_5d", "stock_count_5d")
_INSTITUTION_FLOW_PREFIX = {"foreign": "foreign", "trust": "trust", "dealer": "dealer", "combined": "combined", "all": "all"}


def _validate_basis(basis, quality):
    if basis not in _SUPPORTED_BASES:
        raise ValueError(f"unsupported basis: {basis}")
    generated_basis = quality.get("basis")
    if generated_basis and generated_basis != basis:
        raise ValueError(f"payload basis {basis} does not match generated basis {generated_basis}")


def _validate_model(rotation_rows):
    for row in rotation_rows:
        if row.get("model") not in (None, "A"):
            raise ValueError("only Model A rows are supported")
        if "model_a_x" not in row or "model_a_y" not in row:
            raise ValueError("rotation row is missing Model A coordinates")


def _key(row):
    return row.get("date"), row.get("institution"), row.get("industry_code")


def _latest_rows(sector_rows, rotation_rows, institution):
    rotation_by_key = {_key(row): row for row in rotation_rows if row.get("institution") == institution}
    rows = []
    for sector in sector_rows:
        if sector.get("institution") != institution:
            continue
        rotation = rotation_by_key.get(_key(sector))
        if rotation is None:
            continue
        item = {
            "date": sector.get("date"),
            "institution": institution,
            "industry_code": sector.get("industry_code"),
            "sector": sector.get("sector", rotation.get("industry_name")),
            "industry_name": rotation.get("industry_name", sector.get("sector")),
            "model_a_x": rotation.get("model_a_x"),
            "model_a_y": rotation.get("model_a_y"),
            "model_a_quadrant": rotation.get("model_a_quadrant"),
        }
        item.update({metric: sector.get(metric) for metric in _METRICS})
        rows.append(item)
    return sorted(rows, key=lambda row: (row.get("industry_code") or "", row.get("sector") or ""))


def _rankings(rows):
    rankings = {}
    for metric in _METRICS:
        rankings[metric] = sorted(
            rows,
            key=lambda row: (row.get(metric) is not None, row.get(metric) or 0),
            reverse=True,
        )
    return rankings


def _stock_rows(stock_flow_rows, stock_master_rows, *, institution, latest_only=False):
    """Normalize stock-level rows for the frontend without filling missing windows."""
    master = {row.get("symbol"): row for row in stock_master_rows if row.get("symbol")}
    prefix = _INSTITUTION_FLOW_PREFIX.get(institution, "all")
    grouped = {}
    latest_date = max((row.get("date") for row in stock_flow_rows if row.get("date")), default=None)
    for source in stock_flow_rows:
        symbol = source.get("symbol")
        mapping = master.get(symbol, {})
        industry_code = mapping.get("industry_code")
        if not symbol or not industry_code or not source.get("date"):
            continue
        if latest_only and source.get("date") != latest_date:
            continue
        flow_1d = source.get(f"{prefix}_flow_1d")
        flow_5d = source.get(f"{prefix}_flow_5d")
        flow_20d = source.get(f"{prefix}_flow_20d")
        key = (source.get("date"), industry_code)
        grouped.setdefault(key, []).append((source, mapping, flow_1d, flow_5d, flow_20d))
    rows = []
    for (date, industry_code), items in grouped.items():
        denominator = sum(abs(item[3]) for item in items if item[3] is not None)
        for source, mapping, flow_1d, flow_5d, flow_20d in items:
            rows.append({
                "date": date,
                "institution": institution,
                "symbol": source.get("symbol"),
                "name": source.get("name") or mapping.get("name"),
                "industry_code": industry_code,
                "industry_name": mapping.get("industry_name"),
                "flow_1d": flow_1d,
                "flow_5d": flow_5d,
                "flow_20d": flow_20d,
                "foreign_net": source.get("foreign_net"),
                "trust_net": source.get("trust_net"),
                "dealer_net": source.get("dealer_net"),
                "contribution_share": (abs(flow_5d) / denominator) if flow_5d is not None and denominator else None,
                "source_missing": bool(source.get("source_missing")),
            })
    return sorted(rows, key=lambda row: (row.get("date") or "", row.get("industry_code") or "", row.get("symbol") or ""))


def build_model_a_payload(sector_rows, rotation_rows, institution_rows, quality, *, institution="all", basis="shares", stock_flow_rows=None, stock_master_rows=None):
    """Return a stable frontend payload without recomputing any source metric."""

    _validate_basis(basis, quality)
    _validate_model(rotation_rows)
    available_institutions = sorted({row.get("institution") for row in sector_rows if row.get("institution")} | {institution})
    latest_by_institution = {
        name: _latest_rows(sector_rows, rotation_rows, name)
        for name in available_institutions
    }
    latest = latest_by_institution.get(institution, [])
    stock_flow_rows = stock_flow_rows or []
    stock_master_rows = stock_master_rows or []
    stocks_by_sector = {name: _stock_rows(stock_flow_rows, stock_master_rows, institution=name, latest_only=True) for name in available_institutions}
    selected_history_rows = _stock_rows(stock_flow_rows, stock_master_rows, institution=institution)
    stock_history_compact = [{"s": row["symbol"], "d": row["date"], "v": row["flow_5d"], "m": row["source_missing"]} for row in selected_history_rows]
    dates = sorted({row.get("date") for row in sector_rows if row.get("date")})
    meta = {
        "model": "A",
        "x_metric": "flow_5d",
        "y_metric": "flow_1d",
        "basis": basis,
        "date_min": quality.get("date_min") or (dates[0] if dates else None),
        "date_max": quality.get("date_max") or (dates[-1] if dates else None),
        "generated_at": quality.get("generated_at"),
    }
    return {
        "meta": meta,
        "latest": latest,
        "history": [row for row in rotation_rows if row.get("institution") == institution],
        "rankings": _rankings(latest),
        "latest_by_institution": latest_by_institution,
        "history_by_institution": {
            name: [row for row in rotation_rows if row.get("institution") == name]
            for name in available_institutions
        },
        "rankings_by_institution": {name: _rankings(rows) for name, rows in latest_by_institution.items()},
        "quality": dict(quality),
        "institutions": available_institutions,
        "institution_comparison": list(institution_rows),
        "topic_mapping": {"version": "sector-v1", "source": "existing validated industry assignments", "assignments": [{"industry_code": row.get("industry_code"), "industry_name": row.get("industry_name")} for row in latest]},
        "stocks_by_sector": stocks_by_sector,
        "stock_history_compact": stock_history_compact,
    }


def write_model_a_payload(output_dir: Path, payload: dict) -> Path:
    path = Path(output_dir) / "model-a.json"
    write_json(path, payload)
    return path


def export_web_data(outputs_dir: Path = Path("outputs"), web_data_dir: Path = Path("web/data"), *, basis=None):
    outputs_dir = Path(outputs_dir)
    manifest = read_json(outputs_dir / "run_manifest.json")
    summary_path = outputs_dir.parent / "data" / "processed" / "run.summary.json"
    summary = read_json(summary_path) if summary_path.exists() else {}
    quality = {**summary, **manifest}
    selected_basis = basis or quality.get("basis", "shares")
    rotation_path = outputs_dir / "rotation_model_comparison.json"
    rotation_rows = read_json(rotation_path) if rotation_path.exists() else read_json(outputs_dir / "latest_rotation_model_comparison.json")
    payload = build_model_a_payload(
        read_json(outputs_dir / "latest_sector_observation.json"),
        rotation_rows,
        read_json(outputs_dir / "latest_institution_comparison.json"),
        quality,
        basis=selected_basis,
        stock_flow_rows=read_json(outputs_dir.parent / "data" / "processed" / "stock_flow.json"),
        stock_master_rows=read_json(outputs_dir.parent / "data" / "processed" / "stocks.json"),
    )
    return write_model_a_payload(web_data_dir, payload)
