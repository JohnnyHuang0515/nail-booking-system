"""
Billing Context - Infrastructure Layer - ORM Models
SQLAlchemy ORM 模型定義
"""
from sqlalchemy import (
    Column, String, Integer, Numeric, DateTime, Boolean, Text,
    ForeignKey, CheckConstraint, Index, text
)
from sqlalchemy.dialects.postgresql import UUID, JSON

from shared.database import Base


class PlanORM(Base):
    """Plan 方案 ORM 模型"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="方案 ID")
    tier = Column(
        String(20),
        nullable=False,
        unique=True,
        comment="方案等級: free/basic/pro/enterprise"
    )
    name = Column(String(100), nullable=False, comment="方案名稱")
    description = Column(Text, nullable=True, comment="方案描述")
    
    # 價格
    price_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="價格金額"
    )
    price_currency = Column(
        String(3),
        nullable=False,
        default="TWD",
        comment="幣別"
    )
    
    billing_interval = Column(
        String(10),
        nullable=False,
        default="month",
        comment="計費週期: month/year"
    )
    
    # 功能額度（JSONB）
    features = Column(
        JSON,
        nullable=False,
        comment="方案功能: {max_bookings_per_month, max_staff, ...}"
    )
    
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    __table_args__ = (
        CheckConstraint(
            "tier IN ('free', 'basic', 'pro', 'enterprise')",
            name="chk_plan_tier"
        ),
        CheckConstraint(
            "billing_interval IN ('month', 'year')",
            name="chk_plan_billing_interval"
        ),
        Index("idx_plans_tier", "tier"),
        {"comment": "訂閱方案表"}
    )


class SubscriptionORM(Base):
    """Subscription 訂閱 ORM 模型"""
    __tablename__ = "subscriptions"
    
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="訂閱 ID (UUID)"
    )
    
    merchant_id = Column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="商家 ID"
    )
    
    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=False,
        comment="方案 ID"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default="trialing",
        comment="訂閱狀態: active/past_due/cancelled/trialing"
    )
    
    # 訂閱週期
    current_period_start = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="當前週期開始時間"
    )
    
    current_period_end = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="當前週期結束時間"
    )
    
    trial_end = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="試用期結束時間"
    )
    
    # Stripe 整合
    stripe_subscription_id = Column(
        String(100),
        nullable=True,
        unique=True,
        comment="Stripe 訂閱 ID"
    )
    
    stripe_customer_id = Column(
        String(100),
        nullable=True,
        comment="Stripe 客戶 ID"
    )
    
    # 審計欄位
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="取消時間"
    )
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'past_due', 'cancelled', 'trialing')",
            name="chk_subscription_status"
        ),
        Index("idx_subscriptions_merchant_status", "merchant_id", "status"),
        Index("idx_subscriptions_stripe_sub_id", "stripe_subscription_id"),
        {"comment": "訂閱表"}
    )

