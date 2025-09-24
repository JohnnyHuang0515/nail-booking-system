#!/bin/bash
# 美甲預約系統 - 資料庫設定腳本

echo "=== 美甲預約系統資料庫設定 ==="

# 設定資料庫 URL
export DATABASE_URL="sqlite:///./nail_booking.db"

echo "已設定 DATABASE_URL: $DATABASE_URL"

# 建立資料表
echo "正在建立資料表..."
python3 create_tables.py

if [ $? -eq 0 ]; then
    echo "✅ 資料表建立成功！"
    echo "📁 資料庫檔案: nail_booking.db"
else
    echo "❌ 資料表建立失敗"
    exit 1
fi

echo "=== 設定完成 ==="
