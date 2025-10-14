# LINE 美甲預約系統 - 後端

> **架構方法論**：DDD × BDD × TDD  
> **框架**：FastAPI + SQLAlchemy + PostgreSQL  
> **測試**：Pytest + Behave

---

## 🏗️ 架構總覽

### Bounded Contexts (6個領域)
```
src/
├── identity/      # Identity & Access Context
├── merchant/      # Merchant Context
├── catalog/       # Catalog Context
├── booking/       # Booking Context 🎯 (已實作)
├── billing/       # Billing Context
├── notification/  # Notification Context
├── shared/        # Shared Kernel
└── api/           # BFF Gateway
```

### Clean Architecture 三層
```
Infrastructure Layer (FastAPI, SQLAlchemy, LINE SDK)
        ↓
Application Layer (Use Cases, Services)
        ↓
Domain Layer (Aggregates, Value Objects) ⭐ 純淨無依賴
```

---

## 🚀 快速開始

### 1. 安裝依賴
```bash
cd backend

# 使用 Poetry（推薦）
poetry install

# 或使用 pip
pip install -r requirements.txt
```

### 2. 設定環境變數
```bash
# 複製範例檔案
cp .env.example .env

# 編輯 .env，設定資料庫連線等
vim .env
```

### 3. 執行資料庫遷移
```bash
# 確保 PostgreSQL 已啟動
# 確保已安裝 btree_gist extension

# 執行遷移
alembic upgrade head

# 驗證 EXCLUDE 約束
psql -d nail_booking -c "\d booking_locks"
```

### 4. 啟動開發服務器
```bash
# 使用 uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# API 文檔
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

---

## 🧪 執行測試

### 單元測試（TDD）
```bash
# 執行所有單元測試
pytest tests/unit/ -v

# 執行特定模組測試
pytest tests/unit/booking/ -v

# 生成覆蓋率報告
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### BDD 測試
```bash
# 執行所有 Feature
behave tests/features/

# 執行特定 Feature
behave tests/features/create_booking.feature

# 顯示詳細步驟
behave tests/features/ --no-capture
```

### 整合測試
```bash
# 需要真實的 PostgreSQL
pytest tests/integration/ -v
```

---

## 📋 開發指令

### 資料庫管理
```bash
# 建立新遷移
alembic revision --autogenerate -m "add new table"

# 升級到最新版本
alembic upgrade head

# 回滾一個版本
alembic downgrade -1

# 查看遷移歷史
alembic history
```

### 代碼品質
```bash
# 格式化代碼
black src/ tests/

# Linting
ruff check src/

# 型別檢查
mypy src/
```

---

## 🎯 Booking Context 開發狀態

### ✅ 已完成
- [x] Domain Layer（Booking 聚合、值物件、事件）
- [x] Application Layer（BookingService、DTOs）
- [x] Infrastructure Layer（ORM、Repository、LIFF Router）
- [x] 資料庫 Schema（含 EXCLUDE 約束）
- [x] BDD Feature 檔案
- [x] TDD 單元測試骨架

### ⏳ 待完成
- [ ] Catalog Context 整合（服務/員工/工時查詢）
- [ ] Merchant Context 整合（商家狀態驗證）
- [ ] Billing Context 整合（訂閱狀態檢查）
- [ ] Notification Handler（LINE 推播）
- [ ] BDD 步驟定義實作
- [ ] 整合測試（含 EXCLUDE 約束驗證）
- [ ] API 認證中介層

---

## 🔑 關鍵不變式

> **這些不變式由測試保護，任何違反都是 P0 Bug：**

1. ✅ **同一員工同時間無重疊** - PostgreSQL EXCLUDE 約束保證
2. ✅ **total_price = Σ(item.total_price())** - Domain 計算邏輯保證
3. ✅ **total_duration = Σ(item.total_duration())** - Domain 計算邏輯保證
4. ✅ **end_at = start_at + total_duration** - Domain 屬性保證
5. ⏳ **訂閱逾期禁止新預約** - 待 Billing Context 實作
6. ⏳ **商家 active 才可預約** - 待 Merchant Context 實作

---

## 📚 參考文檔

- **API 規範**：`../docs/06_api_design_specification.md`
- **架構設計**：`../docs/05_architecture_and_design_document.md`
- **模組規格**：`../docs/07_module_specification_and_tests.md`
- **BDD 指南**：`../docs/03_behavior_driven_development_guide.md`
- **ADR-002**：`../docs/04_architecture_decision_record_002_exclude_constraint.md`

---

## 🐛 已知問題

1. **Catalog Service Mock**：`BookingService._build_booking_items_mock` 使用假資料，待 Catalog Context 實作後替換
2. **認證缺失**：API 端點尚未實作 JWT 認證中介層
3. **事件處理**：EventBus 為記憶體版本，生產環境應替換為 Celery

---

## 💡 開發提示

### 遵循 Linus 哲學
- ✅ 資料結構優先於算法
- ✅ 消除特殊情況（用好的資料結構）
- ✅ 簡潔勝於複雜（避免超過3層縮排）
- ✅ 實用主義（解決真實問題）

### 遵循 Clean Architecture
- ✅ Domain Layer 不依賴任何外部框架
- ✅ Application Layer 依賴 Domain 介面
- ✅ Infrastructure Layer 實作 Domain 介面

### 遵循 DDD
- ✅ 所有變更通過聚合根
- ✅ 跨聚合用領域事件
- ✅ 不變式在 Domain 內保護

---

**開發者：VibeCoding Team**  
**文檔版本：v0.1.0**

