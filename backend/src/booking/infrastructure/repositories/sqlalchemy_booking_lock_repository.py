"""
Booking Context - Infrastructure Layer - BookingLock Repository
"""
from datetime import datetime
from typing import Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, text
from psycopg2.errors import ExclusionViolation

from booking.domain.models import BookingLock
from booking.domain.repositories import BookingLockRepository
from booking.domain.exceptions import BookingOverlapError
from booking.infrastructure.orm.models import BookingLockORM

logger = logging.getLogger(__name__)


class SQLAlchemyBookingLockRepository(BookingLockRepository):
    """SQLAlchemy 實作的 BookingLock Repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_lock(self, lock: BookingLock) -> BookingLock:
        """
        建立預約鎖定
        
        如果違反 EXCLUDE 約束，會拋出 psycopg2.errors.ExclusionViolation
        Application Service 需捕捉並轉換為 BookingOverlapError
        """
        orm_lock = self._domain_to_orm(lock)
        
        try:
            self.session.add(orm_lock)
            self.session.flush()  # 立即執行以觸發約束檢查
            logger.info(f"Created booking lock: {lock.id}")
            return self._orm_to_domain(orm_lock)
        except Exception as e:
            # 檢查是否為 EXCLUDE 約束違反
            if isinstance(e.__cause__, ExclusionViolation):
                logger.warning(f"Booking overlap detected: {lock.staff_id} @ {lock.start_at}")
                raise BookingOverlapError(
                    staff_id=lock.staff_id,
                    start_at=lock.start_at,
                    end_at=lock.end_at
                )
            raise
    
    def find_overlapping_locks(
        self,
        merchant_id: str,
        staff_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[BookingLock]:
        """
        查詢重疊的鎖定
        
        使用 PostgreSQL tstzrange 進行高效重疊檢測
        """
        # 使用 PostgreSQL 的 tstzrange 重疊檢測
        stmt = select(BookingLockORM).where(
            and_(
                BookingLockORM.merchant_id == merchant_id,
                BookingLockORM.staff_id == staff_id,
                # 重疊條件：NOT (a.end <= b.start OR b.end <= a.start)
                BookingLockORM.start_at < end_at,
                BookingLockORM.end_at > start_at
            )
        )
        
        orm_locks = self.session.scalars(stmt).all()
        return [self._orm_to_domain(orm) for orm in orm_locks]
    
    def link_to_booking(self, lock_id: str, booking_id: str) -> bool:
        """將鎖定關聯到預約"""
        orm_lock = self.session.get(BookingLockORM, lock_id)
        
        if not orm_lock:
            return False
        
        orm_lock.booking_id = booking_id
        self.session.flush()
        logger.info(f"Linked lock {lock_id} to booking {booking_id}")
        return True
    
    def delete_lock(self, lock_id: str) -> bool:
        """刪除鎖定"""
        orm_lock = self.session.get(BookingLockORM, lock_id)
        
        if not orm_lock:
            return False
        
        self.session.delete(orm_lock)
        self.session.flush()
        return True
    
    # === ORM ↔ Domain 轉換 ===
    
    def _orm_to_domain(self, orm: BookingLockORM) -> BookingLock:
        """ORM → Domain"""
        return BookingLock(
            id=orm.id,
            merchant_id=orm.merchant_id,
            staff_id=orm.staff_id,
            start_at=orm.start_at,
            end_at=orm.end_at,
            booking_id=orm.booking_id,
            created_at=orm.created_at
        )
    
    def _domain_to_orm(self, domain: BookingLock) -> BookingLockORM:
        """Domain → ORM"""
        return BookingLockORM(
            id=domain.id,
            merchant_id=domain.merchant_id,
            staff_id=domain.staff_id,
            start_at=domain.start_at,
            end_at=domain.end_at,
            booking_id=domain.booking_id,
            created_at=domain.created_at
        )

