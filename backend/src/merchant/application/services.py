"""
Merchant Context - Application Layer - Services
MerchantService 協調商家業務邏輯
"""
from typing import Optional

from merchant.domain.models import Merchant, MerchantStatus
from merchant.domain.repositories import MerchantRepository
from merchant.domain.exceptions import (
    MerchantNotFoundError,
    MerchantInactiveError,
    MerchantSlugDuplicateError
)


class MerchantService:
    """
    MerchantService 應用服務
    
    職責：
    1. 商家查詢與驗證
    2. 商家狀態管理
    3. LINE 憑證管理
    """
    
    def __init__(self, merchant_repo: MerchantRepository):
        self.merchant_repo = merchant_repo
    
    def get_merchant(self, merchant_id: str) -> Merchant:
        """
        取得商家
        
        Args:
            merchant_id: 商家 ID
        
        Returns:
            商家聚合
        
        Raises:
            MerchantNotFoundError: 商家不存在
        """
        merchant = self.merchant_repo.find_by_id(merchant_id)
        
        if merchant is None:
            raise MerchantNotFoundError(merchant_id)
        
        return merchant
    
    def get_merchant_by_slug(self, slug: str) -> Merchant:
        """
        依 slug 取得商家
        
        Args:
            slug: 商家 slug
        
        Returns:
            商家聚合
        
        Raises:
            MerchantNotFoundError: 商家不存在
        """
        merchant = self.merchant_repo.find_by_slug(slug)
        
        if merchant is None:
            raise MerchantNotFoundError(f"slug={slug}")
        
        return merchant
    
    def validate_merchant_active(self, merchant_id: str) -> Merchant:
        """
        驗證商家為啟用狀態
        
        Args:
            merchant_id: 商家 ID
        
        Returns:
            商家聚合
        
        Raises:
            MerchantNotFoundError: 商家不存在
            MerchantInactiveError: 商家未啟用
        """
        merchant = self.get_merchant(merchant_id)
        
        if not merchant.can_accept_booking():
            raise MerchantInactiveError(merchant_id, merchant.status.value)
        
        return merchant
    
    def create_merchant(
        self,
        slug: str,
        name: str,
        timezone: str = "Asia/Taipei",
        address: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Merchant:
        """
        建立新商家
        
        Args:
            slug: 商家 slug（唯一識別碼）
            name: 商家名稱
            timezone: 時區
            address: 地址
            phone: 電話
        
        Returns:
            新建立的商家
        
        Raises:
            MerchantSlugDuplicateError: slug 已存在
        """
        # 檢查 slug 是否已存在
        if self.merchant_repo.exists_by_slug(slug):
            raise MerchantSlugDuplicateError(slug)
        
        # 建立商家（ID 由資料庫生成）
        from uuid import uuid4
        
        merchant = Merchant(
            id=str(uuid4()),
            slug=slug,
            name=name,
            timezone=timezone,
            address=address,
            phone=phone,
            status=MerchantStatus.ACTIVE
        )
        
        self.merchant_repo.save(merchant)
        
        return merchant
    
    def update_merchant_info(
        self,
        merchant_id: str,
        name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Merchant:
        """
        更新商家資訊
        
        Args:
            merchant_id: 商家 ID
            name: 新名稱
            address: 新地址
            phone: 新電話
            timezone: 新時區
        
        Returns:
            更新後的商家
        """
        merchant = self.get_merchant(merchant_id)
        
        merchant.update_info(
            name=name,
            address=address,
            phone=phone,
            timezone=timezone
        )
        
        self.merchant_repo.save(merchant)
        
        return merchant
    
    def suspend_merchant(self, merchant_id: str) -> Merchant:
        """暫停商家"""
        merchant = self.get_merchant(merchant_id)
        merchant.suspend()
        self.merchant_repo.save(merchant)
        return merchant
    
    def activate_merchant(self, merchant_id: str) -> Merchant:
        """啟用商家"""
        merchant = self.get_merchant(merchant_id)
        merchant.activate()
        self.merchant_repo.save(merchant)
        return merchant
    
    def list_active_merchants(self) -> list[Merchant]:
        """列出所有啟用商家"""
        return self.merchant_repo.find_all_active()

