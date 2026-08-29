import html
from collections import defaultdict


def render_rotation_svg(rows, institution, model="B"):
    key_x, key_y = f"model_{model.lower()}_x", f"model_{model.lower()}_y"
    values = [abs(row[key]) for row in rows for key in (key_x, key_y) if row.get(key) is not None]
    limit = max(values or [0.01]) * 1.15
    width, height, pad = 1000, 760, 70
    def point(x, y):
        return pad + (x + limit) / (2 * limit) * (width - 2 * pad), height - pad - (y + limit) / (2 * limit) * (height - 2 * pad)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["industry_code"]].append(row)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#0b1020"/>',
             f'<text x="{pad}" y="35" fill="white" font-size="22">{html.escape(institution.title())} Rotation — Model {model}</text>',
             f'<line x1="{width/2}" y1="{pad}" x2="{width/2}" y2="{height-pad}" stroke="#65708a"/>',
             f'<line x1="{pad}" y1="{height/2}" x2="{width-pad}" y2="{height/2}" stroke="#65708a"/>']
    colors = ("#5eead4", "#fbbf24", "#60a5fa", "#f472b6", "#a78bfa")
    for index, (_, trail) in enumerate(sorted(grouped.items())):
        trail = sorted(trail, key=lambda row: row["date"])[-20:]
        points = [point(row[key_x], row[key_y]) for row in trail]
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        color = colors[index % len(colors)]
        parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.65"/>')
        x, y = points[-1]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        parts.append(f'<text x="{x+6:.1f}" y="{y-6:.1f}" fill="{color}" font-size="11">{html.escape(trail[-1]["industry_name"])}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def render_model_comparison_svg(rows):
    latest = max((row["date"] for row in rows), default="")
    current = [row for row in rows if row.get("date") == latest]
    width, height = 1400, 760
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#0b1020"/>', '<text x="40" y="35" fill="white" font-size="22">Rotation Model Comparison — {html.escape(latest)}</text>']
    for panel, model in enumerate(("a", "b")):
        left, top, panel_w, panel_h = 40 + panel * 680, 70, 620, 640
        vals = [abs(row.get(f"model_{model}_{axis}") or 0) for row in current for axis in ("x", "y")]
        limit = max(vals or [0.01]) * 1.15
        def point(x, y):
            return left + 40 + (x + limit) / (2 * limit) * (panel_w - 80), top + panel_h - 40 - (y + limit) / (2 * limit) * (panel_h - 80)
        parts.append(f'<text x="{left+40}" y="{top+25}" fill="white" font-size="18">Model {model.upper()}</text>')
        cx, cy = left + panel_w / 2, top + panel_h / 2
        parts.extend([f'<line x1="{cx}" y1="{top+40}" x2="{cx}" y2="{top+panel_h-40}" stroke="#65708a"/>', f'<line x1="{left+40}" y1="{cy}" x2="{left+panel_w-40}" y2="{cy}" stroke="#65708a"/>'])
        for row in current:
            x, y = row.get(f"model_{model}_x"), row.get(f"model_{model}_y")
            if x is None or y is None:
                continue
            px, py = point(x, y)
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#5eead4"/>')
            parts.append(f'<text x="{px+6:.1f}" y="{py-6:.1f}" fill="#d1d5db" font-size="11">{html.escape(row.get("industry_name", ""))}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def render_basis_comparison_svg(rows, primary_basis, compare_basis):
    latest = max((row["date"] for row in rows), default="")
    current = [row for row in rows if row.get("date") == latest]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900"><rect width="100%" height="100%" fill="#0b1020"/>', f'<text x="30" y="35" fill="white" font-size="22">Basis comparison: {html.escape(primary_basis)} vs {html.escape(compare_basis)} — {html.escape(latest)}</text>', '<text x="30" y="62" fill="#cbd5e1" font-size="13">amount = net shares × daily close estimate</text>']
    for index, row in enumerate(current[:20]):
        parts.append(f'<text x="30" y="{95 + index * 36}" fill="#d1d5db" font-size="13">{html.escape(row.get("institution", ""))} / {html.escape(row.get("industry_name", ""))}: {row.get(primary_basis + "_flow_5d")} → {row.get(compare_basis + "_flow_5d")} (Δ {row.get("delta_flow_5d")})</text>')
    parts.append('</svg>')
    return "\n".join(parts)
