# Institutional Flow PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立並實跑 TWSE 120 交易日法人板塊流量資料觀察 PoC。

**Architecture:** 純 Python 批次管線，官方 JSON 落 raw、正規化 CSV 落 processed、分析產物落 outputs。每階段可單獨重跑，品質 gate 先於分析。

**Tech Stack:** Python 3.9+ standard library, unittest, CSV/JSON/SVG/Markdown

**Spec:** `docs/superpowers/specs/2026-08-29-institutional-flow-poc-design.md`

## Global Constraints

- 只使用 TWSE 官方公司主檔、MI_INDEX 與 T86。
- 最近 120 個完整交易日；普通股只採公司主檔交集的四位數字代號。
- 外資、投信、自營商可分開觀察，也支援外資＋投信、All 與 `+` 自由組合；不加入 AI、新聞、即時行情與前端。
- 品質失敗必須保留 `summary`、`success`、`failure` 可回歸輸出。
- 報告只做資料觀察，不輸出趨勢判斷或投資建議。

---

### Task 1: Project contract and source mapping

**Files:** Create `README.md`, `pyproject.toml`, `src/institutional_flow_poc/config.py`, `tests/test_config.py`.

**Interfaces:** Produces source URLs, 33-industry mapping, canonical field mappings and project paths.

- [ ] Write tests that require all official source definitions, unique industry codes and required canonical fields.
- [ ] Run `python -m unittest tests.test_config -v` and confirm failure because the package does not exist.
- [ ] Add the minimal configuration and mapping implementation.
- [ ] Re-run the test and confirm pass.

### Task 2: Parsers and quality validation

**Files:** Create `src/institutional_flow_poc/parsers.py`, `src/institutional_flow_poc/quality.py`, `tests/fixtures/*.json`, `tests/test_parsers.py`, `tests/test_quality.py`.

**Interfaces:** Produces `parse_companies(payload)`, `parse_market(date,payload,universe)`, `parse_t86(date,payload,universe)` and `validate_tables(...)`.

- [ ] Write fixture-backed tests for company, MI_INDEX and T86 parsing, including comma numbers and missing prices.
- [ ] Confirm parser tests fail for missing functions.
- [ ] Implement parsers and confirm tests pass.
- [ ] Write validation tests for duplicates, date mismatch, buy-sell-net mismatch and missing symbols.
- [ ] Confirm validation tests fail, implement validators, and confirm pass.

### Task 3: Fetch and normalization pipeline

**Files:** Create `src/institutional_flow_poc/fetch.py`, `src/institutional_flow_poc/storage.py`, `tests/test_fetch.py`, `tests/test_storage.py`.

**Interfaces:** Produces raw company JSON, dated market/T86 JSON, `fetch_manifest.json`, canonical processed CSV, `data_quality.json` and `meta-dimension-smoke.summary.json`.

- [ ] Test retry/error records and atomic JSON/CSV round trips without external-network mocks beyond the HTTP boundary.
- [ ] Confirm failures, implement storage and fetch orchestration, then confirm pass.
- [ ] Ensure a day counts only when both official responses are valid and require exactly 120 successful days.

### Task 4: Flow and sector metrics

**Files:** Create `src/institutional_flow_poc/metrics.py`, `tests/test_metrics.py`.

**Interfaces:** Produces stock 1D/5D/20D flow and sector flow, breadth, Top1/Top3 concentration and stock count.

- [ ] Write hand-calculated two-sector fixtures for rolling sums, missing history, breadth and concentration.
- [ ] Confirm tests fail, implement minimal rolling calculations, and confirm pass.

### Task 5: Rotation, outcomes and visual maps

**Files:** Create `src/institutional_flow_poc/rotation.py`, `src/institutional_flow_poc/svg.py`, `tests/test_rotation.py`, `tests/test_svg.py`.

**Interfaces:** Produces foreign/trust rotation rows, transition matrix, signal outcomes and two real-data SVG maps.

- [ ] Test quadrant boundaries, transition probabilities, forward outcomes and renderable SVG content.
- [ ] Confirm failures, implement rotation analytics and SVG renderer, and confirm pass.

### Task 6: CLI, real run and decision report

**Files:** Create `src/institutional_flow_poc/cli.py`, `src/institutional_flow_poc/report.py`, `tests/test_cli.py`, `tests/test_report.py`, update `README.md`.

**Interfaces:** Exposes `python -m institutional_flow_poc {fetch,process,analyze,report,run}` and writes required outputs plus `decision_report.md`.

- [ ] Test CLI routing and deterministic decision thresholds; confirm failure.
- [ ] Implement commands and report; confirm targeted tests and full suite pass.
- [ ] Run against the latest 120 complete TWSE sessions.
- [ ] Verify required files, row counts, no duplicate keys, quality summary, SVG validity and GO/MODIFY/NO-GO evidence.
