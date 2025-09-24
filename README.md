# 美甲預約系統

一個完整的美甲預約管理系統，包含管理後台、客戶端 LIFF 應用和 RESTful API。

## 🚀 快速開始

### 使用啟動腳本 (推薦)
```bash
# 一鍵啟動所有服務
./start.sh
```

### 手動啟動
```bash
# 1. 啟動資料庫
./setup_postgresql.sh

# 2. 創建資料庫表
python create_tables.py

# 3. 啟動後端 API
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# 4. 啟動管理後台
cd admin-panel && npm start &

# 5. 啟動客戶端 LIFF
cd customer-liff && npm start &
```

## 🌐 訪問地址

- **管理後台**: http://localhost:3000
- **客戶端 LIFF**: http://localhost:3001  
- **API 文檔**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## 📚 文檔

詳細文檔請查看 [docs/](./docs/) 目錄：

- [📖 完整文檔](./docs/README.md)
- [🔌 API 文檔](./docs/API.md)
- [🚀 部署指南](./docs/DEPLOYMENT.md)
- [🎨 管理後台設計](./docs/admin_panel_design.md)
- [👥 客戶管理指南](./docs/CUSTOMER_MANAGEMENT_README.md)
- [🏗️ 系統設計](./docs/nail_booking_system_design.md)

## 🏗️ 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   客戶端 LIFF   │    │   管理後台      │    │   後端 API      │
│   (React)       │    │   (React)       │    │   (FastAPI)     │
│   Port: 3001    │    │   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Port: 5432     │
                    └─────────────────┘
```

## ✨ 主要功能

### 🎯 核心功能
- ✅ **用戶管理** - LINE 用戶登入/註冊
- ✅ **預約管理** - 創建、編輯、刪除、狀態更新
- ✅ **服務管理** - 服務項目 CRUD 操作
- ✅ **時段管理** - 營業時間和休假管理
- ✅ **儀表板** - 統計數據和今日預約
- ✅ **客戶預約** - 完整的預約流程

### 🛠️ 技術特色
- **後端**: FastAPI + PostgreSQL + SQLAlchemy
- **前端**: React + Material-UI + TypeScript
- **架構**: DDD (Domain-Driven Design)
- **API**: RESTful API + 自動文檔
- **部署**: Docker 支援

## 🚀 開發

### 環境要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Docker (可選)

### 安裝依賴
```bash
# Python 依賴
pip install -r requirements.txt

# 前端依賴
cd admin-panel && npm install
cd ../customer-liff && npm install
```

### 運行測試
```bash
# API 測試
pytest tests/api/v1/

# 前端測試
cd admin-panel && npm test
cd ../customer-liff && npm test
```

## 📦 專案結構

```
美甲預約系統/
├── app/                    # 後端 FastAPI 應用
│   ├── api/               # API 端點
│   ├── application/       # 應用服務層
│   ├── domain/           # 領域模型
│   └── infrastructure/   # 基礎設施層
├── admin-panel/          # 管理後台 React 應用
├── customer-liff/        # 客戶端 LIFF React 應用
├── docs/                # 文檔
├── tests/               # 測試文件
├── requirements.txt     # Python 依賴
└── *.sh                # 啟動腳本
```

## 🤝 貢獻

歡迎貢獻代碼！請遵循以下步驟：

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件。

## 📞 支援

如果您在使用過程中遇到問題：

1. 查看 [文檔](./docs/)
2. 檢查 [Issues](../../issues) 頁面
3. 創建新的 Issue 描述問題

---

**版本**: v1.0.0  
**最後更新**: 2025年1月
