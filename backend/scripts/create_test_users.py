#!/usr/bin/env python3
"""
建立測試用戶腳本
用途：為開發環境建立測試商家帳號
"""
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from shared.database import SessionLocal
from identity.domain.models import User, RoleType, Role
from identity.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from identity.application.services import PasswordService

def create_test_users(db: Session):
    """建立測試用戶"""
    
    user_repo = SQLAlchemyUserRepository(db)
    
    print("👤 建立測試用戶...")
    
    # 商家 ID（與種子資料一致）
    merchant_id = "00000000-0000-0000-0000-000000000001"
    
    # 1. 建立商家擁有者帳號
    owner_user = User(
        id=str(uuid4()),
        email="admin@nailbooking.com",
        password_hash=PasswordService.hash_password("admin123"),
        name="美甲沙龍管理員",
        merchant_id=merchant_id,
        role=Role(id=2, name=RoleType.MERCHANT_OWNER),
        is_active=True,
        is_verified=True
    )
    
    user_repo.save(owner_user)
    print("✅ 商家擁有者帳號已建立")
    print(f"   帳號: admin@nailbooking.com")
    print(f"   密碼: admin123")
    print(f"   角色: MERCHANT_OWNER")
    
    # 2. 建立系統管理員帳號
    admin_user = User(
        id=str(uuid4()),
        email="system@nailbooking.com",
        password_hash=PasswordService.hash_password("system123"),
        name="系統管理員",
        merchant_id=None,  # 系統管理員不屬於特定商家
        role=Role(id=1, name=RoleType.ADMIN),
        is_active=True,
        is_verified=True
    )
    
    user_repo.save(admin_user)
    print("✅ 系統管理員帳號已建立")
    print(f"   帳號: system@nailbooking.com")
    print(f"   密碼: system123")
    print(f"   角色: ADMIN")
    
    # 3. 建立測試客戶帳號
    customer_user = User(
        id=str(uuid4()),
        email="customer@test.com",
        password_hash=PasswordService.hash_password("customer123"),
        name="測試客戶",
        merchant_id=merchant_id,
        role=Role(id=4, name=RoleType.CUSTOMER),
        is_active=True,
        is_verified=True
    )
    
    user_repo.save(customer_user)
    print("✅ 測試客戶帳號已建立")
    print(f"   帳號: customer@test.com")
    print(f"   密碼: customer123")
    print(f"   角色: CUSTOMER")
    
    db.commit()
    print("🎉 測試用戶建立完成！")

def main():
    """主函式"""
    print("🌱 建立測試用戶...")
    
    db = SessionLocal()
    try:
        create_test_users(db)
    except Exception as e:
        print(f"❌ 建立失敗: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
