"""
Billing Context - Application Layer - Services
BillingService 協調訂閱與計費邏輯
"""
from typing import Optional
from datetime import datetime, timedelta, timezone as dt_timezone

from billing.domain.models import Subscription, Plan, SubscriptionStatus, PlanTier
from billing.domain.repositories import SubscriptionRepository, PlanRepository
from billing.domain.exceptions import (
    SubscriptionNotFoundError,
    NoActiveSubscriptionError,
    SubscriptionPastDueError,
    PlanNotFoundError,
    QuotaExceededError
)


class BillingService:
    """
    BillingService 應用服務
    
    職責：
    1. 訂閱狀態查詢與驗證
    2. 方案額度檢查
    3. 訂閱生命週期管理
    """
    
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
    
    def get_active_subscription(self, merchant_id: str) -> Subscription:
        """
        取得商家的啟用訂閱
        
        Args:
            merchant_id: 商家 ID
        
        Returns:
            訂閱聚合
        
        Raises:
            NoActiveSubscriptionError: 無啟用訂閱
        """
        subscription = self.subscription_repo.find_active_by_merchant(merchant_id)
        
        if subscription is None:
            raise NoActiveSubscriptionError(merchant_id)
        
        return subscription
    
    def validate_can_create_booking(self, merchant_id: str) -> Subscription:
        """
        驗證商家可建立預約
        
        Args:
            merchant_id: 商家 ID
        
        Returns:
            訂閱聚合
        
        Raises:
            NoActiveSubscriptionError: 無訂閱
            SubscriptionPastDueError: 訂閱逾期
        """
        subscription = self.get_active_subscription(merchant_id)
        
        if not subscription.can_create_booking():
            raise SubscriptionPastDueError(merchant_id)
        
        return subscription
    
    def check_booking_quota(
        self,
        merchant_id: str,
        current_month_bookings: int
    ) -> bool:
        """
        檢查預約額度
        
        Args:
            merchant_id: 商家 ID
            current_month_bookings: 本月已建立預約數
        
        Returns:
            是否在額度內
        
        Raises:
            NoActiveSubscriptionError: 無訂閱
            QuotaExceededError: 超過額度
        """
        subscription = self.get_active_subscription(merchant_id)
        plan = self.plan_repo.find_by_id(subscription.plan_id)
        
        if plan is None:
            raise PlanNotFoundError(subscription.plan_id)
        
        if not plan.features.allows_booking_creation(current_month_bookings):
            raise QuotaExceededError(
                resource="bookings_per_month",
                limit=plan.features.max_bookings_per_month,
                current=current_month_bookings
            )
        
        return True
    
    def create_subscription(
        self,
        merchant_id: str,
        plan_id: int,
        trial_days: int = 14
    ) -> Subscription:
        """
        建立訂閱（含試用期）
        
        Args:
            merchant_id: 商家 ID
            plan_id: 方案 ID
            trial_days: 試用天數
        
        Returns:
            新訂閱
        """
        # 驗證方案存在
        plan = self.plan_repo.find_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundError(plan_id)
        
        # 建立訂閱
        from uuid import uuid4
        
        now = datetime.now(dt_timezone.utc)
        trial_end = now + timedelta(days=trial_days)
        
        subscription = Subscription(
            id=str(uuid4()),
            merchant_id=merchant_id,
            plan_id=plan_id,
            status=SubscriptionStatus.TRIALING,
            current_period_start=now,
            current_period_end=trial_end,
            trial_end=trial_end
        )
        
        self.subscription_repo.save(subscription)
        
        return subscription
    
    def activate_subscription(self, subscription_id: str) -> Subscription:
        """啟用訂閱（付款成功）"""
        subscription = self.subscription_repo.find_by_id(subscription_id)
        
        if subscription is None:
            raise SubscriptionNotFoundError(subscription_id)
        
        subscription.activate()
        self.subscription_repo.save(subscription)
        
        return subscription
    
    def mark_subscription_past_due(self, subscription_id: str) -> Subscription:
        """標記訂閱逾期（付款失敗）"""
        subscription = self.subscription_repo.find_by_id(subscription_id)
        
        if subscription is None:
            raise SubscriptionNotFoundError(subscription_id)
        
        subscription.mark_past_due()
        self.subscription_repo.save(subscription)
        
        return subscription
    
    def cancel_subscription(self, subscription_id: str) -> Subscription:
        """取消訂閱"""
        subscription = self.subscription_repo.find_by_id(subscription_id)
        
        if subscription is None:
            raise SubscriptionNotFoundError(subscription_id)
        
        subscription.cancel()
        self.subscription_repo.save(subscription)
        
        return subscription
    
    def get_plan(self, plan_id: int) -> Plan:
        """取得方案"""
        plan = self.plan_repo.find_by_id(plan_id)
        
        if plan is None:
            raise PlanNotFoundError(plan_id)
        
        return plan
    
    def list_active_plans(self) -> list[Plan]:
        """列出所有啟用方案"""
        return self.plan_repo.find_all_active()

