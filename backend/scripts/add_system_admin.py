#!/usr/bin/env python3
"""
添加系統管理員腳本
用途：為開發環境添加系統管理員帳號
"""
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from shared.database import SessionLocal
from identity.domain.models import User, RoleType, Role
from identity.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from identity.application.services import PasswordService

def add_system_admin(db: Session):
    """添加系統管理員"""
    
    user_repo = SQLAlchemyUserRepository(db)
    
    print("👤 添加系統管理員...")
    
    # 檢查是否已存在
    existing_admin = user_repo.find_by_email("system@nailbooking.com")
    if existing_admin:
        print("⚠️  系統管理員帳號已存在")
        print(f"   帳號: {existing_admin.email}")
        print(f"   角色: {existing_admin.role}")
        return
    
    # 建立系統管理員帳號
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
    db.commit()
    
    print("✅ 系統管理員帳號已建立")
    print(f"   帳號: system@nailbooking.com")
    print(f"   密碼: system123")
    print(f"   角色: ADMIN")
    print("🎉 系統管理員添加完成！")

def main():
    """主函式"""
    print("🌱 添加系統管理員...")
    
    db = SessionLocal()
    try:
        add_system_admin(db)
    except Exception as e:
        print(f"❌ 添加失敗: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
