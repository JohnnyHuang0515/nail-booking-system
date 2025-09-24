# 美甲預約系統文檔

歡迎來到美甲預約系統的文檔中心！這裡包含了系統的所有相關文檔和指南。

## 📚 文檔目錄

### 🏗️ 系統設計
- [系統整體設計](./nail_booking_system_design.md) - 系統架構、技術棧和整體設計理念
- [系統開發計劃](./system_development_plan.md) - 開發階段規劃和里程碑

### 🎨 前端設計
- [管理後台設計](./admin_panel_design.md) - 管理後台的 UI/UX 設計規範和組件說明

### 👥 用戶管理
- [客戶管理指南](./CUSTOMER_MANAGEMENT_README.md) - 客戶端 LIFF 應用的使用說明

### 🚀 部署與啟動
- [啟動腳本說明](./STARTUP_SCRIPTS.md) - 系統啟動腳本的使用方法

### 🧪 測試規範
- [功能測試](./features/) - BDD 測試用例和功能規範

## 🏃‍♂️ 快速開始

### 1. 環境準備
```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝前端依賴
cd admin-panel && npm install
cd ../customer-liff && npm install
```

### 2. 資料庫設置
```bash
# 使用 Docker 啟動 PostgreSQL
./setup_postgresql.sh

# 創建資料庫表
python create_tables.py
```

### 3. 啟動系統
```bash
# 一鍵啟動所有服務
./start.sh
```

### 4. 訪問應用
- **管理後台**: http://localhost:3000
- **客戶端 LIFF**: http://localhost:3001
- **API 文檔**: http://localhost:8000/docs

## 🛠️ 開發指南

### 後端開發
- 使用 FastAPI 框架
- 遵循 DDD (Domain-Driven Design) 架構
- PostgreSQL 資料庫
- SQLAlchemy ORM

### 前端開發
- **管理後台**: React + Material-UI
- **客戶端**: React + TypeScript + Bootstrap
- 支援 LINE LIFF 整合

### API 設計
- RESTful API 設計
- 完整的 CRUD 操作
- 統一的錯誤處理
- API 文檔自動生成

## 📋 功能清單

### ✅ 已實現功能
- [x] 用戶管理（LINE 用戶登入/註冊）
- [x] 預約管理（創建、編輯、刪除、狀態更新）
- [x] 服務項目管理
- [x] 營業時間和休假管理
- [x] 儀表板統計
- [x] 客戶預約流程
- [x] 資料庫整合
- [x] Docker 支援

### 🔄 進行中功能
- [ ] 支付整合
- [ ] 通知系統
- [ ] 報表功能

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📞 支援

如果您在使用過程中遇到問題，請：
1. 查看相關文檔
2. 檢查 [Issues](../../issues) 頁面
3. 創建新的 Issue 描述問題

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](../../LICENSE) 文件。

---

**最後更新**: 2025年1月
**版本**: v1.0.0
