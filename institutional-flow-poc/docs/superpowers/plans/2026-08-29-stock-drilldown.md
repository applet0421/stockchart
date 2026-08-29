# Phase 1 Stock Drill-down Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a transparent Model A sector-to-stock drill-down and historical stock flow view using the existing public-data pipeline.

**Architecture:** Extend the existing export payload rather than introducing a backend. Keep aggregation in Python, keep view state serializable in `state.js`, and render the drill-down as focused components composed by the current page renderer.

**Tech Stack:** Python standard library, existing project metrics, vanilla ES modules, native HTML/SVG, Node built-in test runner.

**Spec:** `docs/superpowers/specs/2026-08-29-stock-drilldown-design.md`

## Global Constraints

- Model A remains `flow_5d` on X and `flow_1d` on Y.
- Preserve `null`, `success`, `failure`, and `source_missing` provenance fields.
- Do not add third-party dependencies.
- Do not create unsupported topic assignments; mapping metadata must be versioned.
- Keep the UI observation-only; no buy/sell recommendation copy.

### Task 1: Extend export payload with stock drill-down rows

**Files:**
- Modify: `src/institutional_flow_poc/web_payload.py`
- Modify: `tests/test_web_payload.py`

**Interfaces:**
- Produce `stocks_by_sector` and `stock_history_by_symbol` in `build_model_a_payload`.
- Preserve existing payload keys and Model A output.

- [ ] Add failing tests for a sector stock row, contribution share, and null source values.
- [ ] Implement aggregation from `stock_flow.json` and `institutional_flow.json`, joining by date/symbol and sector mapping.
- [ ] Add `topic_mapping: {version, source, assignments}` metadata using the existing 32-sector assignments.
- [ ] Run `PYTHONPATH=src python3 -m unittest tests.test_web_payload -v`.

### Task 2: Add serializable drill-down state

**Files:**
- Modify: `web/src/state.js`
- Modify: `web/tests/state.test.mjs`

**Interfaces:**
- Add `selectedSector`, `selectedSymbol`, and `stockQuery` state fields.
- Add reducer actions `select-sector`, `select-symbol`, and `set-stock-query`.

- [ ] Add failing Node tests for sector selection clearing symbol and query updates.
- [ ] Implement reducer transitions without mutating prior state.
- [ ] Run `node --test web/tests/state.test.mjs`.

### Task 3: Render stock table and history panel

**Files:**
- Create: `web/src/components/stock-drilldown.js`
- Modify: `web/src/components/rotation-map.js`
- Modify: `web/src/main.js`
- Modify: `web/styles.css`

**Interfaces:**
- `renderStockDrilldown(container, payload, state, dispatch)` consumes `stocks_by_sector` and `stock_history_by_symbol`.
- Model A detail panel dispatches `select-sector`; stock rows dispatch `select-symbol`.

- [ ] Add component with accessible table headers, search input, null-safe metrics, source-gap badge, and history SVG.
- [ ] Add keyboard/click handlers for circles and stock rows.
- [ ] Keep history chart native SVG and label it with the selected symbol/name.
- [ ] Add responsive styles for table overflow and stacked detail layout.

### Task 4: Integrate export, tests, and browser verification

**Files:**
- Modify: `tests/test_web_smoke.py`
- Modify: `README.md`

- [ ] Add smoke assertions for new payload keys and component script references.
- [ ] Regenerate `web/data/model-a.json` with `export-web`.
- [ ] Run full `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v`.
- [ ] Run `node --test web/tests/state.test.mjs` and `python3 -m compileall -q src tests`.
- [ ] Use the connected browser to verify Model A sector selection, stock search, history selection, and 390px responsive layout.
- [ ] Update README with the Phase 1 run command and known limitation that topic mapping remains at 32 validated sectors.
