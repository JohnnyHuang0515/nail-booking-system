"""
Billing Context - Infrastructure Layer - Repository Implementation
使用 SQLAlchemy 實作 SubscriptionRepository
"""
from typing import Optional
from sqlalchemy.orm import Session

from billing.domain.models import Subscription, SubscriptionStatus
from billing.domain.repositories import SubscriptionRepository
from billing.infrastructure.orm.models import SubscriptionORM


class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    """SQLAlchemy 實作的 Subscription Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, subscription: Subscription) -> None:
        """儲存訂閱"""
        sub_orm = self.db.query(SubscriptionORM).filter_by(id=subscription.id).first()
        
        if sub_orm:
            # 更新現有記錄
            sub_orm.status = subscription.status.value
            sub_orm.current_period_start = subscription.current_period_start
            sub_orm.current_period_end = subscription.current_period_end
            sub_orm.trial_end = subscription.trial_end
            sub_orm.cancelled_at = subscription.cancelled_at
            sub_orm.updated_at = subscription.updated_at
            sub_orm.stripe_subscription_id = subscription.stripe_subscription_id
            sub_orm.stripe_customer_id = subscription.stripe_customer_id
        else:
            # 新建記錄
            sub_orm = SubscriptionORM(
                id=subscription.id,
                merchant_id=subscription.merchant_id,
                plan_id=subscription.plan_id,
                status=subscription.status.value,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                trial_end=subscription.trial_end,
                cancelled_at=subscription.cancelled_at,
                stripe_subscription_id=subscription.stripe_subscription_id,
                stripe_customer_id=subscription.stripe_customer_id
            )
            self.db.add(sub_orm)
        
        self.db.flush()
    
    def find_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """依 ID 查詢訂閱"""
        sub_orm = self.db.query(SubscriptionORM).filter_by(id=subscription_id).first()
        
        if sub_orm is None:
            return None
        
        return self._to_domain(sub_orm)
    
    def find_active_by_merchant(self, merchant_id: str) -> Optional[Subscription]:
        """查詢商家的啟用訂閱"""
        sub_orm = self.db.query(SubscriptionORM).filter(
            SubscriptionORM.merchant_id == merchant_id,
            SubscriptionORM.status.in_(['active', 'trialing', 'past_due'])
        ).order_by(
            SubscriptionORM.created_at.desc()
        ).first()
        
        if sub_orm is None:
            return None
        
        return self._to_domain(sub_orm)
    
    def find_by_stripe_subscription_id(self, stripe_sub_id: str) -> Optional[Subscription]:
        """依 Stripe 訂閱 ID 查詢"""
        sub_orm = self.db.query(SubscriptionORM).filter_by(
            stripe_subscription_id=stripe_sub_id
        ).first()
        
        if sub_orm is None:
            return None
        
        return self._to_domain(sub_orm)
    
    def _to_domain(self, sub_orm: SubscriptionORM) -> Subscription:
        """將 ORM 模型轉換為 Domain 模型"""
        return Subscription(
            id=sub_orm.id,
            merchant_id=sub_orm.merchant_id,
            plan_id=sub_orm.plan_id,
            status=SubscriptionStatus(sub_orm.status),
            current_period_start=sub_orm.current_period_start,
            current_period_end=sub_orm.current_period_end,
            trial_end=sub_orm.trial_end,
            cancelled_at=sub_orm.cancelled_at,
            created_at=sub_orm.created_at,
            updated_at=sub_orm.updated_at,
            stripe_subscription_id=sub_orm.stripe_subscription_id,
            stripe_customer_id=sub_orm.stripe_customer_id
        )

