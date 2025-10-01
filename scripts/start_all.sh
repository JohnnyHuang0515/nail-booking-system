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

if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    exit 1
fi

# 設置環境變數
export DATABASE_URL="postgresql://user:password@localhost/nail_booking_db"

# 啟動 PostgreSQL 資料庫
echo "🗄️ 啟動 PostgreSQL 資料庫..."
if ! docker ps | grep -q "nail-booking-postgres"; then
    echo "啟動 PostgreSQL 容器..."
    docker run -d \
        --name nail-booking-postgres \
        -e POSTGRES_DB=nail_booking_db \
        -e POSTGRES_USER=user \
        -e POSTGRES_PASSWORD=password \
        -p 5432:5432 \
        postgres:13
    echo "⏳ 等待資料庫啟動..."
    sleep 10
else
    echo "✅ PostgreSQL 容器已在運行"
fi

echo "📋 檢查資料庫連接..."
python3 -c "
import psycopg2
import time
max_retries = 5
for i in range(max_retries):
    try:
        conn = psycopg2.connect('$DATABASE_URL')
        conn.close()
        print('✅ 資料庫連接正常')
        break
    except Exception as e:
        if i == max_retries - 1:
            print(f'❌ 資料庫連接失敗: {e}')
            print('請檢查 PostgreSQL 容器狀態')
            exit(1)
        else:
            print(f'⏳ 資料庫連接中... ({i+1}/{max_retries})')
            time.sleep(2)
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
echo "🗄️ 資料庫資訊："
echo "   PostgreSQL:   localhost:5432"
echo "   資料庫名:     nail_booking_db"
echo "   使用者:       user"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止所有服務..."
    kill $BACKEND_PID $ADMIN_PID $CUSTOMER_PID $PLATFORM_PID 2>/dev/null || true
    
    # 詢問是否停止資料庫容器
    echo ""
    read -p "是否停止 PostgreSQL 容器? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止 PostgreSQL 容器..."
        docker stop nail-booking-postgres 2>/dev/null || true
        docker rm nail-booking-postgres 2>/dev/null || true
    fi
    
    exit 0
}

trap cleanup INT
wait
