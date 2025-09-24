#!/bin/bash

# 美甲預約系統停止腳本

echo "🛑 停止美甲預約系統服務..."

# 停止 uvicorn 進程
echo "🔧 停止後端服務..."
pkill -f "uvicorn app.main:app" || echo "後端服務未運行"

# 停止 npm start 進程
echo "🎨 停止前端服務..."
pkill -f "npm start" || echo "前端服務未運行"

# 停止 PostgreSQL 容器
echo "📋 停止 PostgreSQL 容器..."
docker stop nail-booking-postgres 2>/dev/null || echo "PostgreSQL 容器未運行"

echo "✅ 所有服務已停止"
