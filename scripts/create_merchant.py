#!/usr/bin/env python3
"""
新增商家腳本
用法: python scripts/create_merchant.py <商家名稱> <帳號> <密碼>
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.session import engine
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_service_repository import SqlServiceRepository
from app.infrastructure.repositories.sql_business_hour_repository import SQLBusinessHourRepository
from app.config import MerchantConfig
from app.api.v1.endpoints.admin import get_password_hash
import bcrypt

# 創建資料庫會話
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def create_merchant_with_credentials(
    name: str, 
    account: str, 
    password: str,
    line_channel_id: str = "12345678901234567890123456789012",  # 預設測試用
    line_channel_secret: str = "test_channel_secret",
    line_channel_access_token: str = "test_access_token",
    timezone: str = 'Asia/Taipei'
):
    """創建帶有帳號密碼的商家"""
    
    db_session = SessionLocal()
    try:
        print(f"開始創建商家: {name}")
        
        # 檢查帳號是否已存在
        merchant_repo = SQLMerchantRepository(db_session)
        existing_merchant = merchant_repo.find_by_account(account)
        if existing_merchant:
            print(f"錯誤: 帳號 '{account}' 已存在")
            return False
        
        # 生成密碼雜湊
        password_hash = get_password_hash(password)
        
        # 創建商家
        merchant = merchant_repo.create(
            name=name,
            account=account,
            password_hash=password_hash,
            line_channel_id=line_channel_id,
            line_channel_secret=line_channel_secret,
            line_channel_access_token=line_channel_access_token,
            timezone=timezone
        )
        
        db_session.flush()
        print(f"商家創建成功!")
        print(f"  - 商家ID: {merchant.id}")
        print(f"  - 商家名稱: {merchant.name}")
        print(f"  - 商家代碼: {merchant.merchant_code}")
        print(f"  - 帳號: {merchant.account}")
        
        # 初始化預設服務
        service_repo = SqlServiceRepository(db_session)
        default_services = MerchantConfig.get_default_services()
        
        for service_data in default_services:
            from app.domain.booking.models import Service as DomainService
            domain_service = DomainService(
                merchant_id=merchant.id,
                name=service_data["name"],
                price=service_data["price"],
                duration_minutes=service_data["duration_minutes"]
            )
            service_repo.add(domain_service)
        
        print(f"  - 已創建 {len(default_services)} 個預設服務")
        
        # 初始化營業時間
        business_hour_repo = SQLBusinessHourRepository(db_session)
        default_hours = MerchantConfig.get_default_business_hours()
        
        for hour_data in default_hours:
            business_hour_repo.create(
                merchant_id=merchant.id,
                day_of_week=hour_data["day_of_week"],
                start_time=hour_data["start_time"],
                end_time=hour_data["end_time"]
            )
        
        print(f"  - 已創建 {len(default_hours)} 個營業時間設定")
        
        # 提交變更
        db_session.commit()
        print("所有資料已成功提交到資料庫")
        
        return True
        
    except Exception as e:
        db_session.rollback()
        print(f"創建商家失敗: {str(e)}")
        return False
    finally:
        db_session.close()

def main():
    """主函數"""
    if len(sys.argv) != 4:
        print("用法: python scripts/create_merchant.py <商家名稱> <帳號> <密碼>")
        print("範例: python scripts/create_merchant.py '台北美甲店' taipei_nail merchant123")
        sys.exit(1)
    
    name = sys.argv[1]
    account = sys.argv[2]
    password = sys.argv[3]
    
    # 執行異步函數
    success = asyncio.run(create_merchant_with_credentials(name, account, password))
    
    if success:
        print(f"\n✅ 商家 '{name}' 創建成功!")
        print(f"帳號: {account}")
        print(f"密碼: {password}")
        print("\n商家可以使用這些憑證登入後台系統。")
    else:
        print(f"\n❌ 商家創建失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
