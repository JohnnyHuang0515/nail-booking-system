# 產品開發流程使用說明書 (Dual-Mode: Full Process / Lean MVP)

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `[VibeCoding AI]`
**狀態 (Status):** `活躍 (Active)`

---

## 專案概述

**專案名稱：** LINE 美甲預約系統
**專案類型：** 多租戶 SaaS 預約平台
**開發模式：** MVP 快速迭代（後續可升級至完整流程）

---

## 模式選擇：MVP 快速迭代

### 選擇理由
1. **時間壓力：** 需快速驗證市場需求
2. **核心功能明確：** 預約系統邊界清晰
3. **技術風險可控：** 基於成熟技術棧
4. **可迭代性高：** 允許逐步完善

### 升級觸發條件
- [ ] 月活用戶 > 10,000
- [ ] 商家數量 > 100
- [ ] 需處理金流與訂閱計費（已涉及）
- [ ] 跨團隊協作需求增加

---

## MVP 核心交付物

### 1. MVP Tech Spec
**檔案位置：** `docs/mvp_tech_spec.md`
**內容包含：**
- 問題陳述與目標用戶
- 高層設計（6 個 Bounded Context）
- API 契約（核心端點）
- 資料表 Schema
- 前端範圍與路由
- 風險與替代方案

### 2. 開發進度報告
**檔案位置：** `docs/development_progress_report.md`
**更新頻率：** 每週
**內容包含：**
- 總體進度概覽
- Gantt 時間軸
- 功能開發狀態
- 前端開發進度
- 關鍵技術指標
- 技術債務與風險

### 3. MVP 上線檢查清單
**檔案位置：** `docs/mvp_launch_checklist.md`
**檢查項目：**
- [ ] 備份策略已啟用
- [ ] `/health` 端點可用
- [ ] 核心錯誤日誌接入告警
- [ ] Runbook 完成並演練
- [ ] Secrets 已移至配置中心

---

## DDD × BDD × TDD 整合流程

### 階段 1：領域建模（DDD）
1. 定義 Ubiquitous Language
2. 劃分 6 個 Bounded Context
3. 設計聚合與不變式
4. 產出領域事件

**產出文檔：**
- `docs/05_architecture_and_design_document.md`
- `docs/04_architecture_decision_record_*.md`

### 階段 2：行為規格（BDD）
1. 將使用者故事轉為 Gherkin Feature
2. 定義 Given-When-Then 場景
3. 建立步驟定義骨架

**產出文檔：**
- `docs/03_behavior_driven_development_guide.md`
- `features/*.feature` 檔案

### 階段 3：測試驅動（TDD）
1. 紅：寫失敗測試
2. 綠：最小實作通過
3. 重構：優化設計

**產出文檔：**
- `docs/07_module_specification_and_tests.md`
- `tests/` 目錄下的測試檔案

---

## 關鍵決策記錄（ADR 索引）

| ADR ID | 標題 | 狀態 | 日期 |
|--------|------|------|------|
| ADR-001 | 選擇 PostgreSQL 作為主資料庫 | Accepted | 2025-10-13 |
| ADR-002 | 使用 EXCLUDE 約束防止預約重疊 | Accepted | 2025-10-13 |
| ADR-003 | 採用 FastAPI 作為後端框架 | Accepted | 2025-10-13 |
| ADR-004 | 前端使用 Next.js + React | Accepted | 2025-10-13 |
| ADR-005 | 多租戶隔離策略 | Accepted | 2025-10-13 |

---

## 品質門檻（Gate Criteria）

### MVP 上線前必須通過
- [ ] 核心預約流程 E2E 測試通過
- [ ] 無重疊預約的 DB 約束測試通過
- [ ] LINE 推播功能正常
- [ ] 訂閱計費 Webhook 驗證通過
- [ ] 安全掃描無高危漏洞
- [ ] 效能測試：預約建立 P95 < 300ms

### 持續監控指標
- 預約成功率 > 99%
- API 錯誤率 < 0.1%
- LINE 推播成功率 > 95%
- 資料庫查詢 P95 < 200ms

---

## 風險管理

### 高風險項目
1. **LINE API 限制**
   - 緩解：快取推播結果，實施重試機制
   
2. **預約衝突處理**
   - 緩解：使用 PG EXCLUDE 約束 + 樂觀鎖

3. **多租戶資料隔離**
   - 緩解：RLS 策略 + 應用層驗證

### 技術債務追蹤
- [ ] 前端狀態管理需重構（暫用 Context）
- [ ] 推播服務需獨立為微服務
- [ ] 需建立完整的 E2E 測試套件

---

## 參考文檔架構

```
docs/
├── 00_workflow_manual.md                    # 本文檔
├── 01_development_workflow_cookbook.md      # 開發流程指南
├── 02_project_brief_and_prd.md              # PRD
├── 03_behavior_driven_development_guide.md  # BDD 指南
├── 04_architecture_decision_record_*.md     # ADR 系列
├── 05_architecture_and_design_document.md   # 架構設計
├── 06_api_design_specification.md           # API 規格
├── 07_module_specification_and_tests.md     # 模組規格
├── 08_project_structure_guide.md            # 專案結構
├── 09_file_dependencies_template.md         # 依賴分析
├── 10_class_relationships_template.md       # 類別關係
├── 11_code_review_and_refactoring_guide.md  # Code Review
├── 12_frontend_architecture_specification.md # 前端架構
├── 13_security_and_readiness_checklists.md  # 安全檢查
├── 14_deployment_and_operations_guide.md    # 部署運維
├── 15_documentation_and_maintenance_guide.md # 文檔維護
├── 16_wbs_development_plan_template.md      # WBS 計劃
└── 17_frontend_information_architecture_template.md # 前端 IA
```

---

## 下一步行動

1. **Week 1-2：** 完成核心 DDD 設計與 BDD Feature
2. **Week 3-4：** 實作預約核心功能 + TDD
3. **Week 5：** 前端三端開發
4. **Week 6：** 整合測試與上線準備

