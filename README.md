# 美甲預約系統

多租戶美甲預約管理系統，支援商家管理、客戶預約和平台管理員功能。

## 系統特色

- 🏢 **多租戶架構** - 支援多商家獨立運營
- 📱 **LINE 整合** - 支援 LINE LIFF 和 Rich Menu
- 🔐 **安全治理** - RBAC 權限控制、審計軌跡
- 📊 **智能監控** - 系統健康檢查、業務報表
- 🚀 **一鍵部署** - 完整的啟動腳本和部署方案

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

# 啟動 PostgreSQL 資料庫 (使用 Docker)
./archive/scripts/setup_postgresql.sh

# 或手動啟動 PostgreSQL 服務
# 確保資料庫連接字串正確設定
```

### 2. 啟動服務

**方式一：一鍵啟動所有服務**
```bash
./scripts/start_all.sh
```

**方式二：分步啟動**
```bash
# 啟動後端
./scripts/start_backend.sh

# 啟動前端（新終端）
./scripts/start-frontends.sh
```

### 3. 訪問應用
- **商家後台**: http://localhost:3000 - 商家管理介面
- **客戶預約**: http://localhost:3001 - 客戶預約介面
- **平台管理員**: http://localhost:3002 - 平台管理介面
- **API 文檔**: http://localhost:8000/docs - Swagger API 文檔
- **後端 API**: http://localhost:8000 - RESTful API 服務

### 4. 停止服務
```bash
./scripts/stop.sh
```

## 專案結構

```
美甲預約系統/
├── app/                    # 後端 API 服務
├── frontend/              # 前端應用
│   └── admin-panel/       # 商家後台
├── customer-booking/      # 客戶預約前端
├── platform-admin/        # 平台管理員前端
├── scripts/               # 啟動腳本
├── docs/                  # 專案文檔
├── archive/               # 歷史檔案
└── requirements.txt       # Python 依賴
```

## 主要功能

### 商家功能
- 服務項目管理
- 預約時間管理
- 客戶資料管理
- 營業時間設定

### 客戶功能
- 線上預約
- 預約查詢
- 服務瀏覽

### 平台管理員功能
- **商家管理**: 建立、初始化、啟停、憑證輪替
- **系統監控**: Webhook 健康檢查、推播配額監控
- **資料報表**: 商家統計、業務指標、客戶規模分析
- **安全治理**: RBAC 權限控制、審計軌跡、秘密管理
- **支援運維**: 工單中心、通知系統、一鍵回滾

## 技術棧

### 後端技術
- **框架**: FastAPI (Python 3.8+)
- **資料庫**: PostgreSQL 14+ with Row Level Security
- **ORM**: SQLAlchemy 2.0
- **認證**: JWT, LINE LIFF
- **加密**: Fernet (AES 128)

### 前端技術
- **框架**: React 18 + TypeScript
- **UI 庫**: Ant Design 5.x
- **樣式**: Tailwind CSS
- **狀態管理**: React Hooks
- **HTTP 客戶端**: Fetch API

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

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
export DATABASE_URL="postgresql://user:password@localhost/nail_booking_db"

# 5. 啟動開發服務
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