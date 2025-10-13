#!/bin/bash

# 資源監控腳本
echo "🔍 美甲預約系統 - 資源使用監控"
echo "================================"
echo ""

echo "📊 後端進程 (uvicorn):"
ps aux | grep uvicorn | grep -v grep | awk '{printf "CPU: %s%% | 記憶體: %s%% | PID: %s\n", $3, $4, $2}'
echo ""

echo "📊 前端進程 (node):"
ps aux | grep "react-scripts start" | grep -v grep | awk '{printf "CPU: %s%% | 記憶體: %s%% | 端口: %s\n", $3, $4, $12}'
echo ""

echo "📊 整體系統狀態:"
top -l 1 | grep -E "CPU usage|PhysMem|Load Avg"
echo ""

echo "🌡️ CPU 溫度 (需要安裝 osx-cpu-temp):"
if command -v osx-cpu-temp &> /dev/null; then
    osx-cpu-temp
else
    echo "   未安裝 osx-cpu-temp"
    echo "   安裝: brew install osx-cpu-temp"
fi

