#!/bin/bash

# 美甲預約系統快速啟動腳本
# 簡化版本，適合日常開發使用

echo "🚀 快速啟動美甲預約系統..."

# 設置環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"

# 檢查並啟動 PostgreSQL 容器
if ! docker ps | grep -q "nail-booking-postgres"; then
    echo "📋 啟動 PostgreSQL 容器..."
    docker run --name nail-booking-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=nail_booking_db --network host -d postgres:14
    sleep 3
fi

# 啟動後端
echo "🔧 啟動後端..."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 啟動前端
echo "🎨 啟動前端..."
cd admin-panel && npm start &
FRONTEND_PID=$!

echo ""
echo "✅ 服務啟動中..."
echo "📱 前端: http://localhost:3000"
echo "🔧 後端: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止服務..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT
wait
