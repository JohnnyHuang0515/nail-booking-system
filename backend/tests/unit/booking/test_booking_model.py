"""
Booking Context - Unit Tests - Booking Aggregate
測試 Booking 聚合根的業務邏輯
"""
import pytest
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from booking.domain.models import Booking, BookingItem, BookingStatus, Customer
from booking.domain.value_objects import Money, Duration
from booking.domain.exceptions import (
    BookingAlreadyCompletedError,
    BookingAlreadyCancelledError
)
from shared.exceptions import InvalidStatusTransitionError


TZ = ZoneInfo("Asia/Taipei")


class TestBookingAggregate:
    """Booking 聚合根測試"""
    
    def test_create_booking_with_single_service(self):
        """✅ 測試案例：建立單一服務預約"""
        # Arrange
        customer = Customer(line_user_id="U123", name="王小明")
        items = [
            BookingItem(
                service_id=1,
                service_name="Gel Basic",
                service_price=Money(Decimal("800"), "TWD"),
                service_duration=Duration(60),
                option_ids=[],
                option_names=[],
                option_prices=[],
                option_durations=[]
            )
        ]
        start_at = datetime(2025, 10, 16, 14, 0, tzinfo=TZ)
        
        # Act
        booking = Booking.create_new(
            merchant_id="123e4567-e89b-12d3-a456-426614174000",
            customer=customer,
            staff_id=1,
            start_at=start_at,
            items=items
        )
        
        # Assert
        assert booking.id is not None
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.total_price().amount == Decimal("800")
        assert booking.total_duration().minutes == 60
        assert booking.end_at == datetime(2025, 10, 16, 15, 0, tzinfo=TZ)
    
    def test_total_price_calculation_with_options(self):
        """✅ 測試案例：含選項的總價計算"""
        # Arrange
        items = [
            BookingItem(
                service_id=1,
                service_name="Gel Basic",
                service_price=Money(Decimal("800")),
                service_duration=Duration(60),
                option_ids=[1, 2],
                option_names=["French", "Art"],
                option_prices=[Money(Decimal("200")), Money(Decimal("300"))],
                option_durations=[Duration(15), Duration(20)]
            )
        ]
        
        booking = Booking.create_new(
            merchant_id="test-merchant",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=items
        )
        
        # Act & Assert
        assert booking.total_price().amount == Decimal("1300")  # 800 + 200 + 300
        assert booking.total_duration().minutes == 95  # 60 + 15 + 20
    
    def test_confirm_pending_booking(self):
        """✅ 測試案例：確認待處理預約"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        booking.status = BookingStatus.PENDING
        
        # Act
        booking.confirm()
        
        # Assert
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.updated_at is not None
    
    def test_cancel_confirmed_booking(self):
        """✅ 測試案例：取消已確認預約"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        
        # Act
        booking.cancel(cancelled_by="U123", reason="時間不合適")
        
        # Assert
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancelled_at is not None
    
    def test_cannot_cancel_completed_booking(self):
        """✅ 測試案例：無法取消已完成預約"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        booking.complete()
        
        # Act & Assert
        with pytest.raises(BookingAlreadyCompletedError):
            booking.cancel(cancelled_by="U123")
    
    def test_cannot_cancel_already_cancelled_booking(self):
        """✅ 測試案例：無法重複取消"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        booking.cancel(cancelled_by="U123")
        
        # Act & Assert
        with pytest.raises(BookingAlreadyCancelledError):
            booking.cancel(cancelled_by="U123")
    
    def test_complete_confirmed_booking(self):
        """✅ 測試案例：完成已確認預約"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        
        # Act
        booking.complete()
        
        # Assert
        assert booking.status == BookingStatus.COMPLETED
        assert booking.completed_at is not None
    
    def test_cannot_complete_cancelled_booking(self):
        """✅ 測試案例：無法完成已取消預約"""
        # Arrange
        booking = Booking.create_new(
            merchant_id="test",
            customer=Customer(line_user_id="U123"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("800")),
                    service_duration=Duration(60),
                    option_ids=[],
                    option_names=[],
                    option_prices=[],
                    option_durations=[]
                )
            ]
        )
        booking.cancel(cancelled_by="U123")
        
        # Act & Assert
        with pytest.raises(InvalidStatusTransitionError):
            booking.complete()

