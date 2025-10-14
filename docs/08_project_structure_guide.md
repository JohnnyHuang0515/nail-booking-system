# 專案結構指南 - LINE 美甲預約系統

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-13`
**主要作者:** `技術負責人`
**狀態:** `活躍 (Active)`

---

## 1. 指南目的

為 LINE 美甲預約系統提供標準化的目錄與檔案結構，確保：
- 清晰的 DDD Bounded Context 邊界
- 前端三端（Admin、Merchant、LIFF）獨立開發
- Clean Architecture 分層一致
- 測試代碼易於維護

---

## 2. 核心設計原則

1. **按 Bounded Context 組織：** 每個領域獨立目錄
2. **Clean Architecture 分層：** Domain → Application → Infrastructure
3. **前端按角色分離：** Admin、Merchant、LIFF 各自獨立
4. **測試鏡像結構：** tests/ 結構對應 src/ 結構

---

## 3. 頂層目錄結構

```plaintext
nail-booking-system/
├── backend/                    # 後端服務
│   ├── src/
│   │   ├── identity/           # Identity & Access Context
│   │   ├── merchant/           # Merchant Context
│   │   ├── catalog/            # Catalog Context
│   │   ├── booking/            # Booking Context 🎯
│   │   ├── billing/            # Billing Context
│   │   ├── notification/       # Notification Context
│   │   ├── shared/             # 共享 Kernel
│   │   └── api/                # BFF Gateway
│   ├── tests/
│   │   ├── features/           # BDD Feature 檔案
│   │   ├── unit/               # 單元測試
│   │   ├── integration/        # 整合測試
│   │   └── e2e/                # 端到端測試
│   ├── migrations/             # Alembic 資料庫遷移
│   ├── scripts/                # 輔助腳本
│   └── pyproject.toml          # Python 專案定義
│
├── frontend/
│   ├── admin/                  # 管理員後台 (Next.js)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── features/
│   │   │   └── lib/
│   │   └── package.json
│   │
│   ├── merchant/               # 商家後台 (Next.js)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── features/
│   │   │   └── lib/
│   │   └── package.json
│   │
│   └── liff/                   # LINE LIFF (React)
│       ├── src/
│       │   ├── pages/
│       │   ├── components/
│       │   ├── features/
│       │   ├── hooks/
│       │   └── services/
│       └── package.json
│
├── docs/                       # 所有文檔
│   ├── 00_workflow_manual.md
│   ├── 01_development_workflow_cookbook.md
│   ├── 02_project_brief_and_prd.md
│   ├── ...
│   └── features/               # BDD Feature 檔案
│       ├── bookable_slots.feature
│       ├── create_booking.feature
│       └── ...
│
├── infra/                      # 基礎設施即代碼
│   ├── terraform/
│   ├── docker/
│   └── k8s/
│
├── .github/
│   └── workflows/              # CI/CD
│
└── README.md
```

---

## 4. 後端結構詳解

### 4.1 Booking Context（核心領域範例）

```plaintext
backend/src/booking/
├── __init__.py
│
├── domain/                     # Domain Layer
│   ├── __init__.py
│   ├── models.py              # 聚合根、實體
│   │   ├── class Booking      # 聚合根
│   │   ├── class BookingLock
│   │   └── class BookingItem  # 值物件
│   ├── value_objects.py       # 值物件
│   │   ├── class Money
│   │   └── class Duration
│   ├── events.py              # 領域事件
│   │   ├── BookingConfirmed
│   │   ├── BookingCancelled
│   │   └── BookingCompleted
│   ├── repositories.py        # Repository 介面（ABC）
│   │   └── class BookingRepository(ABC)
│   └── exceptions.py          # 領域異常
│       ├── BookingOverlapError
│       ├── InvalidStatusTransitionError
│       └── ...
│
├── application/                # Application Layer
│   ├── __init__.py
│   ├── services.py            # 應用服務 / Use Cases
│   │   └── class BookingService
│   ├── dtos.py                # Data Transfer Objects
│   │   ├── CreateBookingRequest
│   │   ├── BookingResponse
│   │   └── SlotResponse
│   └── validators.py          # 輸入驗證
│
└── infrastructure/             # Infrastructure Layer
    ├── __init__.py
    ├── orm/                   # SQLAlchemy ORM
    │   └── models.py          # ORM 模型
    │       ├── BookingORM
    │       └── BookingLockORM
    ├── repositories/          # Repository 實作
    │   └── sqlalchemy_booking_repository.py
    └── routers/               # FastAPI Routers
        ├── public_router.py   # /public/merchants/{slug}/slots
        ├── liff_router.py     # /liff/bookings
        └── merchant_router.py # /merchant/bookings
```

### 4.2 共享 Kernel (Shared Kernel)

```plaintext
backend/src/shared/
├── __init__.py
├── database.py                # SQLAlchemy Engine, Session
├── config.py                  # Pydantic Settings
├── security.py                # JWT, Password hashing
├── timezone.py                # 時區處理工具
├── event_bus.py               # 領域事件發布/訂閱
└── exceptions.py              # 基礎異常類別
```

### 4.3 API Gateway (BFF)

```plaintext
backend/src/api/
├── __init__.py
├── main.py                    # FastAPI App 入口
├── dependencies.py            # Dependency Injection
├── middleware/
│   ├── auth.py               # JWT 認證
│   ├── tenant.py             # 租戶識別
│   ├── rate_limit.py         # 速率限制
│   └── logging.py            # 結構化日誌
└── routers/
    ├── public.py
    ├── liff.py
    ├── merchant.py
    └── admin.py
```

---

## 5. 前端結構詳解

### 5.1 LIFF 客戶端（React）

```plaintext
frontend/liff/src/
├── pages/                     # 頁面
│   ├── BookingPage.tsx       # 預約頁面
│   ├── BookingDetailPage.tsx # 預約詳情
│   └── HistoryPage.tsx       # 歷史紀錄
│
├── features/                  # Feature-based 組織
│   ├── booking/
│   │   ├── components/
│   │   │   ├── SlotPicker.tsx
│   │   │   ├── ServiceSelector.tsx
│   │   │   └── BookingForm.tsx
│   │   ├── hooks/
│   │   │   ├── useAvailableSlots.ts
│   │   │   ├── useCreateBooking.ts
│   │   │   └── useCancelBooking.ts
│   │   ├── services/
│   │   │   └── bookingApi.ts
│   │   └── types/
│   │       └── booking.types.ts
│   │
│   └── merchant/
│       └── ...
│
├── components/                # 共享組件
│   ├── atoms/
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   ├── molecules/
│   │   └── TimeSlotCard.tsx
│   └── organisms/
│       └── CalendarView.tsx
│
├── hooks/                     # 共享 Hooks
│   ├── useLiff.ts
│   ├── useAuth.ts
│   └── useApi.ts
│
├── services/                  # API 客戶端
│   ├── apiClient.ts
│   └── auth.ts
│
├── stores/                    # Zustand Stores
│   ├── authStore.ts
│   └── bookingStore.ts
│
├── utils/                     # 工具函數
│   ├── datetime.ts
│   └── formatter.ts
│
└── App.tsx                    # 主應用
```

---

## 6. 測試結構

### 6.1 BDD Feature 檔案

```plaintext
backend/tests/features/
├── bookable_slots.feature
├── create_booking.feature
├── cancel_booking.feature
├── merchant_calendar.feature
├── subscription_billing.feature
└── steps/                     # 步驟定義
    ├── booking_steps.py
    ├── catalog_steps.py
    └── common_steps.py
```

### 6.2 單元測試

```plaintext
backend/tests/unit/
├── booking/
│   ├── test_booking_model.py
│   ├── test_booking_service.py
│   ├── test_value_objects.py
│   └── test_time_utils.py
├── catalog/
│   └── test_service_model.py
└── shared/
    └── test_timezone.py
```

### 6.3 整合測試

```plaintext
backend/tests/integration/
├── test_booking_repository.py     # 測試 ORM + DB
├── test_exclude_constraint.py     # 測試 EXCLUDE 約束
├── test_booking_api.py            # 測試 API 端點
└── test_line_notification.py     # 測試 LINE 推播（Mock）
```

---

## 7. 檔案命名約定

### 7.1 Python
- **模組：** `snake_case.py`
- **測試：** `test_snake_case.py`
- **類別：** `PascalCase`
- **函式：** `snake_case`

### 7.2 TypeScript/React
- **組件：** `PascalCase.tsx`
- **Hooks：** `useCamelCase.ts`
- **工具函數：** `camelCase.ts`
- **類型定義：** `camelCase.types.ts`

### 7.3 文檔
- **Markdown：** `kebab-case.md`
- **Feature：** `snake_case.feature`

---

## 8. 資料庫遷移

```plaintext
backend/migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_exclude_constraint.py
│   ├── 003_add_rls_policies.py
│   └── ...
└── alembic.ini
```

**遷移命名規範：**
```
{version}_{description}.py
```

**範例：**
```bash
# 生成遷移
alembic revision --autogenerate -m "add booking table"

# 執行遷移
alembic upgrade head

# 回滾
alembic downgrade -1
```

---

## 9. 環境配置

```plaintext
backend/
├── .env.example               # 環境變數範本
├── .env.development
├── .env.staging
└── .env.production            # ⚠️ 不加入版控
```

**.env.example:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nailbook
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# LINE
LINE_CHANNEL_SECRET=your-line-secret
LINE_CHANNEL_ACCESS_TOKEN=your-line-token

# AWS
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=nailbook-uploads
```

---

## 10. CI/CD 結構

```plaintext
.github/workflows/
├── backend-ci.yml             # 後端測試與部署
├── frontend-admin-ci.yml      # Admin 部署
├── frontend-merchant-ci.yml   # Merchant 部署
├── frontend-liff-ci.yml       # LIFF 部署
└── db-migrations.yml          # 資料庫遷移
```

---

## 11. Docker 結構

```plaintext
backend/
├── Dockerfile                 # 生產環境
├── Dockerfile.dev             # 開發環境
└── docker-compose.yml         # 本地開發

frontend/admin/
├── Dockerfile
└── .dockerignore

frontend/merchant/
├── Dockerfile
└── .dockerignore

frontend/liff/
├── Dockerfile
└── .dockerignore
```

---

## 12. 專案根目錄清潔度

**根目錄僅保留：**
```plaintext
nail-booking-system/
├── backend/
├── frontend/
├── docs/
├── infra/
├── .github/
├── .gitignore
├── README.md
├── LICENSE
└── Makefile                   # 常用指令集合
```

**Makefile 範例：**
```makefile
.PHONY: help backend-dev frontend-dev test

help:
	@echo "可用指令："
	@echo "  make backend-dev    - 啟動後端開發服務"
	@echo "  make frontend-dev   - 啟動前端開發服務"
	@echo "  make test           - 執行所有測試"
	@echo "  make migrate        - 執行資料庫遷移"

backend-dev:
	cd backend && uvicorn src.api.main:app --reload

frontend-dev:
	cd frontend/liff && npm run dev

test:
	cd backend && pytest tests/
	cd backend && behave features/

migrate:
	cd backend && alembic upgrade head
```

---

**記住：保持結構清晰比嚴格遵守某個模式更重要。隨專案演進調整。**

