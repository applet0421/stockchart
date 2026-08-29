# StockChart Model A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一個只呈現 Model A（5D Flow × 1D Flow）的 StockChart 觀察介面，讓使用者能從最新資料狀態進入 Rotation Map、法人排行、追蹤產業與資料品質檢查。

**Architecture:** 以 Python 標準函式庫把既有 processed／outputs 正規化成單一 `model-a.json` payload；前端採無框架 ES modules 與原生 SVG，直接讀取該 payload。所有頁面共享同一份 state，切換法人組合、日期與 basis 時同步刷新圖表、表格與 provenance。

**Tech Stack:** Python 3.9+、既有 `institutional_flow_poc` 套件、原生 HTML/CSS/ES modules、原生 SVG、Node built-in test runner、pytest。

**Spec:** `docs/superpowers/specs/2026-08-29-stockchart-model-a-interface-design.md`

## Global Constraints

- Model A 固定為 `X=5D Flow`、`Y=1D Flow`；不實作 Model B 或 A/B 比較。
- 保留既有 `shares`／`amount` 定義、資料品質檢查、來源 URL、`generated_at` 與 SHA-256。
- 象限只作資料座標分類，不出現 AI、看多／看空、預測機率、明牌、推薦或交易訊號語意。
- 不新增第三方前端或圖表套件；圖表使用原生 SVG。
- 缺漏、算術失敗與日期不足不得以零值或空白掩蓋。
- 桌面與手機版都必須提供資料品質與來源入口。
- 本 workspace 目前不是 Git repository；若實作時仍無 Git metadata，保留每個任務的驗證紀錄並跳過 commit 指令。

## File Map

- Create `src/institutional_flow_poc/web_payload.py`: 將既有輸出轉成前端單一資料契約。
- Modify `src/institutional_flow_poc/cli.py`: 新增 `export-web` 子命令。
- Create `tests/test_web_payload.py`: payload 欄位、排序、缺值與品質狀態測試。
- Create `web/index.html`: 應用程式 shell、頁面標題與導航容器。
- Create `web/styles.css`: 深色／亮色 tokens、桌面與手機 layout、focus 狀態。
- Create `web/src/state.js`: 可序列化的 Model A UI state 與 reducer。
- Create `web/src/data.js`: payload 載入、日期／法人／basis 篩選與格式化。
- Create `web/src/components/status.js`: 資料狀態列與錯誤狀態。
- Create `web/src/components/today.js`: 今日觀察首頁。
- Create `web/src/components/rotation-map.js`: Model A 原生 SVG 與產業詳情。
- Create `web/src/components/ranking.js`: Flow／Breadth／集中度排行。
- Create `web/src/components/watchlist.js`: 追蹤產業與空狀態。
- Create `web/src/components/quality.js`: 品質、來源與 manifest 顯示。
- Create `web/src/main.js`: 路由、事件委派與畫面組裝。
- Create `web/tests/state.test.mjs`: state reducer 與篩選行為測試。
- Create `web/tests/fixtures/model-a.json`: 最小可重現的前端測試資料。

### Task 1: 建立 Model A 前端資料契約

**Files:**
- Create: `src/institutional_flow_poc/web_payload.py`
- Modify: `src/institutional_flow_poc/cli.py`
- Test: `tests/test_web_payload.py`

**Interfaces:**
- `build_model_a_payload(sector_rows, rotation_rows, institution_rows, quality, *, institution="all", basis="shares") -> dict`
- `write_model_a_payload(output_dir: Path, payload: dict) -> Path`
- Payload keys: `meta`, `latest`, `history`, `rankings`, `quality`, `institutions`。
- `meta` 必須包含 `model="A"`、`x_metric="flow_5d"`、`y_metric="flow_1d"`、`basis`、`date_min`、`date_max`、`generated_at`。

- [ ] **Step 1: Write failing tests**

```python
def test_build_model_a_payload_has_model_a_axes_and_quality():
    payload = build_model_a_payload(SECTOR_ROWS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY)
    assert payload["meta"]["model"] == "A"
    assert payload["meta"]["x_metric"] == "flow_5d"
    assert payload["meta"]["y_metric"] == "flow_1d"
    assert payload["quality"]["success"] is True

def test_missing_window_values_remain_null():
    payload = build_model_a_payload(SECTOR_ROWS_WITH_NULLS, ROTATION_ROWS, INSTITUTION_ROWS, QUALITY)
    row = next(item for item in payload["latest"] if item["industry_code"] == "01")
    assert row["flow_5d"] is None
```

- [ ] **Step 2: Run tests and verify failure**

Run: `PYTHONPATH=src pytest tests/test_web_payload.py -q`

Expected: FAIL because `web_payload.py` and the payload builder do not exist.

- [ ] **Step 3: Implement the adapter**

Read the existing JSON/CSV-shaped dictionaries without recomputing Flow. Select the requested `institution` and `basis`, sort `latest` by `industry_code`, keep nulls unchanged, copy quality fields verbatim, and derive `rankings` only from existing numeric fields (`flow_1d`, `flow_5d`, `breadth_5d`, `top1_concentration_5d`, `top3_concentration_5d`, `stock_count_5d`). Reject `model != "A"` or unsupported basis with `ValueError`.

- [ ] **Step 4: Add the CLI export command**

Add `export-web` to `cli.py`; it reads `outputs/latest_sector_observation.json`, `outputs/latest_rotation_model_comparison.json`, `outputs/latest_institution_comparison.json`, `outputs/run_manifest.json`, writes `web/data/model-a.json`, and prints the output path plus `success`／`failure` summary.

- [ ] **Step 5: Run tests and verify success**

Run: `PYTHONPATH=src pytest tests/test_web_payload.py -q`

Expected: all payload and null-preservation tests pass.

### Task 2: 建立無框架應用 shell 與共享 state

**Files:**
- Create: `web/index.html`
- Create: `web/styles.css`
- Create: `web/src/state.js`
- Create: `web/src/data.js`
- Create: `web/src/main.js`
- Test: `web/tests/state.test.mjs`, `web/tests/fixtures/model-a.json`

**Interfaces:**
- `createInitialState(payload) -> { page, institution, date, basis, trailWindow, selectedIndustryCode, watchlist }`
- `reduceState(state, action) -> state`
- `selectRows(payload, state) -> { latest, history, rankings }`
- `formatMetric(value, basis) -> string`

- [ ] **Step 1: Write reducer and selector tests**

```js
import assert from "node:assert/strict";
import test from "node:test";
import { createInitialState, reduceState } from "../src/state.js";

test("institution and basis changes are serializable", () => {
  const state = createInitialState(fixture);
  const next = reduceState(state, { type: "set-institution", value: "foreign" });
  assert.equal(next.institution, "foreign");
});

test("page navigation does not reset selected date", () => {
  const state = { ...createInitialState(fixture), date: "2026-08-28" };
  const next = reduceState(state, { type: "navigate", page: "rotation" });
  assert.equal(next.date, "2026-08-28");
});
```

- [ ] **Step 2: Run the tests and verify failure**

Run: `node --test web/tests/state.test.mjs`

Expected: FAIL because the modules and fixture do not exist.

- [ ] **Step 3: Implement the shell and state modules**

Create one `h1`, a five-item navigation (`今日觀察`, `Model A`, `法人排行`, `追蹤產業`, `資料品質`), a main content region, and a live status region. Initialize state from `model-a.json`; navigation actions must preserve date, institution and basis.

- [ ] **Step 4: Implement the visual tokens**

Define CSS variables for background, surface, border, text, positive, negative and warning states. Add keyboard-visible `:focus-visible`, 44px minimum touch targets, mobile bottom navigation, desktop side navigation, and a layout that reflows below 768px.

- [ ] **Step 5: Run tests and verify success**

Run: `node --test web/tests/state.test.mjs`

Expected: all state tests pass.

### Task 3: 實作今日觀察與資料狀態列

**Files:**
- Create: `web/src/components/status.js`
- Create: `web/src/components/today.js`
- Modify: `web/src/main.js`
- Test: `web/tests/state.test.mjs`

**Interfaces:**
- `renderStatusBar(container, meta, quality) -> void`
- `renderToday(container, selectedRows, quality, dispatch) -> void`

- [ ] **Step 1: Add tests for status classification**

```js
test("quality status distinguishes usable, partial, and unavailable", () => {
  assert.equal(classifyQuality({ success: true, missing_in_flow_count: 0 }), "usable");
  assert.equal(classifyQuality({ success: true, missing_in_flow_count: 2 }), "partial");
  assert.equal(classifyQuality({ success: false }), "unavailable");
});
```

- [ ] **Step 2: Implement the status bar**

Render latest date, `successful_days/required_days`, basis, quality label, `generated_at`, and an expandable source／hash block. Put partial or unavailable warnings before chart content.

- [ ] **Step 3: Implement the Today view**

Render neutral metric cards for Flow 1D／5D／20D, Breadth and stock count; add a compact Model A preview region with explicit `X=5D Flow` and `Y=1D Flow` text. Do not render recommendation, direction, prediction or trading language.

- [ ] **Step 4: Wire navigation and verify**

Run: `node --test web/tests/state.test.mjs`

Expected: status and navigation tests pass; changing institution or basis rerenders both status metadata and cards.

### Task 4: 實作 Model A Rotation Map 與產業詳情

**Files:**
- Create: `web/src/components/rotation-map.js`
- Modify: `web/src/main.js`, `web/styles.css`
- Test: `web/tests/state.test.mjs`

**Interfaces:**
- `renderRotationMap(container, rows, state, dispatch) -> void`
- `renderIndustryDetails(container, row, historyRows, meta, quality) -> void`
- `quadrantLabel(x, y) -> "ACCUMULATING" | "WEAKENING" | "REVERSING" | "DISTRIBUTING"`

- [ ] **Step 1: Add pure Model A tests**

```js
test("Model A uses 5D on x and 1D on y", () => {
  const point = projectPoint({ model_a_x: 0.25, model_a_y: -0.1 });
  assert.equal(point.xMetric, "flow_5d");
  assert.equal(point.yMetric, "flow_1d");
});
```

- [ ] **Step 2: Implement the SVG map**

Draw zero axes, four neutral quadrant labels, circles sized from `stock_count_5d`, and text labels with a non-truncated accessible fallback. Render a legend for basis and metrics. Use click and keyboard activation to select a point; do not rely on hover alone.

- [ ] **Step 3: Implement trail and detail panel**

For the selected industry, draw 5D／10D／20D historical trail from `history`, then show Flow 1D／5D／20D, Breadth, Top1／Top3 concentration, stock count, institution, basis, date and quality metadata. Keep trail colors descriptive rather than directional.

- [ ] **Step 4: Verify map behavior**

Run: `node --test web/tests/state.test.mjs`

Expected: metric mapping, quadrant labeling and selected-industry state tests pass.

### Task 5: 實作法人排行、追蹤產業與資料品質頁

**Files:**
- Create: `web/src/components/ranking.js`
- Create: `web/src/components/watchlist.js`
- Create: `web/src/components/quality.js`
- Modify: `web/src/main.js`
- Test: `web/tests/state.test.mjs`

**Interfaces:**
- `renderRanking(container, rankings, state, dispatch) -> void`
- `renderWatchlist(container, watchlist, latestRows, dispatch) -> void`
- `renderQuality(container, quality, meta, dispatch) -> void`

- [ ] **Step 1: Implement ranking filters**

Provide tabs for Flow, Breadth, Top1 concentration, Top3 concentration and stock count; provide period controls for 1D, 5D and 20D where data exists. Every row includes value, unit, period, institution and date.

- [ ] **Step 2: Implement watchlist state**

Persist only industry codes in `localStorage`; render an empty state with a data-sorted add list, never a recommendation label. Keep add/remove controls keyboard accessible.

- [ ] **Step 3: Implement quality page**

Render complete days, row counts, duplicate count, arithmetic failure count, missing symbol count, source URLs, generated_at and SHA-256. Unavailable status disables map-dependent content and shows the exact failure array.

- [ ] **Step 4: Run tests**

Run: `node --test web/tests/state.test.mjs && PYTHONPATH=src pytest -q`

Expected: frontend state tests and the existing Python suite pass.

### Task 6: 整合、響應式與交付驗證

**Files:**
- Modify: `web/index.html`, `web/styles.css`, `web/src/main.js`
- Create: `tests/test_web_smoke.py`

- [ ] **Step 1: Add a static smoke test**

Assert that `web/index.html` references `web/src/main.js`, `web/data/model-a.json` exists after export, and every navigation label appears exactly once in the HTML shell.

- [ ] **Step 2: Generate the payload and start local server**

Run: `PYTHONPATH=src python3 -m institutional_flow_poc export-web`

Then run: `python3 -m http.server 8000 --directory web`

- [ ] **Step 3: Verify desktop and mobile manually**

Check at 1280×720 and 390×844: status bar remains visible, Model A axes are labeled, controls update all views, labels remain accessible without hover, bottom／side navigation works, and quality warnings remain visible when fixture data is incomplete.

- [ ] **Step 4: Verify accessibility and prohibited language**

Run: `rg -n 'AI|看多|看空|預測|明牌|推薦|交易訊號|Model B' web src tests`

Expected: only intentional negative-constraint documentation matches; no rendered UI copy contains prohibited language.

- [ ] **Step 5: Run the complete verification suite**

Run: `node --test web/tests/state.test.mjs && PYTHONPATH=src pytest -q`

Expected: exit code 0, no test failures.
