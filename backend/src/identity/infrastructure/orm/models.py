"""
Identity Context - Infrastructure Layer - ORM Models
SQLAlchemy ORM 模型定義
"""
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Index, text, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID

from shared.database import Base


class UserORM(Base):
    """User 聚合根 ORM 模型"""
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="用戶 ID (UUID)"
    )
    
    # 登入憑證
    email = Column(String(255), nullable=True, unique=True, comment="Email")
    line_user_id = Column(String(100), nullable=True, unique=True, comment="LINE User ID")
    password_hash = Column(Text, nullable=True, comment="密碼雜湊")
    
    # 基本資訊
    name = Column(String(200), nullable=True, comment="姓名")
    
    # 租戶隔離
    merchant_id = Column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="所屬商家 ID（租戶隔離）"
    )
    
    # 角色與權限
    role = Column(
        String(50),
        nullable=False,
        default="customer",
        comment="角色: admin/merchant_owner/merchant_staff/customer"
    )
    
    # 狀態
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    is_verified = Column(Boolean, nullable=False, default=False, comment="Email 是否已驗證")
    
    # 審計欄位
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最後登入時間"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="建立時間"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="更新時間"
    )
    
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_line_user_id", "line_user_id"),
        Index("idx_users_merchant_id", "merchant_id"),
        Index("idx_users_merchant_role", "merchant_id", "role"),
        {"comment": "用戶表"}
    )

