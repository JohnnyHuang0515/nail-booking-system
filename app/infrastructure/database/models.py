import uuid
from sqlalchemy import (Column, String, DateTime, Time, Date, Numeric, ForeignKey, 
                        Integer, Boolean, Enum as SQLAlchemyEnum, Text, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.booking.models import AppointmentStatus
from .session import Base


class Merchant(Base):
    """商家與 LINE 憑證"""
    __tablename__ = "merchants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    account = Column(String(50), unique=True, nullable=True, index=True)  # 商家登入帳號
    password_hash = Column(String(255), nullable=True)  # 商家登入密碼雜湊
    merchant_code = Column(String(20), unique=True, nullable=False, index=True)  # 商家代碼
    line_channel_id = Column(String(64), unique=True, nullable=False, index=True)
    line_channel_secret = Column(Text, nullable=False)
    line_channel_access_token = Column(Text, nullable=False)
    liff_id = Column(String(64), nullable=True)  # LIFF App ID
    timezone = Column(String(50), default='Asia/Taipei')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    users = relationship("User", back_populates="merchant", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="merchant", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    business_hours = relationship("BusinessHour", back_populates="merchant", cascade="all, delete-orphan")
    time_offs = relationship("TimeOff", back_populates="merchant", cascade="all, delete-orphan")
    billing_records = relationship("BillingRecord", back_populates="merchant", cascade="all, delete-orphan")


class User(Base):
    """使用者：同一人可在多商家各有一筆"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    line_user_id = Column(String(64), nullable=False)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 多租戶唯一約束：同一人在同一商家只能有一筆記錄
    __table_args__ = (
        UniqueConstraint('merchant_id', 'line_user_id', name='uq_user_merchant_line'),
    )

    # 關聯
    merchant = relationship("Merchant", back_populates="users")
    appointments = relationship("Appointment", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Service(Base):
    """服務：每商家自管"""
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # 可選分店ID
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    # 多租戶唯一約束：同一商家內服務名稱唯一
    __table_args__ = (
        UniqueConstraint('merchant_id', 'name', name='uq_service_merchant_name'),
    )

    # 關聯
    merchant = relationship("Merchant", back_populates="services")


class Appointment(Base):
    """預約：強綁商家"""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # 可選，支援直接預約
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # 可選分店ID
    staff_id = Column(UUID(as_uuid=True), nullable=True)   # 可選員工ID
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(SQLAlchemyEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 直接預約欄位 (當沒有user_id時使用)
    customer_name = Column(String(100), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # 多租戶唯一約束：同一商家、分店、時間、員工的時段唯一
    __table_args__ = (
        UniqueConstraint('merchant_id', 'branch_id', 'appointment_date', 'appointment_time', 'staff_id', 
                        name='uq_appointment_slot'),
    )

    # 關聯
    merchant = relationship("Merchant", back_populates="appointments")
    user = relationship("User", back_populates="appointments")
    service = relationship("Service")
    transaction = relationship("Transaction", back_populates="appointment", uselist=False)


class Transaction(Base):
    """交易：強綁商家"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    merchant = relationship("Merchant", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    appointment = relationship("Appointment", back_populates="transaction")


class BusinessHour(Base):
    """營業時間：每商家自管"""
    __tablename__ = "business_hours"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # 可選分店ID
    # 0=Monday, 1=Tuesday, ..., 6=Sunday
    day_of_week = Column(Integer, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # 關聯
    merchant = relationship("Merchant", back_populates="business_hours")


class TimeOff(Base):
    """休假時間：每商家自管"""
    __tablename__ = "time_off"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # 可選分店ID
    staff_id = Column(UUID(as_uuid=True), nullable=True)   # 可選員工ID
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    merchant = relationship("Merchant", back_populates="time_offs")


class BillingRecord(Base):
    """帳單記錄：每商家自管"""
    __tablename__ = "billing_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    plan = Column(String(50), nullable=False)  # 方案名稱
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default='pending')  # pending, paid, overdue
    billing_period_start = Column(Date, nullable=False)  # 帳單期間開始
    billing_period_end = Column(Date, nullable=False)    # 帳單期間結束
    due_date = Column(Date, nullable=False)              # 到期日
    paid_at = Column(DateTime(timezone=True), nullable=True)  # 付款時間
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    merchant = relationship("Merchant", back_populates="billing_records")