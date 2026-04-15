# house-ops

[English](README.md) | [繁體中文](README-TW.md)

基於 Claude Code 的 AI 找房管線。自動化物件發掘、評估與追蹤，涵蓋從掃描房屋平台、根據預算與生活需求進行結構化評估，到追蹤所有考慮過的物件的完整搜尋流程。

Fork 自 [kylinfish/tw-house-ops](https://github.com/kylinfish/tw-house-ops)（台灣版），本 fork 新增多國支援與多項改進。

支援三種使用者類型：**租屋族**、**首購族**、**換屋族**。

---

## 分支

| 分支 | 國家 | 平台 | 幣別 |
|------|------|------|------|
| `main` | 台灣 | 591、樂屋網、信義、永慶、東森、住商 | TWD |
| `ireland` | 愛爾蘭 | Daft.ie、MyHome.ie、Property.ie、SherryFitzGerald、Lisney | EUR |

## 相較上游的改進

### 瀏覽器自動化
- **`agent-browser` → `playwright-cli` 遷移** — 每次工作階段減少 4 倍 token 使用量，快照存到磁碟而非灌入 context window，由 Microsoft 維護
- **Daft.ie API 整合**（`daft-scan.py`）— 直接呼叫內部 API 完全繞過 Cloudflare CAPTCHA，回傳完整資料（BER 評級、面積、GPS 座標、價格歷史）

### 管線增強
- **PDF 報告生成** — 透過 `md-to-pdf` 將評估報告匯出至 `output/`，可離線檢閱
- **API 優先掃描** — 有 API 的平台（如 Daft.ie gateway API）直接呼叫，比瀏覽器爬取更快更穩定

### 愛爾蘭分支（`ireland`）
- 完整適配愛爾蘭房屋市場：EUR/m²、BER 能源評級、央行房貸規則（首購 4 倍 / 換屋 3.5 倍）、Help to Buy、First Home Scheme、印花稅、資本利得稅、RPZ、RTB
- 愛爾蘭平台：Daft.ie、MyHome.ie、Property.ie、SherryFitzGerald、Lisney
- 都柏林交通：Luas、DART、Dublin Bus、Irish Rail
- 物件風險標記：pyrite、mica、石棉、未經許可的擴建
- Property Price Register（PPR）作為市場比較來源

---

## 功能

- **掃描** 各房屋平台，搜尋符合條件的物件
- **評估** 每間物件：市場行情比較、通勤計算、五維度評分
- **追蹤** 所有考慮過的物件，以結構化 Markdown 表格記錄
- **試算** 可負擔房價與財務規劃
- **準備** 根據評估報告產生看屋清單與議價策略
- **匯出** 報告為 PDF

---

## 事前準備

掃描與物件驗證依賴 `playwright-cli`：

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

愛爾蘭分支另需安裝 Daft.ie 掃描器：

```bash
pip install daftlistings requests
```

---

## 快速開始

1. 安裝上述工具
2. Clone 此 repo 並在 Claude Code 中開啟
3. Claude 會自動偵測缺少的設定檔，啟動初始設定流程（7 個步驟，約 5 分鐘）
4. 設定完成後，貼上任何物件 URL 即可評估——或輸入 `scan` 搜尋目標區域

---

## 用法

| 輸入 | 動作 |
|------|------|
| 貼上物件 URL | 自動判斷租屋 / 買屋 → 評估 → 產生報告 |
| `scan` | 在目標區域掃描各平台的新物件 |
| `pipeline` | 批次處理 `data/pipeline.md` 中所有待評估 URL |
| `compare 001, 003` | 並列比較兩間已評估物件 |
| `prepare visit for 001` | 產生報告 001 的看屋清單與議價策略 |
| `affordability` | 試算可負擔房價 |
| `upgrade plan` / `move plan` | 換屋規劃：賣舊買新時程、稅務、資金缺口分析 |
| `tracker` | 顯示所有追蹤物件的摘要 |

---

## 評分標準

物件依五個維度評分 0–5：

| 維度 | 租屋權重 | 買屋權重 |
|------|----------|----------|
| 價格合理性 | 30% | 35% |
| 空間與格局 | 20% | 20% |
| 區域生活機能 | 25% | 20% |
| 物件條件 | 15% | 15% |
| 風險與潛力 | 10% | 10% |

分數判讀：≥4.0 → 推薦看屋 | 3.5–3.9 → 持保留態度 | <3.5 → 建議跳過

---

## 追蹤表狀態

`Scanned` → `Evaluated` → `Visit` → `Visited` → `Offer` → `Negotiating` → `Signed` → `Done`

另有：`Skip`（篩除）、`Pass`（看後放棄）、`Expired`（物件已下架）

---

## 資料合約

**使用者層**（永遠不會被自動覆寫）：`config/profile.yml`、`modes/_profile.md`、`data/*`、`reports/*`、`output/*`

**系統層**（可能隨系統更新）：所有 mode 檔案、`CLAUDE.md`、`*.mjs` 腳本、`templates/*`

---

## 腳本

```bash
node merge-tracker.mjs           # 合併待新增 TSV 至 tracker.md
node verify-pipeline.mjs         # 檢查 pipeline 完整性
node dedup-tracker.mjs           # 移除重複追蹤條目
python daft-scan.py --help       # Daft.ie API 掃描器（愛爾蘭分支）
```

---

## 致謝

- 原始專案：[kylinfish/tw-house-ops](https://github.com/kylinfish/tw-house-ops) — 本 fork 基於此台灣找房管線
- 靈感來源：[santifer/career-ops](https://github.com/santifer/career-ops) — 將 ops 方法論應用於人生決策

---

## 使用原則

本系統以精準找房為目標，非大量瀏覽。Claude 不會代替你送出 offer、簽約或送出任何申請。評分低於 3.5/5 的物件將被明確建議不值得追蹤。

---

## 支持這個專案

如果這個工具對你的找房過程有幫助：

[![Sponsor](https://img.shields.io/badge/Sponsor-silver2dream-ea4aaa?logo=github-sponsors)](https://github.com/sponsors/silver2dream)

也歡迎支持原作者：[kylinfish on Ko-fi](https://ko-fi.com/kylinwin)
