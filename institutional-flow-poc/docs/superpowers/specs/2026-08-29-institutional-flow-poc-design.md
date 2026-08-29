# Institutional Flow PoC Design

最後更新：2026-08-29

## Goal

以 TWSE 官方資料建立最近 120 個交易日的可重跑法人板塊流量觀察 PoC，分別呈現外資、投信、自營商，以及外資＋投信、All 與自訂組合的 Rotation Trail、Reversal persistence、Sector breadth 與差異；只做資料觀察，不產出投資判斷。

## Scope

- 市場：TWSE 上市普通股。
- 資料：上市公司基本資料與官方產業分類、每日收盤行情、T86 外資、投信與自營商買賣超。
- 排除：ETF、ETN、權證、牛熊證、特別股及其他非普通股。
- 期間：執行截止日向前尋找最近 120 個同時具有行情與 T86 的交易日。
- 不做：AI、新聞、Event Intelligence、即時行情與前端網站。

## Architecture

管線只依賴 Python 標準函式庫。`fetch` 將官方 JSON 原封保存到 `data/raw`，並產生逐請求 manifest；`process` 將欄位正規化至 `data/processed`；`analyze` 計算股票與產業指標、兩種 Rotation Model、轉移矩陣及訊號結果；`report` 產生 SVG Rotation Map 與決策報告。`run` 依序執行四階段。

所有輸出採 CSV、JSON、SVG 或 Markdown，讓結果在沒有資料庫與 notebook 的環境也能檢查與回歸。抓取失敗不會被吞掉；不足 120 個完整交易日即整體失敗，避免以不完整期間產生結論。

## Official Sources and Universe

- 公司主檔：`https://openapi.twse.com.tw/v1/opendata/t187ap03_L`。
- 法人：`https://www.twse.com.tw/rwd/zh/fund/T86`，`selectType=ALL`。
- 行情：`https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX`，`type=ALLBUT0999`，選取「每日收盤行情」資料表。
- 普通股母集合：公司主檔中的公司代號，且代號須為四位數字。每日行情與 T86 都必須與此集合交集。
- 產業：公司主檔的 `產業別` 代碼，名稱由 TWSE 公布的 33 類產業代碼表 mapping。

## Canonical Tables

### `stocks.csv`

`symbol,name,industry_code,industry_name,market,listed_date,issued_common_shares,source_report_date`

### `daily_market.csv`

`date,symbol,name,volume,trade_count,turnover,open,high,low,close,price_change,pe_ratio`

### `institutional_flow.csv`

`date,symbol,name,foreign_buy,foreign_sell,foreign_net,trust_buy,trust_sell,trust_net,dealer_buy,dealer_sell,dealer_net,source_missing`

T86 是稀疏報表；行情存在而 T86 未列的證券以零法人流量補齊，並標記 `source_missing=true`。品質報告仍保存補齊前的 missing symbol 清單，避免補零掩蓋來源差異。

### `stock_flow.csv`

除市場與法人欄位外，分別包含各法人組合的 `*_flow_1d/5d/20d`。N 日公式固定為同一股票最近 N 個有效交易日 `sum(net) / sum(volume)`；組合先將成員 net 相加，不平均比例；歷史不足 N 日時留空。

### `sector_flow.csv`

每個 `date × sector × institution` 計算：

- `flow_1d/5d/20d = sum(stock net over window) / sum(stock volume over window)`。
- `breadth_Nd = window net > 0 的股票數 / 有效股票數`。
- `top1/top3_concentration_Nd = 最大一／三檔 abs(window net) / sum(abs(window net))`。
- `stock_count_Nd` 為該視窗有效股票數。

產業 Flow 直接先加總股數，不平均個股 Flow Ratio。

## Rotation Models and Outcomes

- Model A：`x = flow_5d`、`y = flow_1d`，偏向方向改變。
- Model B：`x = flow_20d`、`y = flow_5d`，偏向中期趨勢。
- Quadrant：`ACCUMULATING (+,+)`、`WEAKENING (+,-)`、`REVERSING (-,+)`、`DISTRIBUTING (-,-)`；零視為正側。
- Rotation CSV 皆同時包含 Model A 與 Model B 的每日座標，供 5D/10D/20D trail 重建。
- `transition_matrix.csv`：institution、model、from/to quadrant、count、probability。
- `signal_outcomes.csv`：每個 Reversing/Weakening 觀測的未來 3 日同方向比例、未來 5 日 Flow 與 persistence/success 布林值。Reversing 成功定義為未來 5 日 Flow > 0；Weakening 成功定義為未來 5 日 Flow < 0。

## Data Quality Gates

- 交易日期：行情與 T86 回應日期必須等於請求日期，兩者都為 `OK`。
- Row count：每個完整交易日的普通股行情、法人交集筆數必須大於零，並記錄原始與交集 row count。
- Duplicate：`date + symbol` 在行情與法人表不得重複。
- Arithmetic：每筆 `buy - sell = net`，外資、投信及自營商分別檢查。
- Missing symbol：行情或法人代號不在公司主檔，以及普通股在兩來源缺失的集合均輸出檢查結果。
- 完整性：完整交易日少於 120 天時命令回傳非零狀態，不產生誤導性的最終判斷。

## Observation Rule

報告只揭露資料品質、Reversal/Weakening 的 5D success、3D persistence、平均 breadth、Top3 concentration，以及法人組合每日產業座標的原始觀察。這些都是歷史觀測比例，不做趨勢判斷、不設策略門檻、不輸出 GO／MODIFY／NO-GO，也不構成投資建議。
