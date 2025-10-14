"""
整合測試 - PostgreSQL EXCLUDE 約束
測試核心反重疊機制：同一員工同一時間不可有重疊預約
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from booking.infrastructure.orm.models import BookingLockORM


TZ = timezone(timedelta(hours=8))


class TestBookingLockExcludeConstraint:
    """測試 PostgreSQL EXCLUDE USING GIST 約束"""
    
    def test_non_overlapping_locks_allowed(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：非重疊時段可成功建立"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
        )
        
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),  # 緊接著第一個鎖
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ)
        )
        
        # Act & Assert
        db_session_commit.add(lock1)
        db_session_commit.commit()  # 第一個鎖成功
        
        db_session_commit.add(lock2)
        db_session_commit.commit()  # 第二個鎖也成功（無重疊）
        
        # Verify
        locks = db_session_commit.query(BookingLockORM).all()
        assert len(locks) == 2
    
    def test_overlapping_locks_rejected(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：重疊時段被 EXCLUDE 約束拒絕"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 30, tzinfo=TZ),
        )
        
        db_session_commit.add(lock1)
        db_session_commit.commit()  # 第一個鎖成功
        
        # Act: 嘗試插入重疊的鎖
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 30, tzinfo=TZ),  # 重疊！
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ),
        )
        
        db_session_commit.add(lock2)
        
        # Assert: 應拋出 IntegrityError
        with pytest.raises(IntegrityError) as exc_info:
            db_session_commit.commit()
        
        # Verify 錯誤訊息包含約束名稱
        assert "no_overlap_booking_locks" in str(exc_info.value).lower()
    
    def test_overlapping_partial_start(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：部分重疊（開始時間在範圍內）被拒絕"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ),
        )
        
        db_session_commit.add(lock1)
        db_session_commit.commit()
        
        # Act: 嘗試插入部分重疊的鎖（開始時間在範圍內）
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),  # 在範圍內
            end_at=datetime(2025, 10, 16, 13, 0, tzinfo=TZ),
        )
        
        db_session_commit.add(lock2)
        
        # Assert
        with pytest.raises(IntegrityError):
            db_session_commit.commit()
    
    def test_overlapping_contains(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：完全包含的時段被拒絕"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ),
        )
        
        db_session_commit.add(lock1)
        db_session_commit.commit()
        
        # Act: 嘗試插入被包含的鎖
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 30, tzinfo=TZ),  # 被包含
            end_at=datetime(2025, 10, 16, 11, 30, tzinfo=TZ),
        )
        
        db_session_commit.add(lock2)
        
        # Assert
        with pytest.raises(IntegrityError):
            db_session_commit.commit()
    
    def test_different_staff_same_time_allowed(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：不同員工同一時間可成功建立"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),
        )
        
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=2,  # 不同員工
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),  # 同一時間
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),
        )
        
        # Act & Assert
        db_session_commit.add(lock1)
        db_session_commit.commit()
        
        db_session_commit.add(lock2)
        db_session_commit.commit()  # 應該成功（不同員工）
        
        # Verify
        locks = db_session_commit.query(BookingLockORM).all()
        assert len(locks) == 2
    
    def test_different_merchant_same_staff_same_time_allowed(self, db_session_commit):
        """✅ 測試案例：不同商家的同一員工 ID 可重疊（租戶隔離）"""
        # Arrange
        from uuid import uuid4
        
        lock1 = BookingLockORM(
            merchant_id=str(uuid4()),
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),
        )
        
        lock2 = BookingLockORM(
            merchant_id=str(uuid4()),  # 不同商家
            staff_id=1,  # 同一員工 ID
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),
        )
        
        # Act & Assert
        db_session_commit.add(lock1)
        db_session_commit.commit()
        
        db_session_commit.add(lock2)
        db_session_commit.commit()  # 應該成功（租戶隔離）
        
        # Verify
        locks = db_session_commit.query(BookingLockORM).all()
        assert len(locks) == 2
    
    def test_adjacent_locks_boundary(self, db_session_commit, test_merchant_id):
        """✅ 測試案例：邊界測試 - end_at = next.start_at"""
        # Arrange
        lock1 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),
        )
        
        lock2 = BookingLockORM(
            merchant_id=test_merchant_id,
            staff_id=1,
            start_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),  # 正好接續
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ),
        )
        
        # Act & Assert
        db_session_commit.add(lock1)
        db_session_commit.commit()
        
        db_session_commit.add(lock2)
        db_session_commit.commit()  # 應該成功（tstzrange 不包含上界）
        
        # Verify
        locks = db_session_commit.query(BookingLockORM).all()
        assert len(locks) == 2

