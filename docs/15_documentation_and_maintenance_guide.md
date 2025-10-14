# 文檔與維護指南 - LINE 美甲預約系統

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-13`
**狀態:** `活躍 (Active)`

---

## 📖 文檔類型總覽

### 1. API 文檔

**OpenAPI/Swagger：**
- **位置：** `backend/openapi.yaml`
- **自動生成：** FastAPI 自動生成
- **存取網址：** `https://api.nailbook.com/docs`

**更新流程：**
1. 修改 FastAPI router 的 docstring 和型別提示
2. FastAPI 自動更新 OpenAPI spec
3. Redoc 即時反映變更

**範例：**
```python
@router.post(
    "/liff/bookings",
    response_model=BookingResponse,
    status_code=201,
    summary="建立預約",
    description="客戶透過 LIFF 建立預約，系統自動檢查時段衝突並發送 LINE 通知。",
    responses={
        201: {"description": "預約建立成功"},
        409: {"description": "時段衝突"},
        403: {"description": "訂閱逾期"}
    }
)
async def create_booking(request: CreateBookingRequest):
    """
    建立新預約
    
    ## 前置條件
    - 商家狀態為 active
    - 員工狀態為 active
    - 所選時段無衝突
    
    ## 業務規則
    - 自動計算總價與總時長
    - 建立 booking_lock 防止重疊
    - 發送 LINE 推播通知
    
    ## 錯誤處理
    - 409: 時段已被預約，返回建議時段
    - 403: 商家訂閱逾期
    """
    pass
```

---

### 2. 架構文檔

**文檔清單：**

| 文檔 | 路徑 | 更新頻率 | 負責人 |
|------|------|----------|--------|
| Workflow Manual | docs/00_workflow_manual.md | 每季 | PM |
| PRD | docs/02_project_brief_and_prd.md | 需求變更時 | PM |
| BDD Guide | docs/03_behavior_driven_development_guide.md | 新 Feature 時 | TL |
| Architecture | docs/05_architecture_and_design_document.md | 架構變更時 | Architect |
| API Spec | docs/06_api_design_specification.md | API 變更時 | Backend Lead |

---

### 3. BDD Feature 文檔（活文檔）

**位置：** `backend/tests/features/*.feature`

**維護原則：**
1. **Feature 即規格：** Feature 檔案是業務規格的單一事實來源
2. **可執行性：** 每個 Scenario 都應可執行並通過
3. **與程式碼同步：** Feature 變更需同步更新 Step Definitions

**範例：**
```gherkin
# features/create_booking.feature
Feature: 建立預約
  作為客戶，我想透過 LINE 建立預約，以便快速預訂服務
  
  @critical @documented
  Scenario: 成功建立預約並收到通知
    Given 商家 "nail-abc" 狀態為 active
    And 員工 "Amy" 在 2025-10-16 工作時間為 10:00-18:00
    When 我建立預約於 2025-10-16T14:00+08:00
    Then 預約狀態為 confirmed
    And 我在 2 秒內收到 LINE 通知
```

**執行與報告：**
```bash
# 執行 BDD 測試並生成 HTML 報告
behave features/ --format html --outfile reports/bdd-report.html

# 在 CI 中執行
behave features/ --tags=critical --format json --outfile bdd-results.json
```

---

## 📝 文檔標準

### README 模板

**專案根目錄 README.md：**
```markdown
# LINE 美甲預約系統

## 專案簡介
多租戶 SaaS 預約平台，整合 LINE Messaging API，為美甲產業提供數位化預約管理解決方案。

## 核心功能
- ✅ LINE LIFF 客戶預約
- ✅ 商家預約日曆管理
- ✅ 自動防止時段衝突（PostgreSQL EXCLUDE 約束）
- ✅ LINE 推播通知
- ✅ 訂閱計費管理

## 技術棧
- **後端：** Python 3.11 + FastAPI + SQLAlchemy + PostgreSQL 14
- **前端：** Next.js 14 + React 18 + TypeScript
- **部署：** AWS ECS Fargate + RDS Multi-AZ
- **監控：** Grafana + Prometheus + Loki

## 快速開始

### 後端
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.api.main:app --reload
```

### 前端（LIFF）
```bash
cd frontend/liff
pnpm install
pnpm dev
```

## 文檔
- 📚 [完整文檔](./docs/)
- 🔧 [API 文檔](https://api.nailbook.com/docs)
- 🏗️ [架構設計](./docs/05_architecture_and_design_document.md)

## 聯絡
- **Tech Lead:** backend@nailbook.com
- **Issues:** [GitHub Issues](https://github.com/...)
```

---

## 🔄 文檔維護

### 月度維護任務

- [ ] 檢查所有文檔準確性
- [ ] 更新 API 變更紀錄（CHANGELOG）
- [ ] 更新架構圖（若有變更）
- [ ] 檢查外部連結有效性
- [ ] 更新效能基準數據

### 季度維護任務

- [ ] 完整架構文檔審計
- [ ] 重新評估 ADR 決策
- [ ] 更新 Runbook
- [ ] 分析文檔使用指標（Page Views）
- [ ] 收集團隊回饋並改進

---

## 📊 文檔指標

### 追蹤項目

```javascript
{
  "api_docs_views": 1200,  // 月度瀏覽次數
  "bdd_features": 12,      // Feature 檔案數量
  "bdd_scenarios": 45,     // Scenario 總數
  "architecture_docs": 18, // 架構文檔數量
  "adr_count": 11,         // ADR 數量
  "docs_freshness": {
    "< 30_days": 15,
    "30-90_days": 3,
    "> 90_days": 0
  }
}
```

---

## 🛠️ 自動化文檔生成

### OpenAPI 文檔部署

```yaml
# .github/workflows/docs-deploy.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths: ['backend/src/api/**', 'docs/**']

jobs:
  deploy-api-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate OpenAPI spec
        run: |
          cd backend
          python scripts/generate_openapi.py > openapi.yaml
      
      - name: Deploy to S3
        run: |
          aws s3 cp openapi.yaml s3://nailbook-docs/openapi.yaml
          aws s3 sync docs/ s3://nailbook-docs/architecture/
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id $CF_DIST_ID \
            --paths "/*"
```

---

## 📚 知識管理

### Wiki 結構

**GitHub Wiki：**
```
Home
├── Getting Started
│   ├── Local Development Setup
│   ├── Running Tests
│   └── Contributing Guide
├── Architecture
│   ├── System Overview
│   ├── DDD Bounded Contexts
│   └── Database Schema
├── Deployment
│   ├── Deployment Process
│   ├── Rollback Procedures
│   └── Monitoring Guide
└── Troubleshooting
    ├── Common Issues
    └── FAQ
```

### 內部知識庫（Notion）

**結構：**
- **產品需求：** PRD、User Stories
- **技術設計：** ADR、Architecture Docs
- **會議紀錄：** Weekly Sync、Design Review
- **最佳實踐：** Coding Standards、Design Patterns
- **Post-mortem：** 事故報告與改進

---

## 🎯 文檔品質標準

### Checklist

- [ ] 標題清晰且具描述性
- [ ] 使用階層式標題（H2, H3）
- [ ] 包含程式碼範例（可執行）
- [ ] 圖表使用 Mermaid（可版本控制）
- [ ] 日期與版本號正確
- [ ] 所有連結有效
- [ ] 錯別字檢查（語法工具）

### Markdown Linting

```bash
# 安裝 markdownlint
pnpm install -g markdownlint-cli

# 檢查文檔
markdownlint docs/**/*.md

# 自動修復
markdownlint --fix docs/**/*.md
```

---

## 🔗 相關資源

### 外部參考
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [PostgreSQL 14 文檔](https://www.postgresql.org/docs/14/)
- [LINE LIFF 文檔](https://developers.line.biz/en/docs/liff/)
- [DDD Reference (Eric Evans)](https://www.domainlanguage.com/ddd/)

### 內部資源
- **Slack Channels:**
  - #engineering: 技術討論
  - #incidents: 事故處理
  - #deployments: 部署通知
- **Monitoring:** https://grafana.nailbook.com
- **Error Tracking:** https://sentry.io/nailbook
- **Status Page:** https://status.nailbook.com

---

**Remember:** 好的文檔是團隊效率與知識傳承的關鍵投資。

