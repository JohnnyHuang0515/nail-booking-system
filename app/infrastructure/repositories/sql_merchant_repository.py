"""
商家資料存取層
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.database.models import Merchant
from app.encryption import token_encryption_manager


class SQLMerchantRepository:
    """商家資料存取實作"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def find_by_channel_id(self, channel_id: str) -> Optional[Merchant]:
        """根據 LINE Channel ID 查找商家"""
        stmt = select(Merchant).where(
            Merchant.line_channel_id == channel_id,
            Merchant.is_active == True
        )
        result = self.db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    def find_by_id(self, merchant_id: UUID) -> Optional[Merchant]:
        """根據商家ID查找商家"""
        stmt = select(Merchant).where(
            Merchant.id == merchant_id,
            Merchant.is_active == True
        )
        result = self.db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    def create(self, name: str, line_channel_id: str, line_channel_secret: str, 
               line_channel_access_token: str, timezone: str = 'Asia/Taipei', 
               liff_id: str = None) -> Merchant:
        """創建新商家"""
        # 加密敏感資料
        encrypted_secret = token_encryption_manager.encrypt_access_token(line_channel_secret)
        encrypted_token = token_encryption_manager.encrypt_access_token(line_channel_access_token)
        
        merchant = Merchant(
            name=name,
            line_channel_id=line_channel_id,
            line_channel_secret=encrypted_secret,
            line_channel_access_token=encrypted_token,
            liff_id=liff_id,
            timezone=timezone
        )
        self.db_session.add(merchant)
        self.db_session.flush()
        return merchant
    
    def update_credentials(self, merchant_id: UUID, line_channel_secret: str = None, 
                          line_channel_access_token: str = None) -> Optional[Merchant]:
        """更新商家憑證"""
        merchant = self.find_by_id(merchant_id)
        if not merchant:
            return None
        
        if line_channel_secret:
            merchant.line_channel_secret = token_encryption_manager.encrypt_access_token(line_channel_secret)
        if line_channel_access_token:
            merchant.line_channel_access_token = token_encryption_manager.encrypt_access_token(line_channel_access_token)
        
        self.db_session.flush()
        return merchant
    
    def get_decrypted_merchant(self, merchant_id: UUID) -> Optional[dict]:
        """取得解密後的商家資料"""
        merchant = self.find_by_id(merchant_id)
        if not merchant:
            return None
        
        # 解密敏感資料
        merchant_data = {
            "id": merchant.id,
            "name": merchant.name,
            "line_channel_id": merchant.line_channel_id,
            "line_channel_secret": token_encryption_manager.decrypt_access_token(merchant.line_channel_secret),
            "line_channel_access_token": token_encryption_manager.decrypt_access_token(merchant.line_channel_access_token),
            "liff_id": merchant.liff_id,
            "timezone": merchant.timezone,
            "is_active": merchant.is_active,
            "created_at": merchant.created_at
        }
        
        return merchant_data
    
    def list_active(self) -> List[Merchant]:
        """列出所有活躍商家"""
        stmt = select(Merchant).where(Merchant.is_active == True)
        result = self.db_session.execute(stmt)
        return list(result.scalars().all())
    
    def deactivate(self, merchant_id: UUID) -> bool:
        """停用商家"""
        merchant = self.find_by_id(merchant_id)
        if not merchant:
            return False
        
        merchant.is_active = False
        self.db_session.flush()
        return True
