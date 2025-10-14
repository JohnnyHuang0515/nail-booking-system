"""
整合測試 - BookingRepository
測試資料庫 CRUD 操作與查詢
"""
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from booking.infrastructure.repositories.sqlalchemy_booking_repository import (
    SQLAlchemyBookingRepository
)
from booking.infrastructure.repositories.sqlalchemy_booking_lock_repository import (
    SQLAlchemyBookingLockRepository
)
from booking.domain.models import Booking, BookingItem, Customer, BookingStatus
from booking.domain.value_objects import Money, Duration


TZ = timezone(timedelta(hours=8))


class TestBookingRepository:
    """BookingRepository 整合測試"""
    
    def test_save_and_get_booking(self, db_session_commit):
        """✅ 測試案例：儲存並取得預約"""
        # Arrange
        repo = SQLAlchemyBookingRepository(db_session_commit)
        
        booking = Booking(
            id=str(uuid4()),
            merchant_id=str(uuid4()),
            customer=Customer(
                line_user_id="U123456789",
                name="王小明",
                phone="0912345678"
            ),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Gel Basic",
                    service_price=Money(Decimal("800"), "TWD"),
                    service_duration=Duration(60)
                )
            ],
            status=BookingStatus.CONFIRMED
        )
        
        # Act
        repo.save(booking)
        db_session_commit.commit()
        
        # Assert - 重新取得
        retrieved = repo.find_by_id(booking.id, booking.merchant_id)
        assert retrieved is not None
        assert retrieved.id == booking.id
        assert retrieved.customer.line_user_id == "U123456789"
        assert retrieved.status == BookingStatus.CONFIRMED
        assert retrieved.total_price().amount == Decimal("800")
        assert len(retrieved.items) == 1
    
    def test_update_booking_status(self, db_session_commit):
        """✅ 測試案例：更新預約狀態"""
        # Arrange
        repo = SQLAlchemyBookingRepository(db_session_commit)
        
        booking = Booking(
            id=str(uuid4()),
            merchant_id=str(uuid4()),
            customer=Customer(line_user_id="U123", name="Test"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("500")),
                    service_duration=Duration(30)
                )
            ],
            status=BookingStatus.PENDING
        )
        
        repo.save(booking)
        db_session_commit.commit()
        
        # Act - 更新狀態
        booking.confirm()
        repo.save(booking)
        db_session_commit.commit()
        
        # Assert
        retrieved = repo.find_by_id(booking.id, test_merchant_id)
        assert retrieved.status == BookingStatus.CONFIRMED
    
    def test_list_bookings_by_merchant(self, db_session_commit):
        """✅ 測試案例：依商家 ID 列出預約"""
        # Arrange
        repo = SQLAlchemyBookingRepository(db_session_commit)
        merchant_id = str(uuid4())
        
        # 建立兩個預約
        for i in range(2):
            booking = Booking(
                id=str(uuid4()),
                merchant_id=merchant_id,
                customer=Customer(line_user_id=f"U{i}", name=f"User{i}"),
                staff_id=1,
                start_at=datetime(2025, 10, 16, 10 + i, 0, tzinfo=TZ),
                items=[
                    BookingItem(
                        service_id=1,
                        service_name="Test",
                        price=Money(Decimal("500")),
                        duration=Duration(30),
                        option_ids=[],
                        options=[]
                    )
                ],
                status=BookingStatus.CONFIRMED
            )
            repo.save(booking)
        
        db_session_commit.commit()
        
        # Act
        bookings = repo.list_by_merchant(merchant_id)
        
        # Assert
        assert len(bookings) == 2
        assert all(b.merchant_id == merchant_id for b in bookings)
    
    def test_list_bookings_by_date_range(self, db_session_commit):
        """✅ 測試案例：依日期範圍查詢預約"""
        # Arrange
        repo = SQLAlchemyBookingRepository(db_session_commit)
        merchant_id = str(uuid4())
        
        # 建立不同日期的預約
        dates = [
            datetime(2025, 10, 15, 10, 0, tzinfo=TZ),  # 前一天
            datetime(2025, 10, 16, 10, 0, tzinfo=TZ),  # 目標日
            datetime(2025, 10, 17, 10, 0, tzinfo=TZ),  # 後一天
        ]
        
        for i, dt in enumerate(dates):
            booking = Booking(
                id=str(uuid4()),
                merchant_id=merchant_id,
                customer=Customer(line_user_id=f"U{i}", name=f"User{i}"),
                staff_id=1,
                start_at=dt,
                items=[
                    BookingItem(
                        service_id=1,
                        service_name="Test",
                        price=Money(Decimal("500")),
                        duration=Duration(30),
                        option_ids=[],
                        options=[]
                    )
                ],
                status=BookingStatus.CONFIRMED
            )
            repo.save(booking)
        
        db_session_commit.commit()
        
        # Act - 只查詢 10/16 的預約
        from_date = datetime(2025, 10, 16, 0, 0, tzinfo=TZ)
        to_date = datetime(2025, 10, 17, 0, 0, tzinfo=TZ)
        
        bookings = repo.list_by_date_range(
            merchant_id=merchant_id,
            from_date=from_date,
            to_date=to_date
        )
        
        # Assert
        assert len(bookings) == 1
        assert bookings[0].start_at.date() == from_date.date()
    
    def test_delete_booking(self, db_session_commit):
        """✅ 測試案例：刪除預約"""
        # Arrange
        repo = SQLAlchemyBookingRepository(db_session_commit)
        
        booking = Booking(
            id=str(uuid4()),
            merchant_id=str(uuid4()),
            customer=Customer(line_user_id="U123", name="Test"),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            items=[
                BookingItem(
                    service_id=1,
                    service_name="Test",
                    service_price=Money(Decimal("500")),
                    service_duration=Duration(30)
                )
            ],
            status=BookingStatus.CONFIRMED
        )
        
        repo.save(booking)
        db_session_commit.commit()
        
        # Act
        repo.delete(booking.id)
        db_session_commit.commit()
        
        # Assert
        retrieved = repo.find_by_id(booking.id, test_merchant_id)
        assert retrieved is None


class TestBookingLockRepository:
    """BookingLockRepository 整合測試（簡化版）"""
    
    def test_create_and_find_lock(self, db_session_commit):
        """✅ 測試案例：建立並查詢鎖定"""
        # Arrange
        repo = SQLAlchemyBookingLockRepository(db_session_commit)
        merchant_id = str(uuid4())
        
        from booking.domain.models import BookingLock
        
        # Act - 建立鎖
        lock = BookingLock(
            id=str(uuid4()),
            merchant_id=merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
        )
        
        repo.save(lock)
        db_session_commit.commit()
        
        # Assert - 查詢鎖
        retrieved = repo.find_by_id(lock.id)
        assert retrieved is not None
        assert retrieved.staff_id == 1
        assert retrieved.merchant_id == merchant_id

