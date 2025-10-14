"""
Booking Context - Domain Layer - Domain Events
領域事件：記錄重要業務事實
"""
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from shared.event_bus import DomainEvent
from shared.timezone import now_utc


@dataclass
class BookingRequestedEvent(DomainEvent):
    """預約請求事件（初始狀態）"""
    
    @classmethod
    def create(cls, booking_id: str, merchant_id: str, payload: dict):
        return cls(
            event_id=str(uuid4()),
            occurred_at=now_utc(),
            aggregate_id=booking_id,
            aggregate_type="Booking",
            event_type="BookingRequested",
            payload=payload
        )


@dataclass
class BookingConfirmedEvent(DomainEvent):
    """預約確認事件（最重要）"""
    
    @classmethod
    def create(cls, booking_id: str, merchant_id: str, payload: dict):
        return cls(
            event_id=str(uuid4()),
            occurred_at=now_utc(),
            aggregate_id=booking_id,
            aggregate_type="Booking",
            event_type="BookingConfirmed",
            payload={
                **payload,
                "merchant_id": merchant_id,
                "line_user_id": payload.get("customer", {}).get("line_user_id")
            }
        )


@dataclass
class BookingCancelledEvent(DomainEvent):
    """預約取消事件"""
    
    @classmethod
    def create(
        cls,
        booking_id: str,
        merchant_id: str,
        cancelled_by: str,
        reason: str = ""
    ):
        return cls(
            event_id=str(uuid4()),
            occurred_at=now_utc(),
            aggregate_id=booking_id,
            aggregate_type="Booking",
            event_type="BookingCancelled",
            payload={
                "merchant_id": merchant_id,
                "cancelled_by": cancelled_by,
                "reason": reason
            }
        )


@dataclass
class BookingCompletedEvent(DomainEvent):
    """預約完成事件"""
    
    @classmethod
    def create(cls, booking_id: str, merchant_id: str, completed_at: datetime):
        return cls(
            event_id=str(uuid4()),
            occurred_at=now_utc(),
            aggregate_id=booking_id,
            aggregate_type="Booking",
            event_type="BookingCompleted",
            payload={
                "merchant_id": merchant_id,
                "completed_at": completed_at.isoformat()
            }
        )


@dataclass
class BookingRescheduledEvent(DomainEvent):
    """預約改期事件"""
    
    @classmethod
    def create(
        cls,
        booking_id: str,
        old_start_at: datetime,
        new_start_at: datetime
    ):
        return cls(
            event_id=str(uuid4()),
            occurred_at=now_utc(),
            aggregate_id=booking_id,
            aggregate_type="Booking",
            event_type="BookingRescheduled",
            payload={
                "old_start_at": old_start_at.isoformat(),
                "new_start_at": new_start_at.isoformat()
            }
        )

