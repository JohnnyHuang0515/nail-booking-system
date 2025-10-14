"""
Billing Context - Domain Layer - Aggregates
Subscription 訂閱與 Plan 方案聚合
"""
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from booking.domain.value_objects import Money


class PlanTier(str, Enum):
    """方案等級"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """訂閱狀態"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"


@dataclass
class PlanFeatures:
    """
    方案功能（值物件）
    
    定義每個方案可使用的功能額度
    """
    max_bookings_per_month: int  # 每月最大預約數
    max_staff: int  # 最大員工數
    max_services: int  # 最大服務數
    enable_line_notification: bool = True  # LINE 推播
    enable_custom_branding: bool = False  # 客製化品牌
    enable_analytics: bool = False  # 數據分析
    support_level: str = "email"  # 支援等級：email, chat, priority
    
    def allows_booking_creation(self, current_month_bookings: int) -> bool:
        """檢查是否可建立新預約"""
        return current_month_bookings < self.max_bookings_per_month


class Plan:
    """
    Plan 聚合根（方案）
    
    不變式：
    1. price >= 0
    2. billing_interval in ['month', 'year']
    3. features 不可為空
    """
    
    def __init__(
        self,
        id: int,
        tier: PlanTier,
        name: str,
        price: Money,
        billing_interval: str = "month",  # month, year
        features: Optional[PlanFeatures] = None,
        is_active: bool = True,
        description: Optional[str] = None
    ):
        self.id = id
        self.tier = tier
        self.name = name
        self.price = price
        self.billing_interval = billing_interval
        self.features = features or self._default_features_for_tier(tier)
        self.is_active = is_active
        self.description = description
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if self.price.amount < 0:
            raise ValueError("方案價格不可為負數")
        
        if self.billing_interval not in ["month", "year"]:
            raise ValueError("計費週期只能為 month 或 year")
    
    def _default_features_for_tier(self, tier: PlanTier) -> PlanFeatures:
        """根據等級返回預設功能"""
        if tier == PlanTier.FREE:
            return PlanFeatures(
                max_bookings_per_month=30,
                max_staff=1,
                max_services=5,
                enable_line_notification=False,
                enable_custom_branding=False,
                enable_analytics=False,
                support_level="email"
            )
        elif tier == PlanTier.BASIC:
            return PlanFeatures(
                max_bookings_per_month=100,
                max_staff=3,
                max_services=20,
                enable_line_notification=True,
                enable_custom_branding=False,
                enable_analytics=False,
                support_level="email"
            )
        elif tier == PlanTier.PRO:
            return PlanFeatures(
                max_bookings_per_month=500,
                max_staff=10,
                max_services=100,
                enable_line_notification=True,
                enable_custom_branding=True,
                enable_analytics=True,
                support_level="chat"
            )
        else:  # ENTERPRISE
            return PlanFeatures(
                max_bookings_per_month=9999,
                max_staff=999,
                max_services=999,
                enable_line_notification=True,
                enable_custom_branding=True,
                enable_analytics=True,
                support_level="priority"
            )
    
    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, tier={self.tier.value}, price={self.price.amount})>"


class Subscription:
    """
    Subscription 聚合根（訂閱）
    
    不變式：
    1. merchant_id 不可為空
    2. status 為 active 或 trialing 才能使用功能
    3. past_due 狀態下應降級功能
    4. current_period_end >= current_period_start
    """
    
    def __init__(
        self,
        id: str,  # UUID
        merchant_id: str,
        plan_id: int,
        status: SubscriptionStatus = SubscriptionStatus.TRIALING,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        trial_end: Optional[datetime] = None,
        cancelled_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        # Stripe/Payment Gateway 相關
        stripe_subscription_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.plan_id = plan_id
        self.status = status
        self.current_period_start = current_period_start or datetime.now(dt_timezone.utc)
        self.current_period_end = current_period_end
        self.trial_end = trial_end
        self.cancelled_at = cancelled_at
        self.created_at = created_at or datetime.now(dt_timezone.utc)
        self.updated_at = updated_at
        self.stripe_subscription_id = stripe_subscription_id
        self.stripe_customer_id = stripe_customer_id
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if not self.merchant_id:
            raise ValueError("訂閱必須關聯到商家")
        
        if self.current_period_end and self.current_period_end < self.current_period_start:
            raise ValueError("訂閱結束時間必須晚於開始時間")
    
    def is_active(self) -> bool:
        """檢查訂閱是否為啟用狀態"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    def can_create_booking(self) -> bool:
        """
        檢查是否可建立預約
        
        規則：
        1. 訂閱狀態為 active 或 trialing
        2. 未逾期（past_due 應拒絕）
        """
        if self.status == SubscriptionStatus.PAST_DUE:
            return False
        
        if self.status == SubscriptionStatus.CANCELLED:
            return False
        
        return True
    
    def activate(self):
        """啟用訂閱（付款成功後）"""
        self.status = SubscriptionStatus.ACTIVE
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def mark_past_due(self):
        """標記為逾期（付款失敗）"""
        self.status = SubscriptionStatus.PAST_DUE
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def cancel(self):
        """取消訂閱"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now(dt_timezone.utc)
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def renew(self, new_period_end: datetime):
        """續訂（更新週期）"""
        self.current_period_start = self.current_period_end or datetime.now(dt_timezone.utc)
        self.current_period_end = new_period_end
        self.status = SubscriptionStatus.ACTIVE
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, merchant_id={self.merchant_id}, status={self.status.value})>"

