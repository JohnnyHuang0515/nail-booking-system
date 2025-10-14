"""
Merchant Context - Infrastructure Layer - ORM Models
SQLAlchemy ORM 模型定義
"""
from sqlalchemy import (
    Column, String, Text, JSON, DateTime, CheckConstraint, Index, text
)
from sqlalchemy.dialects.postgresql import UUID

from shared.database import Base


class MerchantORM(Base):
    """
    Merchant 聚合根 ORM 模型
    
    對應 Domain Model: merchant.domain.models.Merchant
    """
    __tablename__ = "merchants"
    
    # 主鍵
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="商家 ID (UUID)"
    )
    
    # 唯一識別碼
    slug = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="商家 slug（URL 友善識別碼）"
    )
    
    # 基本資訊
    name = Column(String(200), nullable=False, comment="商家名稱")
    
    status = Column(
        String(20),
        nullable=False,
        default="active",
        comment="商家狀態: active/suspended/cancelled"
    )
    
    # LINE 整合（加密儲存）
    line_channel_id = Column(String(100), nullable=True, comment="LINE Channel ID")
    line_channel_secret = Column(Text, nullable=True, comment="LINE Channel Secret（加密）")
    line_channel_access_token = Column(Text, nullable=True, comment="LINE Channel Access Token（加密）")
    line_bot_basic_id = Column(String(100), nullable=True, comment="LINE Bot Basic ID")
    
    # 設定
    timezone = Column(
        String(50),
        nullable=False,
        default="Asia/Taipei",
        comment="商家時區"
    )
    
    # 聯絡資訊
    address = Column(Text, nullable=True, comment="地址")
    phone = Column(String(20), nullable=True, comment="電話")
    
    # 擴充欄位
    extra_data = Column(
        JSON,
        nullable=False,
        default={},
        comment="其他元資料（JSONB）"
    )
    
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
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新時間"
    )
    
    # 約束與索引
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'cancelled')",
            name="chk_merchant_status"
        ),
        CheckConstraint(
            "slug ~ '^[a-z0-9-]+$'",
            name="chk_merchant_slug_format"
        ),
        Index("idx_merchants_status", "status"),
        {"comment": "商家主檔表"}
    )

