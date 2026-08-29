from collections import Counter, defaultdict


def build_model_comparison(rows):
    fields = ("date", "institution", "industry_code", "industry_name",
              "model_a_x", "model_a_y", "model_a_quadrant",
              "model_b_x", "model_b_y", "model_b_quadrant")
    return [{field: row.get(field) for field in fields} for row in rows]


def quadrant(x, y):
    if x >= 0 and y >= 0:
        return "ACCUMULATING"
    if x >= 0 and y < 0:
        return "WEAKENING"
    if x < 0 and y >= 0:
        return "REVERSING"
    return "DISTRIBUTING"


def build_rotation_rows(sector_rows):
    result = []
    for row in sector_rows:
        if any(row.get(key) is None for key in ("flow_1d", "flow_5d", "flow_20d")):
            continue
        output = dict(row)
        output.update({
            "model_a_x": row["flow_5d"], "model_a_y": row["flow_1d"],
            "model_a_quadrant": quadrant(row["flow_5d"], row["flow_1d"]),
            "model_b_x": row["flow_20d"], "model_b_y": row["flow_5d"],
            "model_b_quadrant": quadrant(row["flow_20d"], row["flow_5d"]),
        })
        result.append(output)
    return result


def build_transition_matrix(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["institution"], row["industry_code"])].append(row)
    counts = Counter()
    totals = Counter()
    for (institution, _), values in grouped.items():
        values.sort(key=lambda row: row["date"])
        for previous, current in zip(values, values[1:]):
            for model in ("A", "B"):
                source = previous[f"model_{model.lower()}_quadrant"]
                target = current[f"model_{model.lower()}_quadrant"]
                counts[(institution, model, source, target)] += 1
                totals[(institution, model, source)] += 1
    return [{"institution": i, "model": m, "from_quadrant": f, "to_quadrant": t, "count": count, "probability": count / totals[(i, m, f)]}
            for (i, m, f, t), count in sorted(counts.items())]


def build_signal_outcomes(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["institution"], row["industry_code"])].append(row)
    result = []
    for (institution, _), values in grouped.items():
        values.sort(key=lambda row: row["date"])
        for index, row in enumerate(values):
            for model in ("A", "B"):
                q = row[f"model_{model.lower()}_quadrant"]
                if q not in {"REVERSING", "WEAKENING"} or index + 5 >= len(values):
                    continue
                future3 = values[index + 1:index + 4]
                positive = q == "REVERSING"
                direction_rate = sum((item["flow_1d"] > 0) == positive for item in future3) / 3
                future5 = values[index + 5]["flow_5d"]
                result.append({
                    "date": row["date"], "industry_code": row["industry_code"], "industry_name": row["industry_name"],
                    "institution": institution, "model": model, "signal": q,
                    "future_3d_direction_rate": direction_rate, "persistent_3d": direction_rate >= 2 / 3,
                    "future_5d_flow": future5, "success_5d": future5 > 0 if positive else future5 < 0,
                })
    return result
