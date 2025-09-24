# 美甲預約系統啟動腳本

## 📋 可用腳本

### 1. `start.sh` - 完整啟動腳本
**功能：** 完整的啟動流程，包含詳細的檢查和錯誤處理
**使用：** `./start.sh`

**特點：**
- ✅ 檢查 PostgreSQL 容器狀態
- ✅ 測試資料庫連接
- ✅ 驗證服務啟動狀態
- ✅ 詳細的狀態報告
- ✅ 優雅的錯誤處理

### 2. `quick_start.sh` - 快速啟動腳本
**功能：** 簡化版本，適合日常開發
**使用：** `./quick_start.sh`

**特點：**
- ⚡ 快速啟動
- 🎯 簡潔輸出
- 🔄 自動處理容器

### 3. `stop.sh` - 停止腳本
**功能：** 停止所有相關服務
**使用：** `./stop.sh`

**特點：**
- 🛑 停止後端服務
- 🛑 停止前端服務
- 🛑 停止 PostgreSQL 容器

## 🚀 使用方法

### 首次啟動
```bash
# 使用完整啟動腳本（推薦）
./start.sh
```

### 日常開發
```bash
# 使用快速啟動腳本
./quick_start.sh
```

### 停止服務
```bash
# 停止所有服務
./stop.sh
```

## 📱 服務地址

啟動成功後，您可以訪問：

- **前端管理面板**: http://localhost:3000
- **後端 API 文檔**: http://localhost:8000/docs
- **API 健康檢查**: http://localhost:8000/

## 🔧 手動啟動（備用方案）

如果腳本無法正常工作，可以手動啟動：

### 1. 啟動 PostgreSQL
```bash
docker run --name nail-booking-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=nail_booking_db --network host -d postgres:14
```

### 2. 啟動後端
```bash
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 啟動前端
```bash
cd admin-panel
npm start
```

## ⚠️ 注意事項

1. **確保在專案根目錄執行腳本**
2. **確保 Docker 已安裝並運行**
3. **確保 Node.js 和 npm 已安裝**
4. **確保 Python 3 和相關依賴已安裝**

## 🐛 故障排除

### PostgreSQL 容器問題
```bash
# 重新創建容器
docker stop nail-booking-postgres
docker rm nail-booking-postgres
./start.sh
```

### 端口衝突
```bash
# 檢查端口使用情況
lsof -i :8000
lsof -i :3000
lsof -i :5432
```

### 權限問題
```bash
# 確保腳本有執行權限
chmod +x *.sh
```
