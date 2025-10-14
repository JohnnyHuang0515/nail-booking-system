"""
Merchant Context - Domain Layer - Repository Interfaces
定義 Merchant Repository 抽象介面
"""
from abc import ABC, abstractmethod
from typing import Optional

from .models import Merchant


class MerchantRepository(ABC):
    """Merchant Repository 抽象基類"""
    
    @abstractmethod
    def save(self, merchant: Merchant) -> None:
        """
        儲存商家
        
        Args:
            merchant: 商家聚合
        """
        pass
    
    @abstractmethod
    def find_by_id(self, merchant_id: str) -> Optional[Merchant]:
        """
        依 ID 查詢商家
        
        Args:
            merchant_id: 商家 ID (UUID)
        
        Returns:
            商家聚合，不存在則返回 None
        """
        pass
    
    @abstractmethod
    def find_by_slug(self, slug: str) -> Optional[Merchant]:
        """
        依 slug 查詢商家
        
        Args:
            slug: 商家 slug（唯一識別碼）
        
        Returns:
            商家聚合，不存在則返回 None
        """
        pass
    
    @abstractmethod
    def find_all_active(self) -> list[Merchant]:
        """
        查詢所有啟用的商家
        
        Returns:
            啟用商家列表
        """
        pass
    
    @abstractmethod
    def exists_by_slug(self, slug: str) -> bool:
        """
        檢查 slug 是否已存在
        
        Args:
            slug: 商家 slug
        
        Returns:
            存在返回 True，否則 False
        """
        pass

