#!/usr/bin/env python3
"""
多商家美甲預約系統設置腳本
"""
import os
import sys
import asyncio
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.infrastructure.database.session import engine, get_db_session
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_service_repository import SQLServiceRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.database.models import Merchant, Service
from app.migrate_to_multi_merchant import migrate_to_multi_merchant
from app.config import settings, MerchantConfig
import uuid


def setup_environment():
    """設置環境"""
    print("設置環境...")
    
    # 創建必要的目錄
    directories = ["logs", "uploads", "temp"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  創建目錄: {directory}")
    
    # 設置環境變數
    env_vars = {
        "DATABASE_URL": "postgresql://user:password@localhost/nail_booking",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "your-secret-key-here-change-in-production",
        "ENCRYPTION_KEY": "your-encryption-key-here-change-in-production"
    }
    
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"  設置環境變數: {key}")


def create_database_tables():
    """創建資料庫表"""
    print("創建資料庫表...")
    
    try:
        migrate_to_multi_merchant()
        print("  資料庫表創建完成")
    except Exception as e:
        print(f"  資料庫表創建失敗: {str(e)}")
        raise


def create_sample_data():
    """創建範例資料"""
    print("創建範例資料...")
    
    with get_db_session() as db_session:
        merchant_repo = SQLMerchantRepository(db_session)
        service_repo = SQLServiceRepository(db_session)
        
        # 創建範例商家
        merchants_data = [
            {
                "name": "台北時尚美甲",
                "line_channel_id": "taipei_fashion_channel_1234567890abcdef",
                "line_channel_secret": "taipei_fashion_secret_1234567890abcdef",
                "line_channel_access_token": "taipei_fashion_token_1234567890abcdef",
                "timezone": "Asia/Taipei"
            },
            {
                "name": "高雄藝術美甲",
                "line_channel_id": "kaohsiung_art_channel_1234567890abcdef",
                "line_channel_secret": "kaohsiung_art_secret_1234567890abcdef",
                "line_channel_access_token": "kaohsiung_art_token_1234567890abcdef",
                "timezone": "Asia/Taipei"
            },
            {
                "name": "台中精品美甲",
                "line_channel_id": "taichung_boutique_channel_1234567890abcdef",
                "line_channel_secret": "taichung_boutique_secret_1234567890abcdef",
                "line_channel_access_token": "taichung_boutique_token_1234567890abcdef",
                "timezone": "Asia/Taipei"
            }
        ]
        
        created_merchants = []
        for merchant_data in merchants_data:
            try:
                merchant = merchant_repo.create(**merchant_data)
                created_merchants.append(merchant)
                print(f"  創建商家: {merchant.name} (ID: {merchant.id})")
            except Exception as e:
                print(f"  創建商家 {merchant_data['name']} 失敗: {str(e)}")
        
        # 為每個商家創建預設服務
        default_services = MerchantConfig.get_default_services()
        
        for merchant in created_merchants:
            for service_data in default_services:
                try:
                    service = Service(
                        merchant_id=merchant.id,
                        name=service_data["name"],
                        price=service_data["price"],
                        duration_minutes=service_data["duration_minutes"]
                    )
                    db_session.add(service)
                    print(f"    創建服務: {service.name} for {merchant.name}")
                except Exception as e:
                    print(f"    創建服務 {service_data['name']} 失敗: {str(e)}")
        
        db_session.commit()
        print(f"  創建了 {len(created_merchants)} 個商家和相關服務")


def test_api_endpoints():
    """測試 API 端點"""
    print("測試 API 端點...")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # 測試健康檢查
        response = client.get("/")
        if response.status_code == 200:
            print("  ✓ 健康檢查端點正常")
        else:
            print(f"  ✗ 健康檢查端點失敗: {response.status_code}")
        
        # 測試商家列表
        response = client.get("/api/v1/merchants")
        if response.status_code == 200:
            merchants = response.json()
            print(f"  ✓ 商家列表端點正常，找到 {len(merchants)} 個商家")
        else:
            print(f"  ✗ 商家列表端點失敗: {response.status_code}")
        
        # 測試 LINE Webhook 端點
        response = client.post("/api/v1/line/webhook", json={"events": []})
        # 這個端點可能會因為缺少簽名而失敗，但應該返回 400 而不是 500
        if response.status_code in [400, 401]:
            print("  ✓ LINE Webhook 端點正常（預期的驗證錯誤）")
        else:
            print(f"  ✗ LINE Webhook 端點異常: {response.status_code}")
        
    except ImportError:
        print("  跳過 API 測試（缺少測試依賴）")
    except Exception as e:
        print(f"  API 測試失敗: {str(e)}")


def test_database_connections():
    """測試資料庫連接"""
    print("測試資料庫連接...")
    
    try:
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            merchants = merchant_repo.list_active()
            print(f"  ✓ 資料庫連接正常，找到 {len(merchants)} 個商家")
    except Exception as e:
        print(f"  ✗ 資料庫連接失敗: {str(e)}")
        raise


def create_startup_script():
    """創建啟動腳本"""
    print("創建啟動腳本...")
    
    startup_script = """#!/bin/bash
# 多商家美甲預約系統啟動腳本

echo "啟動多商家美甲預約系統..."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動應用程式
echo "啟動 FastAPI 應用程式..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
    
    script_path = Path("start_multi_merchant.sh")
    script_path.write_text(startup_script)
    script_path.chmod(0o755)
    print(f"  創建啟動腳本: {script_path}")


def create_docker_compose():
    """創建 Docker Compose 配置"""
    print("創建 Docker Compose 配置...")
    
    docker_compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://nail_user:nail_password@db:5432/nail_booking
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=nail_booking
      - POSTGRES_USER=nail_user
      - POSTGRES_PASSWORD=nail_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
"""
    
    compose_path = Path("docker-compose.yml")
    compose_path.write_text(docker_compose)
    print(f"  創建 Docker Compose 配置: {compose_path}")


def main():
    """主函數"""
    print("=" * 60)
    print("多商家美甲預約系統設置")
    print("=" * 60)
    
    try:
        # 設置環境
        setup_environment()
        
        # 創建資料庫表
        create_database_tables()
        
        # 創建範例資料
        create_sample_data()
        
        # 測試資料庫連接
        test_database_connections()
        
        # 測試 API 端點
        test_api_endpoints()
        
        # 創建啟動腳本
        create_startup_script()
        
        # 創建 Docker Compose 配置
        create_docker_compose()
        
        print("\n" + "=" * 60)
        print("設置完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 更新環境變數配置（.env 檔案）")
        print("2. 配置 LINE Channel 憑證")
        print("3. 運行啟動腳本: ./start_multi_merchant.sh")
        print("4. 訪問 http://localhost:8000/docs 查看 API 文件")
        print("\n商家管理 API:")
        print("- GET /api/v1/merchants - 列出所有商家")
        print("- POST /api/v1/merchants - 創建新商家")
        print("- PUT /api/v1/merchants/{id} - 更新商家")
        print("- POST /api/v1/merchants/{id}/credentials - 更新憑證")
        
    except Exception as e:
        print(f"\n設置失敗: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
