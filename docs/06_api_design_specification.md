# API 設計規範 - LINE 美甲預約系統

---

**文件版本:** `v1.0.0`
**最後更新:** `2025-10-13`
**主要作者:** `API 設計師`
**審核者:** `後端團隊, 前端團隊`
**狀態:** `已批准 (Approved)`
**OpenAPI 定義:** `backend/openapi.yaml`

---

## 1. 引言 (Introduction)

### 1.1 目的
為 LINE 美甲預約系統的所有 API 消費者提供統一、明確的介面契約。

### 1.2 目標讀者
- LIFF 前端開發者
- Merchant Portal 開發者
- Admin Dashboard 開發者
- API 實作者
- QA 測試工程師

### 1.3 快速入門

```bash
# 1. 取得 JWT Token
curl -X POST https://api.nailbook.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 2. 使用 Token 查詢商家
curl -X GET https://api.nailbook.com/v1/public/merchants/nail-abc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 2. 設計原則與約定

### 2.1 API 風格
**風格:** RESTful + Domain-Driven Design

### 2.2 基本 URL
- **生產環境:** `https://api.nailbook.com/v1`
- **預備環境:** `https://staging-api.nailbook.com/v1`
- **開發環境:** `http://localhost:8000/v1`

### 2.3 請求與回應格式
**格式:** `application/json` (UTF-8)

**標準回應結構：**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "request_id": "req_abc123"
}
```

### 2.4 標準 HTTP Headers

**所有請求：**
- `Authorization: Bearer <JWT_TOKEN>`
- `X-Request-ID: <UUID>` (可選，用於追蹤)
- `X-Merchant-ID: <merchant_id>` (Merchant/LIFF 端點必須)

**所有回應：**
- `X-Request-ID: <UUID>`
- `X-RateLimit-Limit: 100`
- `X-RateLimit-Remaining: 95`
- `X-RateLimit-Reset: 1697184000`

### 2.5 命名約定
- **資源路徑:** 小寫，複數形式（`/bookings`）
- **查詢參數:** `snake_case`（`start_date`, `staff_id`）
- **JSON 欄位:** `snake_case`

### 2.6 日期與時間格式
**標準格式:** ISO 8601 with UTC offset

```json
{
  "start_at": "2025-10-16T14:00:00+08:00",
  "created_at": "2025-10-13T10:30:00Z"
}
```

---

## 3. 認證與授權

### 3.1 認證機制

**JWT Bearer Token:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token 結構：**
```json
{
  "sub": "user_123",
  "merchant_id": 456,
  "scope": "merchant",
  "roles": ["owner", "manager"],
  "exp": 1697270400
}
```

### 3.2 授權範圍 (Scopes)

| Scope | 權限 | 適用端點 |
|-------|------|---------|
| `admin` | 系統管理、建立商家 | `/admin/*` |
| `merchant` | 管理預約、員工、服務 | `/merchant/*` |
| `liff` | 建立/取消預約、查詢 | `/liff/*` |
| `public` | 公開查詢 | `/public/*` |

---

## 4. 通用 API 行為

### 4.1 分頁

**查詢參數：**
- `page`: 頁碼（從 1 開始）
- `page_size`: 每頁筆數（預設 25，最大 100）

**回應結構：**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 150,
    "total_pages": 6
  }
}
```

### 4.2 排序
**查詢參數:** `sort_by=field_name` (升序), `sort_by=-field_name` (降序)

**範例：**
```
GET /merchant/bookings?sort_by=-start_at
```

### 4.3 過濾
**使用欄位名作為參數：**
```
GET /merchant/bookings?status=confirmed&staff_id=5
GET /merchant/bookings?start_date=2025-10-16&end_date=2025-10-20
```

### 4.4 冪等性
**支援 Idempotency-Key Header：**
```http
POST /liff/bookings
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

伺服器將在 24 小時內對相同 Key 返回相同結果。

---

## 5. 錯誤處理

### 5.1 標準錯誤回應

```json
{
  "success": false,
  "error": {
    "code": "booking_overlap",
    "message": "所選時段已被預約",
    "details": {
      "staff_id": 5,
      "conflicting_booking_id": 123,
      "start_at": "2025-10-16T14:00:00+08:00"
    }
  },
  "request_id": "req_xyz789"
}
```

### 5.2 錯誤碼字典

| Error Code | HTTP Status | 描述 | 可重試 |
|------------|-------------|------|--------|
| `booking_overlap` | 409 Conflict | 時段已被預約 | ✅ 可選其他時段 |
| `staff_inactive` | 400 Bad Request | 員工已停用 | ❌ |
| `merchant_inactive` | 403 Forbidden | 商家已停用 | ❌ |
| `subscription_past_due` | 403 Forbidden | 訂閱逾期 | ❌ 需付款 |
| `invalid_time_range` | 400 Bad Request | 無效的時間範圍 | ❌ |
| `service_not_found` | 404 Not Found | 服務不存在 | ❌ |
| `unauthorized` | 401 Unauthorized | 未認證 | ❌ 需登入 |
| `permission_denied` | 403 Forbidden | 無權限 | ❌ |
| `rate_limit_exceeded` | 429 Too Many Requests | 超出速率限制 | ✅ 稍後重試 |
| `internal_server_error` | 500 Internal Server Error | 伺服器錯誤 | ✅ 可重試 |

---

## 6. 安全性考量

### 6.1 傳輸層安全
- 強制 HTTPS (TLS 1.3)
- HSTS Header: `max-age=31536000; includeSubDomains`

### 6.2 HTTP 安全 Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### 6.3 速率限制

| 層級 | 限制 | 窗口 |
|------|------|------|
| IP | 100 req/min | 滑動窗口 |
| User (JWT) | 300 req/min | 滑動窗口 |
| Endpoint: POST /bookings | 10 req/min | 滑動窗口 |

**超出限制回應：**
```json
{
  "success": false,
  "error": {
    "code": "rate_limit_exceeded",
    "message": "請求過於頻繁，請稍後再試",
    "retry_after": 30
  }
}
```

---

## 7. API 端點詳述

### 7.1 公開端點 (Public APIs)

#### `GET /public/merchants/{slug}`

**描述：** 取得商家公開資訊

**路徑參數：**
- `slug`: 商家唯一識別碼（字串）

**回應範例（200 OK）：**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "slug": "nail-abc",
    "name": "ABC 美甲沙龍",
    "address": "台北市信義區...",
    "phone": "02-1234-5678",
    "line_bot_basic_id": "@abc123",
    "timezone": "Asia/Taipei",
    "services": [
      {
        "id": 1,
        "name": "凝膠指甲",
        "base_price": 800,
        "base_duration_min": 60
      }
    ],
    "staffs": [
      {
        "id": 1,
        "name": "Amy",
        "avatar_url": "https://..."
      }
    ]
  }
}
```

#### `GET /public/merchants/{slug}/slots` 🎯

**描述：** 查詢可預約時段（核心端點）

**查詢參數：**
- `date`: 日期（YYYY-MM-DD）**必須**
- `staff_id`: 員工 ID（int）可選
- `service_ids`: 服務 ID 陣列（int[]）可選

**範例請求：**
```
GET /public/merchants/nail-abc/slots?date=2025-10-16&staff_id=1&service_ids=1,2
```

**回應範例（200 OK）：**
```json
{
  "success": true,
  "data": {
    "date": "2025-10-16",
    "staff_id": 1,
    "staff_name": "Amy",
    "slots": [
      {
        "start_time": "10:00",
        "end_time": "11:00",
        "available": true
      },
      {
        "start_time": "10:30",
        "end_time": "11:30",
        "available": true
      },
      {
        "start_time": "14:00",
        "end_time": "15:00",
        "available": false,
        "reason": "已被預約"
      }
    ],
    "working_hours": {
      "start": "10:00",
      "end": "18:00"
    }
  }
}
```

---

### 7.2 LIFF 客戶端點

#### `POST /liff/bookings` 🎯

**描述：** 建立預約（核心端點）

**認證：** JWT (scope=liff)

**請求體：**
```json
{
  "merchant_slug": "nail-abc",
  "customer": {
    "line_user_id": "U1234567890abcdef",
    "name": "王小明",
    "phone": "0912345678"
  },
  "staff_id": 1,
  "start_at": "2025-10-16T14:00:00+08:00",
  "items": [
    {
      "service_id": 1,
      "option_ids": [2, 3]
    }
  ],
  "notes": "希望使用粉色系"
}
```

**成功回應（201 Created）：**
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "status": "confirmed",
    "merchant_name": "ABC 美甲沙龍",
    "staff_name": "Amy",
    "start_at": "2025-10-16T14:00:00+08:00",
    "end_at": "2025-10-16T15:15:00+08:00",
    "items": [
      {
        "service_name": "凝膠指甲",
        "service_price": 800,
        "service_duration_min": 60,
        "options": [
          {"name": "法式", "add_price": 200, "add_duration_min": 15}
        ]
      }
    ],
    "total_price": {
      "amount": 1000,
      "currency": "TWD"
    },
    "total_duration_min": 75,
    "created_at": "2025-10-13T10:30:00Z"
  },
  "message": "預約成功，已發送 LINE 通知"
}
```

**錯誤回應範例：**

**409 Conflict（時段衝突）：**
```json
{
  "success": false,
  "error": {
    "code": "booking_overlap",
    "message": "所選時段已被預約，請選擇其他時間",
    "details": {
      "staff_id": 1,
      "staff_name": "Amy",
      "conflicting_slot": {
        "start_at": "2025-10-16T14:00:00+08:00",
        "end_at": "2025-10-16T15:00:00+08:00"
      },
      "suggested_slots": [
        {"start_time": "10:00", "end_time": "11:15"},
        {"start_time": "16:00", "end_time": "17:15"}
      ]
    }
  }
}
```

**403 Forbidden（訂閱逾期）：**
```json
{
  "success": false,
  "error": {
    "code": "subscription_past_due",
    "message": "商家訂閱已逾期，暫時無法接受預約",
    "details": {
      "merchant_id": 123,
      "subscription_status": "past_due"
    }
  }
}
```

#### `DELETE /liff/bookings/{booking_id}`

**描述：** 取消預約

**路徑參數：**
- `booking_id`: 預約 ID（int）

**成功回應（200 OK）：**
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "status": "cancelled",
    "cancelled_at": "2025-10-13T11:00:00Z"
  },
  "message": "預約已取消，已發送 LINE 通知"
}
```

**錯誤回應範例（400 Bad Request）：**
```json
{
  "success": false,
  "error": {
    "code": "cannot_cancel_completed",
    "message": "已完成的預約無法取消"
  }
}
```

---

### 7.3 商家端點 (Merchant APIs)

#### `GET /merchant/bookings`

**描述：** 查詢商家預約列表

**認證：** JWT (scope=merchant)

**查詢參數：**
- `start_date`: 開始日期（YYYY-MM-DD）可選
- `end_date`: 結束日期（YYYY-MM-DD）可選
- `staff_id`: 篩選員工（int）可選
- `status`: 篩選狀態（string）可選
- `page`: 頁碼（int）預設 1
- `page_size`: 每頁筆數（int）預設 25

**範例請求：**
```
GET /merchant/bookings?start_date=2025-10-16&end_date=2025-10-20&staff_id=1&status=confirmed
```

**回應範例：**
```json
{
  "success": true,
  "data": [
    {
      "id": 12345,
      "customer": {
        "line_user_id": "U123...",
        "name": "王小明",
        "phone": "0912345678"
      },
      "staff": {
        "id": 1,
        "name": "Amy"
      },
      "status": "confirmed",
      "start_at": "2025-10-16T14:00:00+08:00",
      "end_at": "2025-10-16T15:15:00+08:00",
      "services": ["凝膠指甲", "法式（選項）"],
      "total_price": 1000,
      "created_at": "2025-10-13T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 45,
    "total_pages": 2
  }
}
```

#### `GET /merchant/calendar`

**描述：** 日曆檢視（關鍵查詢）

**查詢參數：**
- `start_date`: 開始日期（YYYY-MM-DD）**必須**
- `end_date`: 結束日期（YYYY-MM-DD）**必須**
- `staff_id`: 篩選員工（int）可選

**回應範例：**
```json
{
  "success": true,
  "data": {
    "start_date": "2025-10-16",
    "end_date": "2025-10-20",
    "events": [
      {
        "id": 12345,
        "type": "booking",
        "title": "王小明 - 凝膠指甲",
        "start": "2025-10-16T14:00:00+08:00",
        "end": "2025-10-16T15:15:00+08:00",
        "staff": {"id": 1, "name": "Amy"},
        "status": "confirmed",
        "color": "#4caf50"
      },
      {
        "id": 2,
        "type": "working_hours",
        "title": "Amy 上班時間",
        "start": "2025-10-16T10:00:00+08:00",
        "end": "2025-10-16T18:00:00+08:00",
        "staff": {"id": 1, "name": "Amy"},
        "color": "#e0e0e0"
      }
    ]
  }
}
```

---

### 7.4 管理員端點 (Admin APIs)

#### `POST /admin/merchants`

**描述：** 建立新商家

**認證：** JWT (scope=admin)

**請求體：**
```json
{
  "slug": "nail-xyz",
  "name": "XYZ 美甲工作室",
  "email": "owner@nail-xyz.com",
  "phone": "02-8765-4321",
  "address": "台北市大安區...",
  "line_channel_id": "1234567890",
  "line_channel_secret": "abc123...",
  "line_channel_access_token": "xyz789...",
  "timezone": "Asia/Taipei"
}
```

**成功回應（201 Created）：**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "slug": "nail-xyz",
    "name": "XYZ 美甲工作室",
    "status": "active",
    "created_at": "2025-10-13T12:00:00Z",
    "api_key": "sk_live_abc123..."
  }
}
```

#### `POST /admin/merchants/{merchant_id}/subscribe`

**描述：** 為商家啟用訂閱

**路徑參數：**
- `merchant_id`: 商家 ID（int）

**請求體：**
```json
{
  "plan_id": 1,
  "payment_method": "credit_card",
  "billing_interval": "monthly"
}
```

**成功回應（200 OK）：**
```json
{
  "success": true,
  "data": {
    "subscription_id": 789,
    "merchant_id": 456,
    "plan_name": "專業版",
    "status": "active",
    "current_period_start": "2025-10-13T00:00:00Z",
    "current_period_end": "2025-11-13T00:00:00Z",
    "next_billing_date": "2025-11-13"
  }
}
```

---

## 8. Webhook 端點

### 8.1 計費 Webhook

**端點：** `POST /webhooks/billing/stripe`

**描述：** 接收 Stripe 計費事件

**Headers：**
- `Stripe-Signature: <HMAC_SHA256>`

**請求體範例：**
```json
{
  "type": "invoice.paid",
  "data": {
    "object": {
      "id": "in_123",
      "customer": "cus_456",
      "amount_paid": 999,
      "status": "paid"
    }
  }
}
```

**處理邏輯：**
1. 驗證 Stripe 簽章
2. 找到對應的 Invoice
3. 更新狀態為 `paid`
4. 發布 `InvoicePaid` 事件
5. 更新 Subscription 狀態為 `active`

### 8.2 LINE Webhook

**端點：** `POST /webhooks/line/callback`

**描述：** 接收 LINE 事件（如用戶加入好友）

---

## 9. 資料模型 Schema 定義

### 9.1 Booking

```typescript
interface Booking {
  id: number;
  merchant_id: number;
  customer: {
    line_user_id: string;
    name?: string;
    phone?: string;
  };
  staff_id: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  start_at: string;  // ISO 8601
  end_at: string;
  items: BookingItem[];
  total_price: {
    amount: number;
    currency: string;
  };
  total_duration_min: number;
  notes?: string;
  created_at: string;
  confirmed_at?: string;
  cancelled_at?: string;
  completed_at?: string;
}

interface BookingItem {
  service_id: number;
  service_name: string;
  service_price: number;
  service_duration_min: number;
  option_ids: number[];
  option_names: string[];
  option_prices: number[];
  option_durations_min: number[];
}
```

### 9.2 Service

```typescript
interface Service {
  id: number;
  merchant_id: number;
  name: string;
  description?: string;
  base_price: number;
  base_duration_min: number;
  is_active: boolean;
  allow_stack: boolean;
  options: ServiceOption[];
}

interface ServiceOption {
  id: number;
  service_id: number;
  name: string;
  add_price: number;
  add_duration_min: number;
  is_active: boolean;
}
```

---

## 10. API 生命週期與版本控制

### 10.1 版本控制策略
**策略：** URL 路徑版本控制（`/v1/...`）

**變更類型：**
- **向後相容：** 新增可選參數、新增回應欄位
- **破壞性變更：** 刪除欄位、修改型別 → 需升版至 v2

### 10.2 棄用策略
1. 提前 3 個月公告
2. 在回應中加入 `Deprecation` Header
3. 提供遷移指南
4. 保留舊版本 6 個月

---

## 11. 效能指標與 SLO

### 11.1 Service Level Objectives

| 端點類別 | SLO | 衡量方式 |
|---------|-----|----------|
| GET /slots | P95 < 200ms | Prometheus histogram |
| POST /bookings | P95 < 300ms | Prometheus histogram |
| GET /calendar | P95 < 200ms | Prometheus histogram |
| 整體可用性 | > 99.9% | Uptime monitoring |

### 11.2 錯誤預算

**每月可容許停機時間：** 43.2 分鐘
**錯誤率預算：** 0.1%（每 1000 次請求允許 1 次失敗）

---

**簽核記錄:**

| 角色 | 姓名 | 日期 | 狀態 |
|------|------|------|------|
| API 設計委員會 | API Design Board | 2025-10-13 | ✅ 批准 |
| 前端團隊 | Frontend Lead | 2025-10-13 | ✅ 批准 |
| 後端團隊 | Backend Lead | 2025-10-13 | ✅ 批准 |

