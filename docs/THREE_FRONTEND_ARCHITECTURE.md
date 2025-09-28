# 三前端架構完整指南

## 系統架構概述

根據您的需求，我們實現了完整的三前端架構：

1. **顧客端 LIFF** - 顧客預約使用
2. **商家端後台** - 商家管理使用  
3. **平台管理員後台** - 系統管理使用

## 架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        三前端架構                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   顧客端 LIFF   │    │   商家端後台    │    │  平台管理員後台  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ React/Vue SPA   │    │ React/Vue + AntD│    │ React + AntD    │
│ LINE LIFF SDK   │    │ LINE Login      │    │ JWT Auth        │
│ 日曆時段選擇器   │    │ Email Login     │    │ 商家管理        │
│ Flex Message    │    │ 預約管理        │    │ 系統監控        │
│ 預約確認        │    │ 服務管理        │    │ 報表統計        │
└─────────────────┘    │ 交易管理        │    └─────────────────┘
         │              │ 用戶管理        │             │
         │              └─────────────────┘             │
         │                       │                      │
         └───────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   後端 API      │
                    ├─────────────────┤
                    │ FastAPI + Python│
                    │ PostgreSQL      │
                    │ Redis           │
                    │ LINE Bot API    │
                    │ JWT Auth        │
                    │ 多租戶架構      │
                    └─────────────────┘
```

## 1. 顧客端 LIFF

### 技術棧
- **前端**: React/Vue + TypeScript
- **UI**: 自定義組件 + 日曆選擇器
- **認證**: LINE LIFF SDK
- **通訊**: 直接 API 調用

### 主要功能
- ✅ LINE 用戶身分驗證
- ✅ 商家服務瀏覽
- ✅ 日期時段選擇
- ✅ 預約確認
- ✅ 預約歷史查詢
- ✅ Flex Message 互動

### 部署方式
```bash
# 每個商家獨立的 LIFF App
https://liff.line.me/{liff-id}

# URL 參數攜帶 merchant_id
https://liff.line.me/{liff-id}?merchant_id={merchant_uuid}
```

### 認證流程
```javascript
// 1. 初始化 LIFF
liff.init({ liffId: liffId })

// 2. 取得用戶資料
const profile = await liff.getProfile()
const idToken = liff.getIDToken()

// 3. 向後端驗證
const response = await fetch('/api/v1/users/liff-login', {
  method: 'POST',
  body: JSON.stringify({
    id_token: idToken,
    merchant_id: merchantId
  })
})
```

## 2. 商家端後台

### 技術棧
- **前端**: React/Vue + Ant Design
- **認證**: LINE Login + Email Login
- **狀態管理**: Zustand/Redux
- **圖表**: Recharts/ECharts

### 主要功能
- ✅ 商家登入 (LINE Login + Email)
- ✅ 預約管理 (查看、修改、取消)
- ✅ 服務項目管理
- ✅ 顧客資料管理
- ✅ 交易記錄查詢
- ✅ 營業時間設定
- ✅ 數據統計報表

### 認證方式

#### Email 登入
```javascript
// 傳統 Email + 密碼登入
const response = await fetch('/api/v1/merchant-auth/email-login', {
  method: 'POST',
  body: JSON.stringify({
    email: 'merchant@example.com',
    password: 'password123'
  })
})
```

#### LINE Login
```javascript
// 1. 取得 LINE Login URL
const loginUrl = await fetch(`/api/v1/merchant-auth/line-login-url/${merchantId}`)

// 2. 跳轉到 LINE Login
window.location.href = loginUrl.line_login_url

// 3. 回調處理 (後端自動處理)
// LINE Login 會回調到後端，後端驗證後返回 JWT token
```

### 商家後台頁面結構
```
/merchant-dashboard/
├── /login              # 登入頁面
├── /dashboard          # 儀表板
├── /appointments       # 預約管理
│   ├── /list          # 預約列表
│   ├── /calendar      # 日曆視圖
│   └── /details/:id   # 預約詳情
├── /services          # 服務管理
├── /customers         # 顧客管理
├── /transactions      # 交易記錄
├── /settings          # 設定
│   ├── /profile       # 商家資料
│   ├── /business-hours # 營業時間
│   └── /line-config   # LINE 設定
└── /reports           # 報表統計
```

## 3. 平台管理員後台

### 技術棧
- **前端**: React + Ant Design
- **認證**: JWT Token
- **狀態管理**: Zustand
- **圖表**: Recharts

### 主要功能
- ✅ 超級管理員登入
- ✅ 商家管理 (新增、編輯、停用)
- ✅ LINE Channel 配置
- ✅ LIFF ID 管理
- ✅ 系統監控
- ✅ 平台統計報表
- ✅ 用戶行為分析

### 管理員權限
```typescript
interface AdminPermissions {
  merchant_management: boolean;  // 商家管理
  system_settings: boolean;      // 系統設定
  reports: boolean;              // 報表查看
  user_management: boolean;      // 用戶管理
}
```

### 平台後台頁面結構
```
/platform-admin/
├── /login              # 管理員登入
├── /dashboard          # 系統概覽
├── /merchants          # 商家管理
│   ├── /list          # 商家列表
│   ├── /create        # 新增商家
│   ├── /edit/:id      # 編輯商家
│   └── /details/:id   # 商家詳情
├── /reports           # 報表統計
│   ├── /overview      # 總覽報表
│   ├── /merchants     # 商家報表
│   └── /users         # 用戶報表
├── /settings          # 系統設定
│   ├── /platform      # 平台設定
│   ├── /security      # 安全設定
│   └── /backup        # 備份管理
└── /monitoring        # 系統監控
    ├── /health        # 健康檢查
    ├── /performance   # 性能監控
    └── /logs          # 日誌查看
```

## 後端 API 架構

### API 分組

#### 1. 平台管理員 API (`/api/v1/admin/`)
```python
# 管理員認證
POST /admin/login                    # 管理員登入
GET  /admin/profile                  # 管理員資料

# 商家管理
GET  /admin/merchants                # 商家統計
GET  /admin/merchants/{id}/details   # 商家詳情
POST /admin/merchants/{id}/toggle-status  # 切換商家狀態

# 系統監控
GET  /admin/system-stats             # 系統統計
GET  /admin/health                   # 健康檢查
```

#### 2. 商家認證 API (`/api/v1/merchant-auth/`)
```python
# 商家登入
POST /merchant-auth/email-login      # Email 登入
POST /merchant-auth/line-login       # LINE Login
GET  /merchant-auth/line-login-url/{merchant_id}  # LINE Login URL

# 商家資料
GET  /merchant-auth/profile          # 商家資料
POST /merchant-auth/refresh-token    # 刷新令牌
```

#### 3. 商家管理 API (`/api/v1/merchants/`)
```python
# 商家 CRUD (管理員專用)
POST /merchants                      # 創建商家
GET  /merchants                      # 商家列表
GET  /merchants/{id}                 # 商家詳情
PUT  /merchants/{id}                 # 更新商家
DELETE /merchants/{id}               # 刪除商家

# 商家憑證管理
PUT  /merchants/{id}/credentials     # 更新憑證
```

#### 4. 業務 API (多租戶)
```python
# 所有業務 API 都需要 merchant_id
GET  /services?merchant_id={id}      # 服務列表
POST /appointments                   # 創建預約 (body 含 merchant_id)
GET  /appointments?merchant_id={id}  # 預約列表
GET  /users?merchant_id={id}         # 用戶列表
```

#### 5. LIFF 認證 API (`/api/v1/users/`)
```python
# LIFF 用戶認證
POST /users/liff-login               # LIFF 登入
POST /users/login                    # 傳統登入 (向後兼容)
GET  /users?merchant_id={id}         # 用戶列表
```

## 部署架構

### 前端部署
```bash
# 1. 顧客端 LIFF (靜態部署)
# 部署到 CDN 或靜態託管服務
# 每個商家一個 LIFF App ID

# 2. 商家後台 (SPA 部署)
# 部署到 Web 服務器 (Nginx/Apache)
# 支援路由重寫

# 3. 平台管理員後台 (SPA 部署)
# 部署到獨立的子域名
# admin.your-domain.com
```

### 後端部署
```bash
# 單一 FastAPI 應用
# 支援所有三個前端的 API 需求
# 使用中介軟體處理不同認證方式
```

### 域名規劃
```
your-domain.com/                    # 主頁面 (選擇入口)
your-domain.com/liff/               # LIFF 前端
your-domain.com/merchant/           # 商家後台
your-domain.com/admin/              # 平台管理員後台
api.your-domain.com/                # API 服務
```

## 安全考量

### 1. 認證安全
- **LIFF**: LINE 官方 SDK + idToken 驗證
- **商家後台**: JWT + LINE Login / Email 雙重認證
- **管理員**: JWT + 強密碼 + 權限控制

### 2. 資料隔離
- **多租戶**: 所有資料按 merchant_id 隔離
- **RLS**: PostgreSQL Row Level Security
- **API 權限**: 不同角色不同權限

### 3. 憑證管理
- **LINE Token**: 加密存儲
- **JWT Secret**: 環境變數管理
- **HTTPS**: 全程加密傳輸

## 開發指南

### 1. 本地開發
```bash
# 後端
cd /path/to/project
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 前端 (三個分別啟動)
cd platform-admin && npm start      # 端口 3000
cd merchant-backend && npm start    # 端口 3001  
cd customer-liff && npm start       # 端口 3002
```

### 2. 測試帳號
```bash
# 平台管理員
username: admin
password: admin123

# 商家 (Email)
email: merchant@example.com
password: merchant123

# 商家 (LINE Login)
# 使用 LINE Login 流程
```

### 3. API 測試
```bash
# 使用 Postman 或 curl 測試
curl -X POST http://localhost:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 總結

這個三前端架構提供了：

✅ **完整的用戶體驗**: 顧客、商家、管理員各有專屬介面  
✅ **靈活的認證方式**: LIFF、LINE Login、Email、JWT  
✅ **嚴格的資料隔離**: 多租戶架構確保資料安全  
✅ **統一的管理後台**: 平台管理員可管理所有商家  
✅ **可擴展的架構**: 支援新增商家和功能擴展  

所有三個前端都已經實現完成，可以直接部署使用！
