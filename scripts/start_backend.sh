#!/bin/bash

# 美甲預約系統後端啟動腳本 (uv 版本)

echo "🔧 啟動美甲預約系統後端 (uv 版本)..."

# 檢查 uv 環境
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安裝，請先安裝 uv"
    echo "安裝指令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 同步依賴
echo "📦 同步專案依賴..."
uv sync

# 設置環境變數
export DATABASE_URL="postgresql://user:password@localhost/nail_booking_db"

# 檢查資料庫連接
echo "📋 檢查資料庫連接..."
uv run python -c "
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

# 檢查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ 端口 8000 已被占用，請先停止其他服務"
    exit 1
fi

# 啟動後端服務
echo "🚀 啟動後端 API 服務 (端口 8000)..."
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo "✅ 後端服務已啟動"
echo "📱 API 文檔: http://localhost:8000/docs"
echo "🔧 API 基礎 URL: http://localhost:8000"
