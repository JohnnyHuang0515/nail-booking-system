"""
Catalog Context - Infrastructure Layer - Staff Repository
"""
from typing import Optional
from datetime import time
import logging

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, or_

from catalog.domain.models import Staff, StaffWorkingHours, DayOfWeek
from catalog.domain.repositories import StaffRepository
from catalog.infrastructure.orm.models import StaffORM, StaffWorkingHoursORM

logger = logging.getLogger(__name__)


class SQLAlchemyStaffRepository(StaffRepository):
    """SQLAlchemy 實作的 Staff Repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, staff: Staff) -> Staff:
        """儲存員工"""
        existing = self.session.get(StaffORM, staff.id)
        
        if existing:
            self._update_orm_from_domain(existing, staff)
            logger.info(f"Updated staff: {staff.id}")
        else:
            orm_staff = self._domain_to_orm(staff)
            self.session.add(orm_staff)
            logger.info(f"Created staff: {staff.id}")
        
        self.session.flush()
        return self.find_by_id(staff.id, staff.merchant_id)
    
    def find_by_id(self, staff_id: int, merchant_id: str) -> Optional[Staff]:
        """根據 ID 查詢員工"""
        stmt = select(StaffORM).options(
            joinedload(StaffORM.working_hours)
        ).where(
            and_(
                StaffORM.id == staff_id,
                StaffORM.merchant_id == merchant_id
            )
        )
        
        orm_staff = self.session.scalar(stmt)
        
        if not orm_staff:
            return None
        
        return self._orm_to_domain(orm_staff)
    
    def find_by_merchant(self, merchant_id: str, is_active_only: bool = True) -> list[Staff]:
        """查詢商家的所有員工"""
        stmt = select(StaffORM).options(
            joinedload(StaffORM.working_hours)
        ).where(
            StaffORM.merchant_id == merchant_id
        )
        
        if is_active_only:
            stmt = stmt.where(StaffORM.is_active == True)
        
        stmt = stmt.order_by(StaffORM.id)
        
        orm_staff_list = self.session.scalars(stmt).unique().all()
        return [self._orm_to_domain(orm) for orm in orm_staff_list]
    
    def find_by_service(self, service_id: int, merchant_id: str) -> list[Staff]:
        """查詢可執行特定服務的員工"""
        # 使用 PostgreSQL ARRAY 查詢
        stmt = select(StaffORM).options(
            joinedload(StaffORM.working_hours)
        ).where(
            and_(
                StaffORM.merchant_id == merchant_id,
                StaffORM.is_active == True,
                StaffORM.skills.contains([service_id])  # ARRAY contains
            )
        )
        
        orm_staff_list = self.session.scalars(stmt).unique().all()
        return [self._orm_to_domain(orm) for orm in orm_staff_list]
    
    def delete(self, staff_id: int, merchant_id: str) -> bool:
        """刪除員工"""
        stmt = select(StaffORM).where(
            and_(
                StaffORM.id == staff_id,
                StaffORM.merchant_id == merchant_id
            )
        )
        
        orm_staff = self.session.scalar(stmt)
        
        if not orm_staff:
            return False
        
        self.session.delete(orm_staff)
        self.session.flush()
        return True
    
    # === ORM ↔ Domain 轉換 ===
    
    def _orm_to_domain(self, orm: StaffORM) -> Staff:
        """ORM → Domain"""
        # 轉換工時
        working_hours = []
        for orm_wh in orm.working_hours:
            wh = StaffWorkingHours(
                day_of_week=DayOfWeek(orm_wh.day_of_week),
                start_time=orm_wh.start_time,
                end_time=orm_wh.end_time
            )
            working_hours.append(wh)
        
        return Staff(
            id=orm.id,
            merchant_id=orm.merchant_id,
            name=orm.name,
            email=orm.email,
            phone=orm.phone,
            skills=orm.skills or [],
            is_active=orm.is_active,
            working_hours=working_hours
        )
    
    def _domain_to_orm(self, domain: Staff) -> StaffORM:
        """Domain → ORM"""
        orm = StaffORM(
            id=domain.id,
            merchant_id=domain.merchant_id,
            name=domain.name,
            email=domain.email,
            phone=domain.phone,
            skills=domain.skills,
            is_active=domain.is_active
        )
        
        # 轉換工時
        for wh in domain.working_hours:
            orm_wh = StaffWorkingHoursORM(
                staff_id=domain.id,
                day_of_week=wh.day_of_week.value,
                start_time=wh.start_time,
                end_time=wh.end_time
            )
            orm.working_hours.append(orm_wh)
        
        return orm
    
    def _update_orm_from_domain(self, orm: StaffORM, domain: Staff):
        """更新 ORM"""
        orm.name = domain.name
        orm.email = domain.email
        orm.phone = domain.phone
        orm.skills = domain.skills
        orm.is_active = domain.is_active
        
        # 更新工時（簡化：刪除後重建）
        orm.working_hours.clear()
        for wh in domain.working_hours:
            orm_wh = StaffWorkingHoursORM(
                staff_id=domain.id,
                day_of_week=wh.day_of_week.value,
                start_time=wh.start_time,
                end_time=wh.end_time
            )
            orm.working_hours.append(orm_wh)

