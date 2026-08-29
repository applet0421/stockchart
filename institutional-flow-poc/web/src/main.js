import { createInitialState, reduceState, PAGES } from "./state.js";
import { selectRows } from "./data.js";
import { renderStatusBar } from "./components/status.js";
import { renderToday } from "./components/today.js";
import { renderRotationMap } from "./components/rotation-map.js";
import { renderRanking } from "./components/ranking.js";
import { renderWatchlist } from "./components/watchlist.js";
import { renderQuality } from "./components/quality.js";
import { renderStockDrilldown } from "./components/stock-drilldown.js";

const labels = { today: "今日觀察", rotation: "Model A", ranking: "法人排行", watchlist: "追蹤產業", quality: "資料品質" };
const payload = await fetch("./data/model-a.json").then((response) => response.json());
let state = createInitialState(payload);

const content = document.querySelector("#page-content");
const status = document.querySelector("#status-region");
const desktopNav = document.querySelector("#desktop-nav");
const mobileNav = document.querySelector("#mobile-nav");

function renderNav() {
  const html = PAGES.map((page) => `<button type="button" data-page="${page}" aria-current="${state.page === page ? "page" : "false"}">${labels[page]}</button>`).join("");
  desktopNav.innerHTML = `<div class="nav-list">${html}</div>`;
  mobileNav.innerHTML = html;
}

function render() {
  const rows = selectRows(payload, state);
  renderNav();
  renderStatusBar(status, payload.meta, payload.quality, state, dispatch);
  content.replaceChildren();
  const page = document.createElement("section");
  page.className = "page-view";
  page.setAttribute("aria-labelledby", "page-title");
  content.append(page);
  if (state.page === "today") renderToday(page, rows, payload, state, dispatch);
  if (state.page === "rotation") {
    renderRotationMap(page, rows, payload, state, dispatch);
    const drilldown = document.createElement("div");
    drilldown.className = "drilldown-slot";
    page.append(drilldown);
    renderStockDrilldown(drilldown, payload, state, dispatch);
  }
  if (state.page === "ranking") renderRanking(page, rows, payload, state, dispatch);
  if (state.page === "watchlist") renderWatchlist(page, rows, payload, state, dispatch);
  if (state.page === "quality") renderQuality(page, payload.quality, payload.meta, dispatch);
}

function dispatch(action) {
  state = reduceState(state, action);
  if (action.type === "toggle-watchlist" && typeof localStorage !== "undefined") {
    localStorage.setItem("stockchart.watchlist", JSON.stringify(state.watchlist));
  }
  render();
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page]");
  if (button) dispatch({ type: "navigate", page: button.dataset.page });
});

render();
