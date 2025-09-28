#!/bin/bash

# 美甲預約系統完整啟動腳本

echo "🚀 啟動美甲預約系統 - 完整服務"
echo "================================"

# 檢查必要工具
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝"
    exit 1
fi

# 設置環境變數
export DATABASE_URL="postgresql://user:password@localhost/nail_booking_db"

echo "📋 檢查資料庫連接..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('✅ 資料庫連接正常')
except Exception as e:
    print(f'❌ 資料庫連接失敗: {e}')
    print('請先啟動 PostgreSQL 服務')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# 檢查端口
echo "🔍 檢查端口占用..."
for port in 3000 3001 3002 8000; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ 端口 $port 已被占用，請先停止其他服務"
        exit 1
    fi
done

echo "✅ 所有端口可用"

# 啟動後端
echo "🔧 啟動後端 API 服務..."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待後端啟動
echo "⏳ 等待後端啟動..."
sleep 5

# 啟動前端
echo "🎨 啟動前端服務..."

# 獲取專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 商家後台
echo "啟動商家後台 (端口 3000)..."
cd "$PROJECT_ROOT/frontend/admin-panel" && npm start &
ADMIN_PID=$!

# 客戶預約
echo "啟動客戶預約 (端口 3001)..."
cd "$PROJECT_ROOT/frontend/customer-booking" && npm start &
CUSTOMER_PID=$!

# 平台管理員
echo "啟動平台管理員 (端口 3002)..."
cd "$PROJECT_ROOT/platform-admin" && npm start &
PLATFORM_PID=$!

# 等待前端啟動
echo "⏳ 等待前端啟動..."
sleep 10

echo ""
echo "✅ 所有服務已啟動！"
echo ""
echo "📱 訪問地址："
echo "   商家後台:     http://localhost:3000"
echo "   客戶預約:     http://localhost:3001"
echo "   平台管理員:   http://localhost:3002"
echo "   後端 API:     http://localhost:8000"
echo "   API 文檔:     http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止所有服務..."
    kill $BACKEND_PID $ADMIN_PID $CUSTOMER_PID $PLATFORM_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT
wait
