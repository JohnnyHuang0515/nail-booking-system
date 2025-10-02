"""
資料庫初始化腳本
用於創建資料表結構和初始資料
"""
import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.session import get_database_url, Base
from app.infrastructure.database.models import Merchant, Service, User, Appointment, BusinessHour
import uuid
from datetime import datetime, time, date

def create_tables():
    """創建所有資料表"""
    print("正在創建資料表...")
    
    # 獲取資料庫 URL
    database_url = get_database_url()
    if database_url == "postgresql://user:password@localhost/nail_booking_db":
        print("警告: 使用預設的 DATABASE_URL，請設定正確的環境變數")
    
    # 創建引擎
    engine = create_engine(database_url)
    
    # 創建所有資料表
    Base.metadata.create_all(bind=engine)
    print("資料表創建完成!")

def insert_initial_data():
    """插入初始資料"""
    print("正在插入初始資料...")
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # 檢查是否已有資料
        existing_merchants = db.query(Merchant).count()
        if existing_merchants > 0:
            print(f"資料庫中已有 {existing_merchants} 個商家，跳過初始資料插入")
            return
        
        # 創建測試商家
        test_merchant = Merchant(
            id=uuid.uuid4(),
            name="美甲工作室測試",
            line_channel_id="test_channel_id",
            line_channel_secret="test_channel_secret",
            line_channel_access_token="test_access_token",
            liff_id="test_liff_id",
            timezone="Asia/Taipei",
            is_active=True
        )
        db.add(test_merchant)
        db.commit()
        
        # 創建測試服務
        services_data = [
            {
                "name": "基礎保養",
                "duration_minutes": 60,
                "price": 800.0
            },
            {
                "name": "法式指甲",
                "duration_minutes": 90,
                "price": 1200.0
            },
            {
                "name": "光療指甲",
                "duration_minutes": 120,
                "price": 1500.0
            }
        ]
        
        for service_data in services_data:
            service = Service(
                id=uuid.uuid4(),
                merchant_id=test_merchant.id,
                name=service_data["name"],
                duration_minutes=service_data["duration_minutes"],
                price=service_data["price"],
                is_active=True
            )
            db.add(service)
        
        # 創建營業時間
        business_hours_data = [
            {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(18, 0)},  # 週一
            {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(18, 0)},  # 週二
            {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(18, 0)},  # 週三
            {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(18, 0)},  # 週四
            {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(18, 0)},  # 週五
            {"day_of_week": 6, "start_time": time(9, 0), "end_time": time(17, 0)},  # 週六
            # 週日不營業，所以不添加
        ]
        
        for hour_data in business_hours_data:
            business_hour = BusinessHour(
                id=uuid.uuid4(),
                merchant_id=test_merchant.id,
                day_of_week=hour_data["day_of_week"],
                start_time=hour_data["start_time"],
                end_time=hour_data["end_time"]
            )
            db.add(business_hour)
        
        db.commit()
        print("初始資料插入完成!")
        print(f"創建了測試商家: {test_merchant.name} (ID: {test_merchant.id})")
        print(f"創建了 {len(services_data)} 個服務項目")
        print(f"創建了 {len(business_hours_data)} 個營業時間設定")
        
    except Exception as e:
        print(f"插入初始資料時發生錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函數"""
    print("開始初始化資料庫...")
    
    try:
        # 創建資料表
        create_tables()
        
        # 插入初始資料
        insert_initial_data()
        
        print("資料庫初始化完成!")
        
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
