import { formatMetric } from "../data.js";

export function renderToday(container, rows, payload, state, dispatch) {
  const top = [...rows.latest].sort((a, b) => (b.flow_5d ?? -Infinity) - (a.flow_5d ?? -Infinity)).slice(0, 6);
  container.innerHTML = `<div class="page-header"><div><h1 id="page-title">今日觀察</h1><p class="muted">${payload.meta.date_max || "—"}｜Model A 固定使用 5D Flow × 1D Flow</p></div></div>
    <div class="controls"><label>法人組合<select data-action="set-institution">${payload.institutions.map((name) => `<option value="${name}" ${name === state.institution ? "selected" : ""}>${name}</option>`).join("")}</select></label><label>basis<select data-action="set-basis"><option value="shares" ${state.basis === "shares" ? "selected" : ""}>shares</option><option value="amount" ${state.basis === "amount" ? "selected" : ""} ${payload.meta.basis !== "amount" ? "disabled" : ""}>amount</option></select></label>${payload.meta.basis !== "amount" ? '<span class="muted">目前資料以 shares 匯出</span>' : ""}</div>
    <section aria-labelledby="today-metrics"><h2 id="today-metrics">最新產業觀察</h2><div class="card-grid">${top.map((row) => `<article class="card"><span>${row.sector}</span><strong>${formatMetric(row.flow_5d, state.basis)}</strong><span class="muted">Flow 1D ${formatMetric(row.flow_1d, state.basis)}｜Breadth ${row.breadth_5d == null ? "—" : `${(row.breadth_5d * 100).toFixed(0)}%`}</span></article>`).join("")}</div></section>
    <section class="card" style="margin-top:1rem"><h2>Model A 預覽</h2><p class="muted">X 軸：5D Flow｜Y 軸：1D Flow。進入 Model A 查看完整座標與 trail。</p><button type="button" data-page="rotation">查看 Model A</button></section>`;
  container.querySelector('[data-action="set-institution"]').addEventListener("change", (event) => dispatch({ type: "set-institution", value: event.target.value }));
  container.querySelector('[data-action="set-basis"]').addEventListener("change", (event) => dispatch({ type: "set-basis", value: event.target.value }));
}
