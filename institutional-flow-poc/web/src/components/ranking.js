import { formatMetric } from "../data.js";

export function renderRanking(container, rows, payload, state, dispatch) {
  const metric = "flow_5d";
  const ranked = rows.rankings[metric] || rows.latest;
  container.innerHTML = `<div class="page-header"><div><h1 id="page-title">法人排行</h1><p class="muted">只呈現資料排序，不代表推薦或方向判斷。</p></div></div><div class="controls"><label>法人組合<select data-action="set-institution">${payload.institutions.map((name) => `<option value="${name}" ${name === state.institution ? "selected" : ""}>${name}</option>`).join("")}</select></label></div><div class="table-wrap"><table><thead><tr><th>產業</th><th>Flow 5D</th><th>Flow 1D</th><th>Breadth</th><th>Top3 concentration</th><th>股票數</th></tr></thead><tbody>${ranked.slice(0, 20).map((row) => `<tr><td>${row.sector}</td><td>${formatMetric(row.flow_5d, state.basis)}</td><td>${formatMetric(row.flow_1d, state.basis)}</td><td>${row.breadth_5d == null ? "—" : `${(row.breadth_5d * 100).toFixed(0)}%`}</td><td>${row.top3_concentration_5d == null ? "—" : `${(row.top3_concentration_5d * 100).toFixed(0)}%`}</td><td>${row.stock_count_5d ?? "—"}</td></tr>`).join("")}</tbody></table></div>`;
  container.querySelector('[data-action="set-institution"]').addEventListener("change", (event) => dispatch({ type: "set-institution", value: event.target.value }));
}
