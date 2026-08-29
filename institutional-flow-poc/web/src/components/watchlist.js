export function renderWatchlist(container, rows, payload, state, dispatch) {
  const watched = rows.latest.filter((row) => state.watchlist.includes(row.industry_code));
  const candidates = rows.latest.filter((row) => !state.watchlist.includes(row.industry_code)).slice(0, 8);
  container.innerHTML = `<div class="page-header"><div><h1 id="page-title">追蹤產業</h1><p class="muted">收藏產業的最新觀察；此頁不提供推播預測。</p></div></div><section class="card"><h2>我的追蹤（${watched.length}）</h2>${watched.length ? watched.map((row) => `<p>${row.sector} <button type="button" data-toggle="${row.industry_code}">移除</button></p>`).join("") : '<div class="empty">尚無追蹤產業</div>'}</section><section class="card" style="margin-top:1rem"><h2>可加入的產業資料</h2>${candidates.map((row) => `<p>${row.sector} <button type="button" data-toggle="${row.industry_code}">加入</button></p>`).join("")}</section>`;
  container.querySelectorAll("[data-toggle]").forEach((button) => button.addEventListener("click", () => dispatch({ type: "toggle-watchlist", value: button.dataset.toggle })));
}
