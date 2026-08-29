# TWSE Field Mapping

最後更新：2026-08-29

| Layer | Canonical | TWSE source | Raw field / derivation |
|---|---|---|---|
| stocks | symbol | t187ap03_L | 公司代號 |
| stocks | name | t187ap03_L | 公司簡稱 |
| stocks | industry_code | t187ap03_L | 產業別 |
| stocks | industry_name | TWSE industry code table | 產業別代碼 mapping |
| stocks | market | fixed | TWSE |
| stocks | listed_date | t187ap03_L | 上市日期，ROC/compact date 正規化 |
| stocks | issued_common_shares | t187ap03_L | 已發行普通股數或TDR原股發行股數 |
| stocks | source_report_date | t187ap03_L | 出表日期 |
| daily_market | date | MI_INDEX | response date |
| daily_market | symbol | MI_INDEX 每日收盤行情 | 證券代號 |
| daily_market | name | MI_INDEX 每日收盤行情 | 證券名稱 |
| daily_market | volume | MI_INDEX 每日收盤行情 | 成交股數 |
| daily_market | trade_count | MI_INDEX 每日收盤行情 | 成交筆數 |
| daily_market | turnover | MI_INDEX 每日收盤行情 | 成交金額 |
| daily_market | open/high/low/close | MI_INDEX 每日收盤行情 | 開盤價／最高價／最低價／收盤價 |
| daily_market | price_change | MI_INDEX 每日收盤行情 | 漲跌價差 |
| daily_market | pe_ratio | MI_INDEX 每日收盤行情 | 本益比 |
| institutional_flow | date | T86 | response date |
| institutional_flow | symbol/name | T86 | 證券代號／證券名稱 |
| institutional_flow | foreign_buy/sell/net | T86 | 外陸資買進／賣出／買賣超股數（不含外資自營商） |
| institutional_flow | trust_buy/sell/net | T86 | 投信買進／賣出／買賣超股數 |
| institutional_flow | dealer_buy/sell/net | T86 | 自營商買進／賣出／買賣超股數（自行買賣＋避險） |
| institutional_flow | source_missing | T86 × MI_INDEX | T86 未列但行情存在時為 true，法人欄位補零且缺口仍可追蹤 |
| stock_flow | `{institution}_flow_{N}d` | derived | 同股票最近 N 日 sum(net) / sum(volume) |
| sector_flow | flow_{N}d | derived | 產業股票最近 N 日 sum(net) / sum(volume) |
| sector_flow | breadth_{N}d | derived | N 日 net > 0 股票數 / 有效股票數 |
| sector_flow | top1/top3_concentration_{N}d | derived | 最大 1/3 檔 abs(N日 net) / sum(abs(N日 net)) |
| rotation | model_a_x/y | derived | 5D Flow / 1D Flow |
| rotation | model_b_x/y | derived | 20D Flow / 5D Flow |

## Observation outputs

| Output | Fields | Meaning |
|---|---|---|
| sector_observation_daily.csv | date, institution (`foreign`, `trust`, `dealer`, `combined`, `all`), industry_code, sector, flow_1d/5d/20d, breadth_5d, top1/top3_concentration_5d, stock_count_5d | 每日產業與法人原始觀察欄位；組合直接以成員 net 相加後計算 |
| institution_comparison_daily.csv | date, sector, industry_code, foreign/trust/dealer/combined/all flow_5d, breadth_5d, top3_concentration_5d | 同一產業同日的外資、投信、自營商與組合並列資料 |
| combined_rotation.csv | 與 foreign_rotation.csv 相同 rotation 欄位 | 外資＋投信合計的 Model A／B 觀察資料 |
| dealer_rotation.csv / all_rotation.csv | 與 foreign_rotation.csv 相同 rotation 欄位 | 自營商／外資＋投信＋自營商的 Model A／B 觀察資料 |
| quality_observation_daily.csv | date, market_row_count, flow_row_count, missing_in_flow_count, duplicate_count, arithmetic_failure_count, success | 每日來源完整性與品質檢查 |
| latest_sector_observation.csv | sector_observation_daily 的最新交易日欄位 | 最新交易日的五組法人觀察快照 |
| latest_institution_comparison.csv | institution_comparison_daily 的最新交易日欄位 | 最新交易日外資／投信／自營商與組合並列快照 |
| run_manifest.json | run_id, generated_at, source_urls, date_min/date_max, row_counts, files[].sha256 | 執行期間、來源、筆數與輸出檔雜湊追溯 |
