#!/bin/bash

echo "正在啟動美甲預約系統..."

# 檢查端口是否被占用
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "端口 3000 已被占用，請先停止其他服務"
    exit 1
fi

if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "端口 3001 已被占用，請先停止其他服務"
    exit 1
fi

echo "啟動管理後台 (端口 3000)..."
cd admin-panel
npm start &
ADMIN_PID=$!

echo "等待管理後台啟動..."
sleep 10

echo "啟動客戶預約頁面 (端口 3001)..."
cd ../customer-booking
npm start &
CUSTOMER_PID=$!

echo "等待客戶預約頁面啟動..."
sleep 10

echo ""
echo "應用已啟動！"
echo "管理後台: http://localhost:3000"
echo "客戶預約: http://localhost:3001"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待用戶中斷
trap "echo '正在停止服務...'; kill $ADMIN_PID $CUSTOMER_PID; exit" INT
wait