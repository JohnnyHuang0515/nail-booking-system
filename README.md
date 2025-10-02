# 美甲預約系統

多租戶美甲預約管理系統，支援商家管理、客戶預約和平台管理員功能。

## 系統特色

- 🏢 **多租戶架構** - 支援多商家獨立運營
- 📱 **LINE 整合** - 支援 LINE LIFF 和 Rich Menu，包含憑證驗證
- 🔐 **安全治理** - RBAC 權限控制、審計軌跡
- 📊 **智能監控** - 系統健康檢查、業務報表
- 🚀 **一鍵部署** - 完整的啟動腳本和部署方案
- 💰 **帳務管理** - 完整的商家帳務和計費系統

## 專案結構

```
美甲預約系統/
├── app/                          # 後端 API 服務
│   ├── api/v1/endpoints/         # API 端點
│   ├── infrastructure/           # 資料庫和基礎設施
│   ├── services/                 # 業務邏輯服務
│   └── main.py                   # FastAPI 應用入口
├── frontend/
│   ├── admin-panel/              # 商家後台 (端口 3000)
│   └── customer-booking/         # 客戶預約 (端口 3001)
├── platform-admin/               # 平台管理員 (端口 3002)
├── scripts/                      # 啟動和部署腳本
├── docs/                         # 系統文檔
├── archive/                      # 歷史檔案備份
└── requirements.txt              # Python 依賴
```

## 系統架構

### 前端應用
- **商家後台** (`frontend/admin-panel`) - 商家管理介面
- **客戶預約** (`customer-booking`) - 客戶預約介面  
- **平台管理員** (`platform-admin`) - 平台管理介面

### 後端服務
- **FastAPI 後端** (`app/`) - RESTful API 服務
- **PostgreSQL 資料庫** - 多租戶資料存儲

## 快速開始

### 1. 環境準備
```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝前端依賴
cd frontend/admin-panel && npm install
cd ../customer-booking && npm install
cd ../../platform-admin && npm install
```

### 2. 啟動服務

**一鍵啟動所有服務（推薦）**
```bash
./scripts/start_all.sh
```

此腳本會自動：
- 檢查必要工具（Python3、Node.js、npm、Docker）
- 啟動 PostgreSQL 資料庫容器
- 啟動後端 API 服務
- 啟動三個前端應用
- 顯示所有服務訪問地址

### 3. 訪問應用
- **商家後台**: http://localhost:3000 - 商家管理介面
- **客戶預約**: http://localhost:3001 - 客戶預約介面
- **平台管理員**: http://localhost:3002 - 平台管理介面
- **API 文檔**: http://localhost:8000/docs - Swagger API 文檔
- **後端 API**: http://localhost:8000 - RESTful API 服務

### 4. 停止服務
```bash
# 按 Ctrl+C 停止所有服務
# 腳本會詢問是否同時停止資料庫容器
```

## 專案結構

```
美甲預約系統/
├── app/                    # 後端 API 服務
│   ├── api/               # API 路由
│   ├── services/          # 業務邏輯
│   ├── models/            # 資料模型
│   └── infrastructure/    # 基礎設施
├── frontend/              # 前端應用
│   └── admin-panel/       # 商家後台
├── customer-booking/      # 客戶預約前端
├── platform-admin/        # 平台管理員前端
├── scripts/               # 啟動腳本
│   └── start_all.sh       # 一鍵啟動腳本
├── docs/                  # 專案文檔
└── requirements.txt       # Python 依賴
```

## 主要功能

### 商家功能
- 🔐 **登入系統** - Email/密碼認證，JWT Token 管理
- 📅 **預約管理** - 預約時間管理、客戶資料管理
- 🛠️ **服務管理** - 服務項目管理、營業時間設定
- 📊 **報表統計** - 營業報表、客戶分析

### 客戶功能
- 📱 **線上預約** - 直觀的預約介面
- 🔍 **預約查詢** - 預約狀態查詢
- 💅 **服務瀏覽** - 服務項目瀏覽

### 平台管理員功能
- 🏢 **商家管理** - 建立、初始化、啟停、憑證輪替
- 📊 **系統監控** - Webhook 健康檢查、推播配額監控
- 📈 **資料報表** - 商家統計、業務指標、客戶規模分析
- 🔒 **安全治理** - RBAC 權限控制、審計軌跡、秘密管理
- 🛠️ **支援運維** - 工單中心、通知系統、一鍵回滾
- 🔐 **登入系統** - 管理員認證、權限控制

## 技術棧

### 後端技術
- **框架**: FastAPI (Python 3.8+)
- **資料庫**: PostgreSQL 14+ with Row Level Security
- **ORM**: SQLAlchemy 2.0
- **認證**: JWT, LINE LIFF
- **加密**: Fernet (AES 128)

### 前端技術
- **框架**: React 18 + TypeScript
- **UI 庫**: 自定義組件 + Tailwind CSS
- **樣式**: Tailwind CSS
- **狀態管理**: React Hooks
- **HTTP 客戶端**: Fetch API
- **認證**: JWT Token 管理

### 部署與運維
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **資料庫**: PostgreSQL (Docker)
- **監控**: 自建健康檢查系統

## 開發指南

### 專案文檔
詳細開發文檔請參考 `docs/` 目錄：
- `ERD_DOCUMENTATION.md` - 資料庫設計與 ERD 圖
- `THREE_FRONTEND_ARCHITECTURE.md` - 三前端架構設計
- `MULTI_MERCHANT_GUIDE.md` - 多租戶架構指南
- `LIFF_INTEGRATION_GUIDE.md` - LINE LIFF 整合指南

### 開發環境設定
```bash
# 1. 克隆專案
git clone <repository-url>
cd 美甲預約系統

# 2. 設定 Python 虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安裝後端依賴
pip install -r requirements.txt

# 4. 安裝前端依賴
cd frontend/admin-panel && npm install
cd ../customer-booking && npm install
cd ../../platform-admin && npm install
cd ..

# 5. 一鍵啟動所有服務
./scripts/start_all.sh
```

### API 開發
- 後端 API 使用 FastAPI 框架
- 自動生成 OpenAPI 文檔
- 支援 Swagger UI 和 ReDoc
- 完整的型別提示和驗證

### 前端開發
- 使用 TypeScript 確保型別安全
- 模組化組件設計
- 響應式設計支援
- 統一的 UI 設計系統

## 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案