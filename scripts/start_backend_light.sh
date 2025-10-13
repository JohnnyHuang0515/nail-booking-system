#!/bin/bash

# 輕量級後端啟動腳本 (降低 CPU 使用)

echo "🔧 啟動美甲預約系統後端 (輕量級模式)..."

# 檢查 uv 環境
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安裝，請先安裝 uv"
    exit 1
fi

# 設置環境變數
export DATABASE_URL="postgresql://user:password@localhost/nail_booking_db"

# 檢查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 8000 已被占用，正在停止舊服務..."
    pkill -f "uvicorn app.main:app"
    sleep 2
fi

# 啟動後端服務（無 reload 模式，降低 CPU 使用）
echo "🚀 啟動後端 API 服務 (端口 8000)..."
echo "💡 輕量級模式: 無自動重載，修改代碼後需手動重啟"
echo ""

uv run uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level warning

echo "✅ 後端服務已啟動"
echo "📱 API 文檔: http://localhost:8000/docs"

