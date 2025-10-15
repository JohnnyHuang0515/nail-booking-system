#!/usr/bin/env python3
"""
檢查資料庫中的用戶
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from shared.database import SessionLocal
from identity.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

def check_users():
    """檢查資料庫中的用戶"""
    
    db = SessionLocal()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        
        print("👤 檢查資料庫中的用戶...")
        
        # 查詢特定商家的用戶
        merchant_id = "00000000-0000-0000-0000-000000000001"
        merchant_users = user_repo.find_by_merchant(merchant_id)
        
        print(f"✅ 找到商家 {merchant_id} 的 {len(merchant_users)} 個用戶：")
        print()
        
        for user in merchant_users:
            print(f"📧 帳號: {user.email}")
            print(f"👤 姓名: {user.name}")
            print(f"🔑 角色: {user.role.name.value}")
            print(f"🏪 商家: {user.merchant_id}")
            print(f"✅ 啟用: {user.is_active}")
            print(f"✉️  驗證: {user.is_verified}")
            print("-" * 50)
        
        # 檢查特定帳號
        admin_user = user_repo.find_by_email("admin@nailbooking.com")
        system_admin = user_repo.find_by_email("system@nailbooking.com")
        
        print("🎯 測試帳號確認：")
        if admin_user:
            print(f"   商家管理員帳號: {admin_user.email}")
            print(f"   密碼: admin123")
            print(f"   角色: {admin_user.role.name.value}")
        
        if system_admin:
            print(f"   系統管理員帳號: {system_admin.email}")
            print(f"   密碼: system123")
            print(f"   角色: {system_admin.role.name.value}")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
