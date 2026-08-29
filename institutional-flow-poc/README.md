# institutional-flow-poc

最後更新：2026-08-29

使用 TWSE 官方 OpenAPI、MI_INDEX 與 T86，建立最近 120 個完整交易日的上市普通股外資、投信及「外資＋投信」合計產業流量資料集。專案只做資料觀察，不做趨勢判斷或投資建議，也不需要第三方 Python 套件。

## Run

```bash
PYTHONPATH=src python3 -m institutional_flow_poc run --days 120 --end-date 2026-08-28
```

也可分開執行 `fetch`、`process`、`analyze`、`report`。`fetch` 的 `--end-date` 可省略，預設從執行日向前尋找；只有行情與 T86 同時有效且品質檢查通過的日期才算一個交易日。`analyze --groups` 可用逗號指定法人組合，例如 `foreign,trust,dealer,foreign+dealer,all`；`--basis amount` 可切換為收盤價估算金額基礎，預設為股數基礎。

## Layers

- `data/raw/`：官方 JSON 與 `fetch_manifest.json`。
- `data/processed/`：正規化股票、行情、法人、股票 Flow、產業 Flow 與 `data_quality.json`。
- `outputs/`：指定 Rotation CSV（外資、投信、自營商、合計、All 或自訂組合）、每日產業觀察與最新日快照、對應 SVG Rotation Map、資料品質與 `run_manifest.json`、觀察報告。

每日觀察檔保留原始日期、法人別、產業、Flow Ratio、Breadth 與集中度；`run_manifest.json` 記錄資料期間、筆數、官方來源 URL 及輸出檔 SHA-256，供每次執行追溯。所有報告維持 observation-only，不產生趨勢判斷或投資建議。

產品需求見 `docs/institutional-flow-poc-prd.md`，視覺化規格見 `docs/visualization-spec.md`；完整來源與公式見 `docs/superpowers/specs/2026-08-29-institutional-flow-poc-design.md`，欄位對照見 `docs/field_mapping.md`。
## Phase 1 web preview

Export the validated Model A payload and serve the static UI:

```bash
PYTHONPATH=src python3 -m institutional_flow_poc export-web
python3 -m http.server 8000 --directory web
```

Model A now supports sector selection, latest-date component-stock drill-down, stock search, contribution share, institutional net-share breakdown, source-gap badges, and compact 120-trading-day Flow 5D history. The topic mapping is intentionally limited to the 32 validated sectors (`sector-v1`); no unsupported 110-topic assignments are fabricated. Historical stock data in the static payload is for the selected export institution (default `all`); an API-backed implementation can load other institutions on demand.
