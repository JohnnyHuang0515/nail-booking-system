"""
Merchant Context - Infrastructure Layer - Repository Implementation
使用 SQLAlchemy 實作 MerchantRepository
"""
from typing import Optional
from sqlalchemy.orm import Session

from merchant.domain.models import Merchant, MerchantStatus, LineCredentials
from merchant.domain.repositories import MerchantRepository
from merchant.infrastructure.orm.models import MerchantORM


class SQLAlchemyMerchantRepository(MerchantRepository):
    """SQLAlchemy 實作的 Merchant Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, merchant: Merchant) -> None:
        """儲存商家"""
        # 查詢是否已存在
        merchant_orm = self.db.query(MerchantORM).filter_by(id=merchant.id).first()
        
        if merchant_orm:
            # 更新現有記錄
            merchant_orm.name = merchant.name
            merchant_orm.status = merchant.status.value
            merchant_orm.timezone = merchant.timezone
            merchant_orm.address = merchant.address
            merchant_orm.phone = merchant.phone
            merchant_orm.line_channel_id = merchant.line_credentials.channel_id
            merchant_orm.line_channel_secret = merchant.line_credentials.channel_secret
            merchant_orm.line_channel_access_token = merchant.line_credentials.channel_access_token
            merchant_orm.line_bot_basic_id = merchant.line_credentials.bot_basic_id
            merchant_orm.extra_data = merchant.metadata
            merchant_orm.updated_at = merchant.updated_at
        else:
            # 新建記錄
            merchant_orm = MerchantORM(
                id=merchant.id,
                slug=merchant.slug,
                name=merchant.name,
                status=merchant.status.value,
                timezone=merchant.timezone,
                address=merchant.address,
                phone=merchant.phone,
                line_channel_id=merchant.line_credentials.channel_id,
                line_channel_secret=merchant.line_credentials.channel_secret,
                line_channel_access_token=merchant.line_credentials.channel_access_token,
                line_bot_basic_id=merchant.line_credentials.bot_basic_id,
                extra_data=merchant.metadata
            )
            self.db.add(merchant_orm)
        
        self.db.flush()
    
    def find_by_id(self, merchant_id: str) -> Optional[Merchant]:
        """依 ID 查詢商家"""
        merchant_orm = self.db.query(MerchantORM).filter_by(id=merchant_id).first()
        
        if merchant_orm is None:
            return None
        
        return self._to_domain(merchant_orm)
    
    def find_by_slug(self, slug: str) -> Optional[Merchant]:
        """依 slug 查詢商家"""
        merchant_orm = self.db.query(MerchantORM).filter_by(slug=slug).first()
        
        if merchant_orm is None:
            return None
        
        return self._to_domain(merchant_orm)
    
    def find_all_active(self) -> list[Merchant]:
        """查詢所有啟用商家"""
        merchants_orm = self.db.query(MerchantORM).filter_by(
            status=MerchantStatus.ACTIVE.value
        ).all()
        
        return [self._to_domain(m) for m in merchants_orm]
    
    def exists_by_slug(self, slug: str) -> bool:
        """檢查 slug 是否存在"""
        count = self.db.query(MerchantORM).filter_by(slug=slug).count()
        return count > 0
    
    def _to_domain(self, merchant_orm: MerchantORM) -> Merchant:
        """將 ORM 模型轉換為 Domain 模型"""
        return Merchant(
            id=merchant_orm.id,
            slug=merchant_orm.slug,
            name=merchant_orm.name,
            status=MerchantStatus(merchant_orm.status),
            timezone=merchant_orm.timezone,
            address=merchant_orm.address,
            phone=merchant_orm.phone,
            line_credentials=LineCredentials(
                channel_id=merchant_orm.line_channel_id,
                channel_secret=merchant_orm.line_channel_secret,
                channel_access_token=merchant_orm.line_channel_access_token,
                bot_basic_id=merchant_orm.line_bot_basic_id
            ),
            metadata=merchant_orm.extra_data or {},
            created_at=merchant_orm.created_at,
            updated_at=merchant_orm.updated_at
        )

