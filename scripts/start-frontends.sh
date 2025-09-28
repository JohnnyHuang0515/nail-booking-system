#!/bin/bash

echo "🚀 啟動美甲預約系統 - 前端服務"
echo "================================"

# 檢查 Node.js 和 npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝"
    exit 1
fi

echo "📦 檢查依賴..."
cd frontend/admin-panel && npm install --silent
cd ../customer-booking && npm install --silent
cd ../../platform-admin && npm install --silent

echo ""
echo "🌐 啟動前端服務..."
echo ""

# 啟動三個前端 (後台執行)
echo "啟動商家後台 (端口 3000)..."
cd ../frontend/admin-panel && npm start &
ADMIN_PID=$!

echo "啟動顧客端 (端口 3001)..."
cd ../customer-booking && npm start &
CUSTOMER_PID=$!

echo "啟動平台管理員後台 (端口 3002)..."
cd ../../platform-admin && npm start &
PLATFORM_PID=$!

echo ""
echo "✅ 所有前端已啟動！"
echo ""
echo "📱 訪問地址："
echo "   商家後台:     http://localhost:3000"
echo "   顧客端:       http://localhost:3001" 
echo "   平台管理員:   http://localhost:3002"
echo ""
echo "💡 提示：請先執行 ./start_backend.sh 啟動後端 API"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待用戶中斷
trap "echo ''; echo '🛑 停止所有前端服務...'; kill $ADMIN_PID $CUSTOMER_PID $PLATFORM_PID 2>/dev/null; exit 0" INT

# 保持腳本運行
wait
