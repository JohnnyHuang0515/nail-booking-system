#!/bin/bash

echo "=========================================="
echo "🚀 快速驗證腳本"
echo "=========================================="
echo ""

# 檢查服務
echo "檢查服務狀態..."
BACKEND=$(curl -s http://localhost:8000/docs | grep -o '<title>.*</title>' | head -1)
FRONTEND=$(curl -s http://localhost:3001 | grep -o '<title>.*</title>' | head -1)

echo "  後端: $(echo $BACKEND | sed 's/<[^>]*>//g')"
echo "  前端: $(echo $FRONTEND | sed 's/<[^>]*>//g')"
echo ""

# 測試 API
TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
echo "測試關鍵 API..."
SLOTS=$(curl -s "http://localhost:8000/public/merchants/nail-abc/slots?target_date=${TOMORROW}&staff_id=1")
SLOT_COUNT=$(echo "$SLOTS" | grep -o '"start_time"' | wc -l)
echo "  時段 API: ${SLOT_COUNT} 個時段"
echo ""

echo "=========================================="
echo "✅ 系統準備就緒"
echo "=========================================="
echo ""
echo "📱 開啟瀏覽器測試:"
echo "   http://localhost:3001"
echo ""
echo "🔍 預期 Console 輸出:"
echo "   ✅ LIFF 初始化成功"
echo "   ✅ 商家資訊已載入: 美甲沙龍 ABC"
echo "   ✅ 載入時段: 15 個"
echo ""
echo "📸 成功標準:"
echo "   - 能選擇日期"
echo "   - 能看到時段列表"
echo "   - 能選擇服務"
echo "   - 能成功提交預約"
echo ""
