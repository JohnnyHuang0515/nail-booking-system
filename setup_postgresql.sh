#!/bin/bash
# PostgreSQL 資料庫設定腳本 (使用 Docker)

echo "=== PostgreSQL 資料庫設定 (Docker) ==="

# 1. 啟動 PostgreSQL 容器
echo "啟動 PostgreSQL 容器..."
docker run --name nail-booking-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=nail_booking_db --network host -d postgres:14

# 2. 等待容器啟動
echo "等待 PostgreSQL 啟動..."
sleep 5

# 3. 測試連接
echo "測試資料庫連接..."
docker exec nail-booking-postgres psql -U postgres -d nail_booking_db -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL 設定完成！"
    echo "📁 資料庫: nail_booking_db"
    echo "👤 使用者: postgres"
    echo "🔗 端口: 5432"
    echo ""
    echo "現在可以執行以下命令建立資料表："
    echo "export DATABASE_URL=\"postgresql://postgres:password@localhost:5432/nail_booking_db\""
    echo "python3 create_tables.py"
    echo ""
    echo "停止容器: docker stop nail-booking-postgres"
    echo "啟動容器: docker start nail-booking-postgres"
else
    echo "❌ PostgreSQL 設定失敗"
    exit 1
fi
