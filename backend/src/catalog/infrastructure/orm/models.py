"""
Catalog Context - Infrastructure Layer - ORM Models
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Numeric, Text, Time, Date,
    ForeignKey, Index, CheckConstraint, text, JSON
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from shared.database import Base


class ServiceORM(Base):
    """服務 ORM 模型"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    
    name = Column(String(100), nullable=False, comment="服務名稱")
    category = Column(String(20), nullable=False, default="basic", comment="分類")
    description = Column(Text, nullable=True, comment="描述")
    
    base_price_amount = Column(Numeric(10, 2), nullable=False, comment="基礎價格")
    base_price_currency = Column(String(3), nullable=False, default="TWD")
    base_duration_minutes = Column(Integer, nullable=False, comment="基礎時長")
    
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    allow_stack = Column(Boolean, nullable=False, default=True, comment="允許堆疊")
    
    # 關聯
    options = relationship("ServiceOptionORM", back_populates="service", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_services_merchant_active", "merchant_id", "is_active"),
        CheckConstraint("base_price_amount >= 0", name="chk_service_price_positive"),
        CheckConstraint("base_duration_minutes > 0", name="chk_service_duration_positive"),
        {"comment": "服務表"}
    )


class ServiceOptionORM(Base):
    """服務加購選項 ORM 模型"""
    __tablename__ = "service_options"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False, comment="選項名稱")
    add_price_amount = Column(Numeric(10, 2), nullable=False, comment="加價")
    add_price_currency = Column(String(3), nullable=False, default="TWD")
    add_duration_minutes = Column(Integer, nullable=False, comment="增加時長")
    
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0, comment="顯示順序")
    
    # 關聯
    service = relationship("ServiceORM", back_populates="options")
    
    __table_args__ = (
        Index("idx_service_options_service", "service_id", "is_active"),
        CheckConstraint("add_price_amount >= 0", name="chk_option_price_positive"),
        CheckConstraint("add_duration_minutes >= 0", name="chk_option_duration_positive"),
        {"comment": "服務加購選項表"}
    )


class StaffORM(Base):
    """員工 ORM 模型"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    
    name = Column(String(100), nullable=False, comment="姓名")
    email = Column(String(255), nullable=True, comment="Email")
    phone = Column(String(20), nullable=True, comment="電話")
    
    skills = Column(
        ARRAY(Integer),
        nullable=False,
        default=[],
        comment="技能（service_id 陣列）"
    )
    
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    
    # 關聯
    working_hours = relationship("StaffWorkingHoursORM", back_populates="staff", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_staff_merchant_active", "merchant_id", "is_active"),
        Index("idx_staff_skills", "skills", postgresql_using="gin"),  # GIN 索引用於陣列查詢
        {"comment": "員工表"}
    )


class StaffWorkingHoursORM(Base):
    """員工工時 ORM 模型"""
    __tablename__ = "staff_working_hours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    
    day_of_week = Column(Integer, nullable=False, comment="星期（0=Monday, 6=Sunday）")
    start_time = Column(Time, nullable=False, comment="開始時間")
    end_time = Column(Time, nullable=False, comment="結束時間")
    
    # 關聯
    staff = relationship("StaffORM", back_populates="working_hours")
    
    __table_args__ = (
        Index("idx_staff_working_hours_staff_day", "staff_id", "day_of_week"),
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="chk_day_of_week_range"),
        CheckConstraint("start_time < end_time", name="chk_working_hours_time_order"),
        # 同一員工同一天不可有重複工時
        Index("uq_staff_working_hours_staff_day", "staff_id", "day_of_week", unique=True),
        {"comment": "員工工時表"}
    )


class HolidayORM(Base):
    """休假日 ORM 模型"""
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    
    holiday_date = Column(Date, nullable=False, comment="休假日期")
    name = Column(String(100), nullable=False, comment="休假名稱")
    is_recurring = Column(Boolean, nullable=False, default=False, comment="是否每年重複")
    
    __table_args__ = (
        Index("idx_holidays_merchant_date", "merchant_id", "holiday_date"),
        # 同一商家同一日期不可重複設定休假
        Index("uq_holidays_merchant_date", "merchant_id", "holiday_date", unique=True),
        {"comment": "休假日表"}
    )

