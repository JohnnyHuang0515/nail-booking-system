# 美甲預約系統

多租戶美甲預約管理系統，支援商家管理、客戶預約和平台管理員功能。

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

# 啟動 PostgreSQL 資料庫
./archive/scripts/setup_postgresql.sh
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
- 商家後台: http://localhost:3000
- 客戶預約: http://localhost:3001
- 平台管理員: http://localhost:3002
- API 文檔: http://localhost:8000/docs

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
- 商家生命週期管理
- 系統監控
- 資料報表
- 安全治理

## 技術棧

- **後端**: FastAPI, SQLAlchemy, PostgreSQL
- **前端**: React, TypeScript, Ant Design
- **部署**: Docker, Nginx

## 開發指南

詳細開發文檔請參考 `docs/` 目錄：
- `ERD_DOCUMENTATION.md` - 資料庫設計
- `THREE_FRONTEND_ARCHITECTURE.md` - 前端架構
- `MULTI_MERCHANT_GUIDE.md` - 多租戶指南
- `LIFF_INTEGRATION_GUIDE.md` - LINE 整合指南