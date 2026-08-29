export function classifyQuality(quality) {
  if (!quality?.success) return "unavailable";
  return (quality.missing_in_flow_count || quality.arithmetic_failure_count || quality.duplicate_failure_count) ? "partial" : "usable";
}

export function renderStatusBar(container, meta, quality, state, dispatch) {
  const status = classifyQuality(quality);
  const label = { usable: "資料可用", partial: "部分可用", unavailable: "資料不可用" }[status];
  container.innerHTML = `<div class="status-bar">
    <span class="status-item"><strong>最新交易日</strong> ${meta.date_max || "—"}</span>
    <span class="status-item"><strong>完整日數</strong> ${quality.successful_days ?? "—"}/${quality.required_days ?? "—"}</span>
    <span class="status-item"><strong>Model A</strong> X=5D Flow × Y=1D Flow</span>
    <span class="status-item"><strong>basis</strong> ${meta.basis}</span>
    <span class="status-badge ${status}">${label}</span>
    <details class="status-item"><summary>來源與追溯</summary><div>generated_at: ${meta.generated_at || "—"}<br>source: ${Object.values(quality.source_urls || {}).join(" · ") || "—"}</div></details>
  </div>`;
}
