#!/bin/bash

# 美甲預約系統啟動腳本
# 一次啟動前後端服務

set -e  # 遇到錯誤時停止執行

echo "🚀 啟動美甲預約系統..."

# 檢查是否在正確的目錄
if [ ! -f "app/main.py" ]; then
    echo "❌ 錯誤：請在專案根目錄執行此腳本"
    exit 1
fi

# 設置環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"

# 檢查 Docker 容器是否運行
echo "📋 檢查 PostgreSQL 容器..."
if ! docker ps | grep -q "nail-booking-postgres"; then
    echo "⚠️  PostgreSQL 容器未運行，正在啟動..."
    docker run --name nail-booking-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=nail_booking_db --network host -d postgres:14
    echo "⏳ 等待 PostgreSQL 啟動..."
    sleep 5
else
    echo "✅ PostgreSQL 容器正在運行"
fi

# 檢查資料庫連接
echo "🔍 測試資料庫連接..."
if ! docker exec nail-booking-postgres psql -U postgres -d nail_booking_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ 資料庫連接失敗"
    exit 1
fi
echo "✅ 資料庫連接正常"

# 啟動後端服務
echo "🔧 啟動後端服務 (FastAPI)..."
cd /home/johnny/專案/美甲預約系統
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待後端啟動
echo "⏳ 等待後端服務啟動..."
sleep 3

# 檢查後端是否啟動成功
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ 後端服務啟動失敗"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo "✅ 後端服務啟動成功 (http://localhost:8000)"

# 啟動前端服務
echo "🎨 啟動前端服務 (React)..."
cd admin-panel
npm start &
FRONTEND_PID=$!

# 等待前端啟動
echo "⏳ 等待前端服務啟動..."
sleep 5

# 檢查前端是否啟動成功
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ 前端服務啟動失敗"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi
echo "✅ 前端服務啟動成功 (http://localhost:3000)"

echo ""
echo "🎉 美甲預約系統啟動完成！"
echo ""
echo "📱 前端管理面板: http://localhost:3000"
echo "🔧 後端 API 文檔: http://localhost:8000/docs"
echo "📊 API 健康檢查: http://localhost:8000/"
echo ""
echo "💡 提示："
echo "   - 按 Ctrl+C 停止所有服務"
echo "   - 後端 PID: $BACKEND_PID"
echo "   - 前端 PID: $FRONTEND_PID"
echo ""

# 等待用戶中斷
trap 'echo ""; echo "🛑 正在停止服務..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo "✅ 服務已停止"; exit 0' INT

# 保持腳本運行
wait
