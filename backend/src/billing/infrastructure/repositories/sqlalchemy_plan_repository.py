"""
Billing Context - Infrastructure Layer - Plan Repository Implementation
使用 SQLAlchemy 實作 PlanRepository
"""
from typing import Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from billing.domain.models import Plan, PlanTier, PlanFeatures
from billing.domain.repositories import PlanRepository
from billing.infrastructure.orm.models import PlanORM
from booking.domain.value_objects import Money


class SQLAlchemyPlanRepository(PlanRepository):
    """SQLAlchemy 實作的 Plan Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, plan_id: int) -> Optional[Plan]:
        """依 ID 查詢方案"""
        plan_orm = self.db.query(PlanORM).filter_by(id=plan_id).first()
        
        if plan_orm is None:
            return None
        
        return self._to_domain(plan_orm)
    
    def find_all_active(self) -> list[Plan]:
        """查詢所有啟用方案"""
        plans_orm = self.db.query(PlanORM).filter_by(is_active=True).all()
        
        return [self._to_domain(p) for p in plans_orm]
    
    def find_by_tier(self, tier: str) -> Optional[Plan]:
        """依等級查詢方案"""
        plan_orm = self.db.query(PlanORM).filter_by(tier=tier, is_active=True).first()
        
        if plan_orm is None:
            return None
        
        return self._to_domain(plan_orm)
    
    def _to_domain(self, plan_orm: PlanORM) -> Plan:
        """將 ORM 模型轉換為 Domain 模型"""
        features_data = plan_orm.features
        
        features = PlanFeatures(
            max_bookings_per_month=features_data.get("max_bookings_per_month", 30),
            max_staff=features_data.get("max_staff", 1),
            max_services=features_data.get("max_services", 5),
            enable_line_notification=features_data.get("enable_line_notification", False),
            enable_custom_branding=features_data.get("enable_custom_branding", False),
            enable_analytics=features_data.get("enable_analytics", False),
            support_level=features_data.get("support_level", "email")
        )
        
        return Plan(
            id=plan_orm.id,
            tier=PlanTier(plan_orm.tier),
            name=plan_orm.name,
            price=Money(
                amount=Decimal(str(plan_orm.price_amount)),
                currency=plan_orm.price_currency
            ),
            billing_interval=plan_orm.billing_interval,
            features=features,
            is_active=plan_orm.is_active,
            description=plan_orm.description
        )

