# API 文檔

美甲預約系統的 RESTful API 文檔。

## 🔗 基礎 URL

- **開發環境**: `http://localhost:8000/api/v1`
- **生產環境**: `https://your-domain.com/api/v1`

## 🔐 認證

目前系統使用簡單的用戶認證，未來將整合 JWT 或 OAuth2。

## 📋 API 端點

### 用戶管理 (Users)

#### 登入/註冊
```http
POST /users/login
Content-Type: application/json

{
  "line_user_id": "string",
  "name": "string" (optional)
}
```

#### 獲取所有用戶
```http
GET /users
```

#### 獲取特定用戶
```http
GET /users/{user_id}
```

#### 創建用戶
```http
POST /users
Content-Type: application/json

{
  "line_user_id": "string",
  "name": "string",
  "phone": "string" (optional)
}
```

#### 更新用戶
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "name": "string",
  "phone": "string"
}
```

#### 刪除用戶
```http
DELETE /users/{user_id}
```

### 預約管理 (Appointments)

#### 獲取預約列表
```http
GET /appointments?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

#### 創建預約
```http
POST /appointments
Content-Type: application/json

{
  "user_id": "uuid",
  "service_id": "uuid",
  "appointment_date": "YYYY-MM-DD",
  "appointment_time": "HH:MM:SS"
}
```

#### 更新預約
```http
PUT /appointments/{appointment_id}
Content-Type: application/json

{
  "user_id": "uuid",
  "service_id": "uuid",
  "appointment_date": "YYYY-MM-DD",
  "appointment_time": "HH:MM:SS",
  "status": "BOOKED|CONFIRMED|COMPLETED|CANCELLED|NO_SHOW"
}
```

#### 更新預約狀態
```http
PUT /appointments/{appointment_id}/status
Content-Type: application/json

{
  "status": "BOOKED|CONFIRMED|COMPLETED|CANCELLED|NO_SHOW"
}
```

#### 刪除預約
```http
DELETE /appointments/{appointment_id}
```

### 服務管理 (Services)

#### 獲取服務列表
```http
GET /services
```

#### 創建服務
```http
POST /services
Content-Type: application/json

{
  "name": "string",
  "price": "number",
  "duration_minutes": "number",
  "is_active": "boolean"
}
```

#### 更新服務
```http
PUT /services/{service_id}
Content-Type: application/json

{
  "name": "string",
  "price": "number",
  "duration_minutes": "number",
  "is_active": "boolean"
}
```

#### 刪除服務
```http
DELETE /services/{service_id}
```

### 時段管理 (Schedule)

#### 獲取營業時間
```http
GET /schedule/business_hours
```

#### 設置營業時間
```http
POST /schedule/business_hours
Content-Type: application/json

[
  {
    "day_of_week": "number (0-6)",
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS"
  }
]
```

#### 獲取特定日期的休假
```http
GET /schedule/time_off?for_date=YYYY-MM-DD
```

#### 獲取所有休假
```http
GET /schedule/time_off/all
```

#### 新增休假
```http
POST /schedule/time_off
Content-Type: application/json

{
  "start_datetime": "YYYY-MM-DDTHH:MM:SS",
  "end_datetime": "YYYY-MM-DDTHH:MM:SS",
  "reason": "string" (optional)
}
```

#### 刪除休假
```http
DELETE /schedule/time_off/{time_off_id}
```

### 預約時段 (Booking)

#### 獲取可用時段
```http
GET /slots/{for_date}
```

### 儀表板 (Dashboard)

#### 獲取儀表板摘要
```http
GET /dashboard/summary
```

### 交易管理 (Transactions)

#### 獲取交易列表
```http
GET /transactions?user_id={user_id}&start_date={start_date}&end_date={end_date}
```

#### 獲取特定交易
```http
GET /transactions/{transaction_id}
```

#### 創建交易
```http
POST /transactions
Content-Type: application/json

{
  "user_id": "uuid",
  "appointment_id": "uuid",
  "amount": "number",
  "payment_method": "string",
  "status": "PENDING|COMPLETED|FAILED|REFUNDED"
}
```

#### 更新交易
```http
PUT /transactions/{transaction_id}
Content-Type: application/json

{
  "amount": "number",
  "payment_method": "string",
  "status": "PENDING|COMPLETED|FAILED|REFUNDED"
}
```

#### 刪除交易
```http
DELETE /transactions/{transaction_id}
```

#### 獲取用戶交易
```http
GET /users/{user_id}/transactions
```

## 📊 資料模型

### 用戶 (User)
```json
{
  "id": "uuid",
  "line_user_id": "string",
  "name": "string",
  "phone": "string"
}
```

### 預約 (Appointment)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "service_id": "uuid",
  "appointment_date": "YYYY-MM-DD",
  "appointment_time": "HH:MM:SS",
  "status": "BOOKED|CONFIRMED|COMPLETED|CANCELLED|NO_SHOW",
  "user": "User object",
  "service": "Service object"
}
```

### 服務 (Service)
```json
{
  "id": "uuid",
  "name": "string",
  "price": "number",
  "duration_minutes": "number",
  "is_active": "boolean"
}
```

### 營業時間 (BusinessHour)
```json
{
  "id": "uuid",
  "day_of_week": "number (0-6)",
  "start_time": "HH:MM:SS",
  "end_time": "HH:MM:SS"
}
```

### 休假 (TimeOff)
```json
{
  "id": "uuid",
  "start_datetime": "YYYY-MM-DDTHH:MM:SS",
  "end_datetime": "YYYY-MM-DDTHH:MM:SS",
  "reason": "string"
}
```

### 交易 (Transaction)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "appointment_id": "uuid",
  "amount": "number",
  "payment_method": "string",
  "status": "PENDING|COMPLETED|FAILED|REFUNDED",
  "created_at": "YYYY-MM-DDTHH:MM:SS"
}
```

## 🚨 錯誤處理

### 錯誤回應格式
```json
{
  "detail": "錯誤訊息",
  "status_code": "number"
}
```

### 常見錯誤碼
- `400` - 請求參數錯誤
- `401` - 未授權
- `403` - 禁止訪問
- `404` - 資源不存在
- `422` - 資料驗證失敗
- `500` - 伺服器內部錯誤

## 🔧 開發工具

### API 文檔
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 測試
```bash
# 運行 API 測試
pytest tests/api/v1/
```

## 📝 更新日誌

### v1.0.0 (2025-01-XX)
- 初始版本發布
- 完整的 CRUD API
- 用戶管理功能
- 預約管理功能
- 服務管理功能
- 時段管理功能
- 儀表板功能
- 交易管理功能
