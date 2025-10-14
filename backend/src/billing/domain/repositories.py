"""
Billing Context - Domain Layer - Repository Interfaces
定義 Subscription 和 Plan Repository 抽象介面
"""
from abc import ABC, abstractmethod
from typing import Optional

from .models import Subscription, Plan


class SubscriptionRepository(ABC):
    """Subscription Repository 抽象基類"""
    
    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        """儲存訂閱"""
        pass
    
    @abstractmethod
    def find_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """依 ID 查詢訂閱"""
        pass
    
    @abstractmethod
    def find_active_by_merchant(self, merchant_id: str) -> Optional[Subscription]:
        """
        查詢商家的啟用訂閱
        
        Args:
            merchant_id: 商家 ID
        
        Returns:
            啟用的訂閱，不存在則返回 None
        """
        pass
    
    @abstractmethod
    def find_by_stripe_subscription_id(self, stripe_sub_id: str) -> Optional[Subscription]:
        """依 Stripe 訂閱 ID 查詢"""
        pass


class PlanRepository(ABC):
    """Plan Repository 抽象基類"""
    
    @abstractmethod
    def find_by_id(self, plan_id: int) -> Optional[Plan]:
        """依 ID 查詢方案"""
        pass
    
    @abstractmethod
    def find_all_active(self) -> list[Plan]:
        """查詢所有啟用方案"""
        pass
    
    @abstractmethod
    def find_by_tier(self, tier: str) -> Optional[Plan]:
        """依等級查詢方案"""
        pass

