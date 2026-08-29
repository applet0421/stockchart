# Institutional Flow PoC 視覺化規格

最後更新：2026-08-29

## 視覺化原則

### 實作模組

- `rotation.py`：產生 Model A／B 座標、象限、trail 所需資料。
- `svg.py`：`render_rotation_svg(rows, institution, model)` 以 Python 標準函式庫輸出 SVG 散點、軸線、象限座標與最近 20 筆 trail。
- `pipeline.py`：依法人／組合呼叫 renderer，輸出各 `*_rotation_map.svg`。
- `observation.py`：產生每日產業觀察與最新快照 CSV，供圖表旁的可核對資料表使用。

目前不使用 Plotly、Matplotlib、ECharts、D3 或前端網站框架；SVG 是可直接檢查與封裝的靜態輸出。

- 所有圖表標示資料截止日、期間、法人組合與 Model。
- 顏色只表達原始象限或正負值，不使用「推薦」「看多」「看空」等語意。
- 預設允許切換 `foreign`、`trust`、`dealer`、`combined`、`all`；也接受 `+` 自由組合。
- 圖表旁保留可下載 CSV，避免視覺化取代原始資料。
- 圖表標示 `basis=shares` 或 `basis=amount`；amount 必須標註為收盤價估算金額。

## Rotation Map

每一張 Map 使用散點與歷史 trail：

- Model A：X＝5D Flow，Y＝1D Flow
- Model B：X＝20D Flow，Y＝5D Flow
- 原點為零流量；四象限名稱僅為資料座標分類：ACCUMULATING、WEAKENING、REVERSING、DISTRIBUTING。
- 點標示產業名稱；trail 依日期排序，至少可重建最近 5D／10D／20D。
- 外資、投信、自營商、合計與 All 分開輸出，避免不同分母混在同圖。

## Model A／B 並列圖

`rotation_model_comparison.svg` 使用雙面板呈現同一批最新交易日產業資料：左側為 Model A（5D × 1D），右側為 Model B（20D × 5D）。`rotation_model_comparison.csv` 保留兩套座標與象限欄位，僅供並列核對，不標註模型優劣。

## 產業觀察表

`latest_sector_observation.csv` 對應最新交易日，欄位包含 Flow 1D／5D／20D、Breadth、Top1／Top3 concentration、stock_count。表格可依法人組合、產業代碼排序或篩選，但不新增排名或訊號欄位。

## 法人並列表

`latest_institution_comparison.csv` 同列呈現外資、投信、自營商、combined、All 的 5D Flow、Breadth 與 Top3 concentration，供同一產業的數值對照。缺值應顯示為空值，不以零掩蓋來源缺口。

## 品質與追溯資訊

視覺化頁面或報告需顯示：完整交易日／需求日數、market／flow row count、duplicate、arithmetic failure、missing symbol，以及 `run_manifest.json` 的 generated_at、資料期間與來源檔雜湊。

## 禁止事項

不使用截斷座標軸誤導差異、不把歷史 5D success 或 3D persistence 顯示成預測機率、不將象限名稱轉成投資建議，也不隱藏自營商或組合的資料覆蓋差異。
