# Institutional Flow PoC PRD（整合版）

最後更新：2026-08-29

## 1. 背景與產品目標

本 PoC 延續原對話的核心需求：使用 TWSE 官方資料，建立最近 120 個完整交易日的上市普通股法人流量資料，觀察產業層的 Flow、Breadth、集中度、Rotation Trail、Reversal persistence，以及不同法人之間是否呈現不同的流量分布。

最新版本將法人觀察從原本的外資／投信擴充為外資、投信、自營商與可自由組合的法人群組，同時保留 raw／processed 分層、每日快照、品質檢查與來源追溯。

產品定位是「可重跑、可核對的資料觀察工具」，不是選股、預測或交易系統。

## 2. 使用者與使用情境

使用者可以：

1. 查看某一交易日各產業的法人 Flow 與 Breadth。
2. 比較外資、投信、自營商在相同產業的數值差異。
3. 查看外資＋投信或 All 的合計流量。
4. 以 `+` 自由組合法人，例如 `foreign+dealer` 或 `trust+dealer`。
5. 沿日期重建 5D、10D、20D Rotation Trail。
6. 追溯每次輸出的來源、日期範圍、筆數、缺漏與檔案雜湊。

## 3. 資料範圍與排除規則

- 市場：TWSE 上市。
- 股票：公司主檔中的四位數普通股代號。
- 產業：TWSE 官方產業分類與代碼 mapping。
- 期間：截止日向前尋找最近 120 個同時具有有效行情與 T86 的完整交易日。
- 排除：ETF、權證、ETN、牛熊證、特別股及其他非普通股票。
- 來源：TWSE OpenAPI 公司主檔、MI_INDEX 每日行情、T86 法人買賣超。
- 行情存在但 T86 未列的股票，法人流量補零但保留 `source_missing=true` 與每日缺漏清單。

## 4. 法人維度與自由組合

### 基礎法人

- `foreign`：外陸資，不含外資自營商。
- `trust`：投信。
- `dealer`：自營商合計，包含自行買賣與避險。

### 預設組合

- `combined`：外資＋投信。
- `all`：外資＋投信＋自營商。

### 自由組合

以 `+` 串接基礎法人，例如 `foreign+dealer`、`trust+dealer`、`foreign+trust+dealer`。組合的 net 必須先逐筆相加，再進行視窗與產業聚合，不得平均個別法人 Flow Ratio。

## 5. Canonical data layers

### Raw

保存官方 JSON、請求日期、回應狀態、重試次數與 `fetch_manifest.json`。

### Processed

- `stocks.csv`
- `daily_market.csv`
- `institutional_flow.csv`
- `stock_flow.csv`
- `sector_flow.csv`
- `data_quality.json`
- `quality_observation_daily.csv`

`institutional_flow.csv` 必須包含 foreign、trust、dealer 的 buy／sell／net 與 `source_missing`。

### Outputs

- `sector_observation_daily.csv`、`latest_sector_observation.csv`
- `institution_comparison_daily.csv`、`latest_institution_comparison.csv`
- 各法人／組合的 `*_rotation.csv` 與 `*_rotation_map.svg`
- `rotation_model_comparison.csv`／`.svg`：同一產業與法人組合的 Model A／B 並列座標
- `transition_matrix.csv`
- `signal_outcomes.csv`
- `decision.json`、`decision_report.md`
- `run_manifest.json`

## 6. 指標定義

每個股票與產業組合均提供 1D、5D、20D Flow Ratio：

```text
FlowRatio_ND = sum(group_net over N valid trading days)
               / sum(volume over N valid trading days)
```

產業層另提供 `breadth_5d`、`top1_concentration_5d`、`top3_concentration_5d` 與 `stock_count_5d`。產業層直接加總股票 net 與成交量，不平均個股比例。

### 計算基礎

- `shares`（預設）：`net shares / volume shares`。
- `amount`：以 `net shares × daily close` 與 `volume shares × daily close` 計算收盤價估算金額比例；收盤價缺失時該筆視窗留空。
- `run_manifest.json` 記錄本次使用的 `basis`。T86 沒有逐法人金額欄位，因此 `amount` 是可追溯的收盤價估算，不宣稱為原始成交金額。

## 7. Rotation 與歷史觀察

- Model A：X＝5D Flow，Y＝1D Flow。
- Model B：X＝20D Flow，Y＝5D Flow。
- 象限只代表座標分類：ACCUMULATING、WEAKENING、REVERSING、DISTRIBUTING。
- 每一法人／組合保留每日座標，供 5D、10D、20D trail 重建。
- `5D success` 與 `3D persistence` 只表示歷史資料中觀察到的比例，不是預測機率。

## 8. 品質與可追溯性需求

每次執行必須檢查並輸出交易日期、row count、duplicate、foreign／trust／dealer 的 `buy - sell = net`、缺失 symbol、120 日完整性，以及 `run_manifest.json` 的來源 URL、期間、筆數、generated_at 與 SHA-256。

## 9. CLI 與執行契約

```bash
PYTHONPATH=src python3 -m institutional_flow_poc run --days 120 --end-date 2026-08-28
PYTHONPATH=src python3 -m institutional_flow_poc analyze --groups foreign,trust,dealer,foreign+dealer,all
PYTHONPATH=src python3 -m institutional_flow_poc analyze --basis amount
```

## 10. 視覺化與交付

視覺化規格以 `docs/visualization-spec.md` 為準。現階段使用專案內建 `src/institutional_flow_poc/svg.py` 以 Python 標準函式庫直接產生 SVG，不依賴第三方圖表套件或前端框架。每張 Map 必須標示期間、法人組合與 Model，並提供對應 CSV；最新日快照與品質資訊需可獨立檢查。

## 11. 明確非目標與產品護欄

本版本不加入 AI、新聞、Event Intelligence、即時行情、完整前端網站、策略門檻、買賣訊號、趨勢判斷、投資建議或 GO／MODIFY／NO-GO 結論。原始需求中的決策判斷段落已由最新產品原則覆寫為 observation-only。

## 12. 驗收條件

- 120/120 完整交易日可重跑。
- raw／processed／outputs 分層完整。
- 外資、投信、自營商、combined、all 與自由組合均可計算。
- 每日產業觀察、最新快照、Rotation CSV／SVG、品質與 manifest 均產生。
- 所有測試通過，且輸出不包含未經資料支持的趨勢或投資語意。
