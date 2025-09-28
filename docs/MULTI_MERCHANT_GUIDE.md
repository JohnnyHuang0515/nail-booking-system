# 多商家美甲預約系統 - 完整指南

## 概述

本系統已成功升級為支援多商家、多個 LINE 官方帳號的美甲預約系統。每個商家擁有獨立的 LINE 官方帳號，系統能自動識別並路由到正確的商家，實現完全的資料隔離。

## 系統架構

### 核心特性

1. **多租戶架構**：每個商家資料完全隔離
2. **多 LINE 帳號支援**：每個商家使用獨立的 LINE Channel
3. **自動路由**：Webhook 自動識別商家並設定正確上下文
4. **資料隔離**：所有資料操作都基於 merchant_id 進行隔離
5. **彈性擴展**：支援新增商家和分店

### 技術架構

```
LINE Platform (多個 Channel)
    ↓
API Gateway/Nginx
    ↓
FastAPI Application
    ↓
Middleware (商家識別 + 上下文設定)
    ↓
Business Logic (多租戶)
    ↓
PostgreSQL (Row Level Security)
```

## 資料庫架構

### 新增的商家表

```sql
CREATE TABLE merchants (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    line_channel_id VARCHAR(64) UNIQUE NOT NULL,
    line_channel_secret VARCHAR(64) NOT NULL,
    line_channel_access_token TEXT NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Asia/Taipei',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 多租戶約束

所有業務表都增加了 `merchant_id` 欄位：

- `users`: UNIQUE(merchant_id, line_user_id)
- `services`: UNIQUE(merchant_id, name)
- `appointments`: UNIQUE(merchant_id, branch_id, appointment_date, appointment_time, staff_id)
- `transactions`: 強綁 merchant_id
- `business_hours`: 每商家獨立設定
- `time_off`: 每商家獨立管理

## API 端點

### 商家管理 API

```bash
# 創建商家
POST /api/v1/merchants
{
    "name": "台北美甲店",
    "line_channel_id": "your_channel_id",
    "line_channel_secret": "your_channel_secret",
    "line_channel_access_token": "your_access_token",
    "timezone": "Asia/Taipei"
}

# 列出所有商家
GET /api/v1/merchants

# 更新商家
PUT /api/v1/merchants/{merchant_id}

# 更新憑證
PUT /api/v1/merchants/{merchant_id}/credentials

# 停用商家
DELETE /api/v1/merchants/{merchant_id}
```

### 多租戶業務 API

所有業務 API 都需要指定 `merchant_id`：

```bash
# 服務管理
GET /api/v1/services?merchant_id={merchant_id}
POST /api/v1/services
{
    "merchant_id": "merchant_uuid",
    "name": "法式美甲",
    "price": 1200,
    "duration_minutes": 90
}

# 預約管理
GET /api/v1/appointments?merchant_id={merchant_id}
POST /api/v1/appointments
{
    "merchant_id": "merchant_uuid",
    "user_id": "user_uuid",
    "service_id": "service_uuid",
    "appointment_date": "2024-01-15",
    "appointment_time": "14:00"
}
```

### LINE Webhook

```bash
POST /api/v1/line/webhook
Headers:
    X-Line-Signature: {signature}
    X-Line-Channel-Id: {channel_id}  # 可選，用於商家識別

Body: LINE Webhook 事件
```

## LINE 互動流程

### 1. 用戶關注

```
用戶關注 LINE 帳號
    ↓
LINE 發送 follow 事件到 Webhook
    ↓
中介軟體識別商家（根據 Channel ID）
    ↓
設定商家上下文
    ↓
創建或取得用戶記錄
    ↓
發送歡迎訊息（使用商家專屬 token）
```

### 2. 預約流程

```
用戶發送文字訊息
    ↓
識別商家並設定上下文
    ↓
顯示服務選擇 Flex Message
    ↓
用戶選擇服務
    ↓
顯示日期時間選擇
    ↓
確認預約
    ↓
發送預約確認 Flex Message
```

### 3. Flex Message 模板

系統提供多種 Flex Message 模板：

- **歡迎訊息**：新用戶關注時顯示
- **服務選擇**：顯示可用服務列表
- **預約確認**：預約成功後的確認訊息
- **預約提醒**：預約前一天的提醒
- **取消確認**：預約取消的確認

## 部署指南

### 1. 環境設置

```bash
# 複製環境變數模板
cp .env.example .env

# 編輯環境變數
DATABASE_URL=postgresql://user:password@localhost/nail_booking
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

### 2. 資料庫遷移

```bash
# 運行遷移腳本
python migrate_to_multi_merchant.py

# 或使用設置腳本
python setup_multi_merchant.py
```

### 3. 啟動應用

```bash
# 使用啟動腳本
./start_multi_merchant.sh

# 或手動啟動
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 查看日誌
docker-compose logs -f app
```

## LINE 設定

### 1. 創建 LINE Channel

1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 為每個商家創建新的 Provider 和 Channel
3. 取得 Channel ID、Channel Secret、Access Token

### 2. Webhook 設定

1. 設定 Webhook URL：`https://yourdomain.com/api/v1/line/webhook`
2. 啟用 Webhook
3. 設定回應模式為「Bot」

### 3. 商家註冊

使用商家管理 API 註冊每個商家：

```bash
curl -X POST "http://localhost:8000/api/v1/merchants" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "台北美甲店",
       "line_channel_id": "your_channel_id",
       "line_channel_secret": "your_channel_secret",
       "line_channel_access_token": "your_access_token"
     }'
```

## 監控與維護

### 1. 日誌監控

```bash
# 查看應用日誌
tail -f logs/app.log

# 查看錯誤日誌
grep "ERROR" logs/app.log
```

### 2. 資料庫監控

```sql
-- 查看商家統計
SELECT 
    m.name,
    COUNT(DISTINCT u.id) as user_count,
    COUNT(DISTINCT a.id) as appointment_count,
    SUM(t.amount) as total_revenue
FROM merchants m
LEFT JOIN users u ON m.id = u.merchant_id
LEFT JOIN appointments a ON m.id = a.merchant_id
LEFT JOIN transactions t ON m.id = t.merchant_id
GROUP BY m.id, m.name;
```

### 3. 性能監控

系統提供內建的性能監控：

- API 響應時間
- 資料庫查詢性能
- LINE API 調用統計
- 錯誤率監控

## 安全考量

### 1. 資料隔離

- 所有查詢都必須包含 merchant_id
- 使用 Row Level Security (RLS) 確保資料隔離
- 請求上下文自動設定，防止跨商家存取

### 2. 憑證管理

- LINE 憑證加密儲存
- 支援憑證輪替
- 定期檢查憑證有效性

### 3. 安全驗證

- LINE Webhook 簽名驗證
- API 速率限制
- 敏感資料加密

## 擴展功能

### 1. 分店支援

系統已預留分店支援：

```python
# 創建分店相關的預約
appointment = {
    "merchant_id": "merchant_uuid",
    "branch_id": "branch_uuid",  # 可選分店ID
    "user_id": "user_uuid",
    "service_id": "service_uuid",
    # ...
}
```

### 2. 員工管理

支援員工排班和預約分配：

```python
appointment = {
    "staff_id": "staff_uuid",  # 可選員工ID
    # ...
}
```

### 3. 多語言支援

Flex Message 模板支援多語言：

```python
# 根據用戶語言偏好選擇模板
template = FlexTemplates.appointment_confirmation(
    language="zh-TW",  # 或 "en", "ja" 等
    # ...
)
```

## 故障排除

### 常見問題

1. **Webhook 驗證失敗**
   - 檢查 Channel Secret 是否正確
   - 確認 Webhook URL 設定正確

2. **商家上下文未設定**
   - 檢查中介軟體是否正確載入
   - 確認 Channel ID 能正確識別商家

3. **資料隔離問題**
   - 檢查所有查詢是否包含 merchant_id
   - 確認 Repository 方法使用正確的篩選條件

### 除錯工具

```python
# 檢查商家上下文
from app.context import RequestContext
merchant_id = RequestContext.get_merchant_id()
print(f"Current merchant: {merchant_id}")

# 檢查 LINE 客戶端
from app.line_client import get_line_client
client = get_line_client()
```

## 性能優化

### 1. 資料庫優化

- 為 merchant_id 建立索引
- 使用適當的查詢優化
- 考慮讀寫分離

### 2. 快取策略

- Redis 快取商家資訊
- 快取 LINE 用戶資料
- 快取服務列表

### 3. 負載均衡

- 使用 Nginx 進行負載均衡
- 考慮多實例部署
- 監控系統資源使用

## 總結

多商家美甲預約系統已成功實現，具備以下核心能力：

✅ **多租戶架構**：完全資料隔離
✅ **多 LINE 帳號**：每個商家獨立 Channel
✅ **自動路由**：智能識別商家
✅ **完整 API**：商家管理和業務操作
✅ **Flex 模板**：豐富的 LINE 互動
✅ **排程提醒**：自動化預約管理
✅ **安全防護**：多重安全機制
✅ **易於部署**：完整的部署方案

系統已準備好投入生產使用，可根據業務需求進一步擴展功能。
