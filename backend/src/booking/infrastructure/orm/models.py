"""
Booking Context - Infrastructure Layer - ORM Models
SQLAlchemy ORM 模型定義
"""
from sqlalchemy import (
    Column, String, Integer, DateTime, Numeric, Text, JSON,
    ForeignKey, Index, CheckConstraint, text
)
from sqlalchemy.dialects.postgresql import UUID, TSTZRANGE
from sqlalchemy.orm import relationship
from datetime import datetime

from shared.database import Base


class BookingORM(Base):
    """
    Booking 聚合根 ORM 模型
    
    對應 Domain Model: booking.domain.models.Booking
    """
    __tablename__ = "bookings"
    
    # 主鍵
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="預約 ID (UUID)"
    )
    
    # 租戶隔離
    merchant_id = Column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="商家 ID（租戶隔離）"
    )
    
    # 核心欄位
    staff_id = Column(Integer, nullable=False, comment="員工 ID")
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="狀態: pending/confirmed/completed/cancelled"
    )
    
    # 時間欄位
    start_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="開始時間（含時區）"
    )
    end_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="結束時間（計算欄位，儲存以利查詢）"
    )
    
    # 客戶資訊（JSONB）
    customer = Column(
        JSON,
        nullable=False,
        comment="客戶資訊: {line_user_id, name, phone, email}"
    )
    
    # 預約項目（JSONB 陣列）
    items = Column(
        JSON,
        nullable=False,
        comment="預約項目陣列: [{service_id, service_name, ...}]"
    )
    
    # 計算欄位（denormalized for query performance）
    total_price_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="總價金額"
    )
    total_price_currency = Column(
        String(3),
        nullable=False,
        default="TWD",
        comment="幣別"
    )
    total_duration_minutes = Column(
        Integer,
        nullable=False,
        comment="總時長（分鐘）"
    )
    
    # 備註
    notes = Column(Text, nullable=True, comment="備註")
    
    # 審計欄位
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=datetime.utcnow,
        comment="更新時間"
    )
    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="取消時間"
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成時間"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_bookings_merchant_staff_time", "merchant_id", "staff_id", "start_at"),
        Index("idx_bookings_merchant_status", "merchant_id", "status"),
        Index("idx_bookings_customer_line_id", "merchant_id", text("(customer->>'line_user_id')")),
        CheckConstraint("status IN ('pending', 'confirmed', 'completed', 'cancelled')", name="chk_booking_status"),
        CheckConstraint("start_at < end_at", name="chk_booking_time_order"),
        CheckConstraint("total_duration_minutes > 0", name="chk_booking_duration_positive"),
        {"comment": "預約主表"}
    )


class BookingLockORM(Base):
    """
    BookingLock ORM 模型
    
    關鍵：使用 PostgreSQL EXCLUDE 約束防止重疊
    """
    __tablename__ = "booking_locks"
    
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="鎖定 ID"
    )
    
    merchant_id = Column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="商家 ID"
    )
    
    staff_id = Column(Integer, nullable=False, comment="員工 ID")
    
    start_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="開始時間"
    )
    
    end_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="結束時間"
    )
    
    booking_id = Column(
        UUID(as_uuid=False),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=True,
        comment="關聯的預約 ID"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    # ⚠️ 重要：EXCLUDE 約束在 Alembic migration 中定義
    # 無法直接在 SQLAlchemy 宣告式模型中定義
    # 見: migrations/versions/002_add_exclude_constraint.py
    
    __table_args__ = (
        Index("idx_booking_locks_merchant_staff", "merchant_id", "staff_id"),
        CheckConstraint("start_at < end_at", name="chk_lock_time_order"),
        {"comment": "預約鎖定表（EXCLUDE 約束防重疊）"}
    )

