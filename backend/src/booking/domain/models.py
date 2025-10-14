"""
Booking Context - Domain Layer - Aggregate Root
Booking 聚合：預約的生命週期管理
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from .value_objects import Money, Duration, TimeSlot
from .exceptions import (
    InvalidStatusTransitionError,
    BookingAlreadyCancelledError,
    BookingAlreadyCompletedError
)


class BookingStatus(str, Enum):
    """預約狀態"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class BookingItem:
    """
    預約項目（值物件）
    包含服務 + 加購選項
    """
    service_id: int
    service_name: str
    service_price: Money
    service_duration: Duration
    option_ids: list[int] = field(default_factory=list)
    option_names: list[str] = field(default_factory=list)
    option_prices: list[Money] = field(default_factory=list)
    option_durations: list[Duration] = field(default_factory=list)
    
    def total_price(self) -> Money:
        """計算單項總價"""
        total = self.service_price
        for option_price in self.option_prices:
            total = total + option_price
        return total
    
    def total_duration(self) -> Duration:
        """計算單項總時長"""
        total = self.service_duration
        for option_dur in self.option_durations:
            total = total + option_dur
        return total


@dataclass
class Customer:
    """客戶資訊（值物件）"""
    line_user_id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Booking:
    """
    Booking 聚合根
    
    不變式 (Invariants):
    1. total_price = Σ(item.total_price())
    2. total_duration = Σ(item.total_duration())
    3. end_at = start_at + total_duration
    4. 狀態轉移規則必須合法
    5. merchant_id 不可變更（租戶隔離）
    """
    
    def __init__(
        self,
        id: str,
        merchant_id: str,
        customer: Customer,
        staff_id: int,
        start_at: datetime,
        items: list[BookingItem],
        status: BookingStatus = BookingStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        cancelled_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        notes: Optional[str] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.customer = customer
        self.staff_id = staff_id
        self.start_at = start_at
        self.items = items
        self.status = status
        self.created_at = created_at or datetime.now(datetime.timezone.utc)
        self.updated_at = updated_at
        self.cancelled_at = cancelled_at
        self.completed_at = completed_at
        self.notes = notes
        
        # 驗證不變式
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證聚合不變式"""
        if len(self.items) == 0:
            raise ValueError("預約必須至少包含一個服務項目")
        
        if self.start_at.tzinfo is None:
            raise ValueError("start_at 必須包含時區資訊")
        
        # 驗證 end_at 正確計算
        calculated_end = self.start_at + self.total_duration().to_timedelta()
        if hasattr(self, '_end_at') and self._end_at != calculated_end:
            raise ValueError(
                f"end_at 計算錯誤: 預期 {calculated_end}, 實際 {self._end_at}"
            )
    
    @property
    def end_at(self) -> datetime:
        """
        計算結束時間（根據不變式）
        end_at = start_at + total_duration
        """
        return self.start_at + self.total_duration().to_timedelta()
    
    def total_price(self) -> Money:
        """
        計算總價格（根據不變式）
        total_price = Σ(item.total_price())
        """
        if not self.items:
            return Money.zero()
        
        total = self.items[0].total_price()
        for item in self.items[1:]:
            total = total + item.total_price()
        return total
    
    def total_duration(self) -> Duration:
        """
        計算總時長（根據不變式）
        total_duration = Σ(item.total_duration())
        """
        if not self.items:
            return Duration.zero()
        
        total = self.items[0].total_duration()
        for item in self.items[1:]:
            total = total + item.total_duration()
        return total
    
    def time_slot(self) -> TimeSlot:
        """取得預約時段"""
        return TimeSlot(start_at=self.start_at, end_at=self.end_at)
    
    def confirm(self):
        """確認預約"""
        if self.status not in [BookingStatus.PENDING]:
            raise InvalidStatusTransitionError(
                from_status=self.status.value,
                to_status=BookingStatus.CONFIRMED.value
            )
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now(datetime.timezone.utc)
    
    def cancel(self, cancelled_by: str, reason: str = ""):
        """取消預約"""
        if self.status == BookingStatus.COMPLETED:
            raise BookingAlreadyCompletedError(booking_id=self.id)
        
        if self.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelledError(booking_id=self.id)
        
        self.status = BookingStatus.CANCELLED
        self.cancelled_at = datetime.now(datetime.timezone.utc)
        self.updated_at = self.cancelled_at
    
    def complete(self):
        """完成預約"""
        if self.status != BookingStatus.CONFIRMED:
            raise InvalidStatusTransitionError(
                from_status=self.status.value,
                to_status=BookingStatus.COMPLETED.value
            )
        
        self.status = BookingStatus.COMPLETED
        self.completed_at = datetime.now(datetime.timezone.utc)
        self.updated_at = self.completed_at
    
    @classmethod
    def create_new(
        cls,
        merchant_id: str,
        customer: Customer,
        staff_id: int,
        start_at: datetime,
        items: list[BookingItem],
        notes: Optional[str] = None
    ) -> "Booking":
        """工廠方法：建立新預約"""
        return cls(
            id=str(uuid4()),
            merchant_id=merchant_id,
            customer=customer,
            staff_id=staff_id,
            start_at=start_at,
            items=items,
            status=BookingStatus.CONFIRMED,  # 直接確認（根據 BDD）
            notes=notes
        )
    
    def __repr__(self) -> str:
        return (
            f"<Booking(id={self.id}, merchant={self.merchant_id}, "
            f"staff={self.staff_id}, status={self.status.value}, "
            f"slot={self.start_at} - {self.end_at})>"
        )


@dataclass
class BookingLock:
    """
    預約鎖定（防重疊的輔助實體）
    
    用途：在建立 Booking 前先寫入 BookingLock
    PostgreSQL EXCLUDE 約束保證同一員工無重疊
    """
    id: str
    merchant_id: str
    staff_id: int
    start_at: datetime
    end_at: datetime
    booking_id: Optional[str] = None  # 關聯到 Booking
    created_at: Optional[datetime] = None
    
    @classmethod
    def create_for_booking(
        cls,
        merchant_id: str,
        staff_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> "BookingLock":
        """工廠方法：為預約建立鎖定"""
        return cls(
            id=str(uuid4()),
            merchant_id=merchant_id,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at,
            created_at=datetime.now(datetime.timezone.utc)
        )

