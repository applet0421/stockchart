from statistics import mean


def evaluate_decision(quality, outcomes, sector_rows, pattern_difference=None):
    """Return descriptive observations only; never infer a trading decision."""
    pattern_difference = pattern_difference or {}
    success_rate = mean(bool(row["success_5d"]) for row in outcomes) if outcomes else 0.0
    persistence_rate = mean(bool(row["persistent_3d"]) for row in outcomes) if outcomes else 0.0
    concentration_values = [row["top3_concentration_5d"] for row in sector_rows if row.get("top3_concentration_5d") is not None]
    return {
        "mode": "observation_only",
        "data_quality": "pass" if quality.get("success") else "incomplete",
        "successful_days": quality.get("successful_days", 0),
        "signal_count": len(outcomes),
        "success_5d_rate": success_rate,
        "persistence_3d_rate": persistence_rate,
        "mean_top3_concentration_5d": mean(concentration_values) if concentration_values else 0.0,
        "foreign_trust_top5_overlap": pattern_difference.get("top5_overlap", 0.0),
    }


def render_report(observation, quality, pattern, outcome_summary, generated_at):
    lines = [
        "# Institutional Flow PoC Data Observation Report", "", "最後更新：2026-08-29", "",
        f"執行時間：{generated_at}", "",
        "本報告只呈現實際資料觀察，不做趨勢判斷，也不構成投資建議。", "",
        "## Data Quality", "",
        f"- 完整交易日：{quality.get('successful_days', 0)} / {quality.get('required_days', 0)}",
        f"- 品質 gate：{'PASS' if quality.get('success') else 'INCOMPLETE'}",
        f"- Duplicate failures：{quality.get('duplicate_failure_count', 0)}",
        f"- Arithmetic failures：{quality.get('arithmetic_failure_count', 0)}", "",
        "## Observed Flow", "",
        f"- Reversal/Weakening 可評估訊號：{observation.get('signal_count', 0)}",
        f"- 5D success（歷史觀測比例）：{observation.get('success_5d_rate', 0):.2%}",
        f"- 3D persistence（歷史觀測比例）：{observation.get('persistence_3d_rate', 0):.2%}",
        f"- 平均 Top3 concentration（5D）：{observation.get('mean_top3_concentration_5d', 0):.2%}",
        f"- 外資／投信 Top5 sector overlap：{pattern.get('top5_overlap', 0):.2%}",
        f"- 外資／投信 Model B 座標相關：{pattern.get('model_b_coordinate_correlation', 0):.3f}", "",
        "## Institution × Model", "",
        "| Institution | Model | Signals | 5D success | 3D persistence |", "|---|---:|---:|---:|---:|",
    ]
    for row in outcome_summary:
        lines.append(f"| {row['institution']} | {row['model']} | {row['count']} | {row['success_rate']:.2%} | {row['persistence_rate']:.2%} |")
    lines.extend(["", "## Notes", "", "5D success 與 3D persistence 是歷史發生比例，不是預測機率。T86 未列但行情存在的股票以零流量補齊，並保留 source_missing；目前股票 universe 來自執行當下公司主檔。", ""])
    return "\n".join(lines)
