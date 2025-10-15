"""
Catalog Context - Infrastructure Layer - Staff Repository
"""
from typing import Optional
from datetime import time, date
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
    
    def clear_working_hours(self, staff_id: int) -> None:
        """清除員工的所有工時設定"""
        stmt = select(StaffWorkingHoursORM).where(
            StaffWorkingHoursORM.staff_id == staff_id
        )
        
        orm_hours = self.session.scalars(stmt).all()
        for orm_hour in orm_hours:
            self.session.delete(orm_hour)
        
        self.session.flush()
    
    def add_working_hours(self, staff_id: int, day_of_week: int, start_time: str, end_time: str) -> None:
        """新增員工工時"""
        from datetime import time, date
        
        orm_hour = StaffWorkingHoursORM(
            staff_id=staff_id,
            day_of_week=day_of_week,
            start_time=time.fromisoformat(start_time),
            end_time=time.fromisoformat(end_time)
        )
        
        self.session.add(orm_hour)
        self.session.flush()
    
    # ========== Staff Holiday Management ==========
    
    def save_staff_holiday(self, holiday: 'StaffHoliday') -> 'StaffHoliday':
        """儲存美甲師休假"""
        from catalog.domain.models import StaffHoliday
        from catalog.infrastructure.orm.models import StaffHolidayORM
        
        existing = self.session.get(StaffHolidayORM, holiday.id) if holiday.id else None
        
        if existing:
            self._update_holiday_orm_from_domain(existing, holiday)
        else:
            orm_holiday = self._holiday_domain_to_orm(holiday)
            self.session.add(orm_holiday)
            self.session.flush()
            holiday.id = orm_holiday.id
        
        # 載入美甲師名稱
        staff = self.session.get(StaffORM, holiday.staff_id)
        if staff:
            holiday.staff_name = staff.name
        
        return holiday
    
    def find_staff_holidays(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        staff_id: Optional[int] = None
    ) -> list['StaffHoliday']:
        """查詢美甲師休假"""
        from catalog.domain.models import StaffHoliday
        from catalog.infrastructure.orm.models import StaffHolidayORM
        
        stmt = select(StaffHolidayORM).options(
            joinedload(StaffHolidayORM.staff)
        ).where(StaffHolidayORM.merchant_id == merchant_id)
        
        if start_date:
            stmt = stmt.where(StaffHolidayORM.holiday_date >= start_date)
        if end_date:
            stmt = stmt.where(StaffHolidayORM.holiday_date <= end_date)
        if staff_id:
            stmt = stmt.where(StaffHolidayORM.staff_id == staff_id)
        
        stmt = stmt.order_by(StaffHolidayORM.holiday_date)
        
        orm_holidays = self.session.scalars(stmt).all()
        holidays = []
        
        for orm_holiday in orm_holidays:
            holiday = self._holiday_orm_to_domain(orm_holiday)
            holidays.append(holiday)
        
        return holidays
    
    def find_staff_holiday_by_id(self, holiday_id: int, merchant_id: str) -> Optional['StaffHoliday']:
        """根據 ID 查詢美甲師休假"""
        from catalog.domain.models import StaffHoliday
        from catalog.infrastructure.orm.models import StaffHolidayORM
        
        stmt = select(StaffHolidayORM).options(
            joinedload(StaffHolidayORM.staff)
        ).where(
            and_(
                StaffHolidayORM.id == holiday_id,
                StaffHolidayORM.merchant_id == merchant_id
            )
        )
        
        orm_holiday = self.session.scalar(stmt)
        
        if not orm_holiday:
            return None
        
        return self._holiday_orm_to_domain(orm_holiday)
    
    def delete_staff_holiday(self, holiday_id: int, merchant_id: str) -> bool:
        """刪除美甲師休假"""
        from catalog.infrastructure.orm.models import StaffHolidayORM
        
        stmt = select(StaffHolidayORM).where(
            and_(
                StaffHolidayORM.id == holiday_id,
                StaffHolidayORM.merchant_id == merchant_id
            )
        )
        
        orm_holiday = self.session.scalar(stmt)
        
        if not orm_holiday:
            return False
        
        self.session.delete(orm_holiday)
        self.session.flush()
        return True
    
    # === Holiday ORM ↔ Domain 轉換 ===
    
    def _holiday_orm_to_domain(self, orm: 'StaffHolidayORM') -> 'StaffHoliday':
        """休假 ORM → Domain"""
        from catalog.domain.models import StaffHoliday
        
        holiday = StaffHoliday(
            id=orm.id,
            staff_id=orm.staff_id,
            merchant_id=orm.merchant_id,
            holiday_date=orm.holiday_date,
            name=orm.name,
            is_recurring=orm.is_recurring
        )
        
        # 設定美甲師名稱
        if orm.staff:
            holiday.staff_name = orm.staff.name
        
        return holiday
    
    def _holiday_domain_to_orm(self, domain: 'StaffHoliday') -> 'StaffHolidayORM':
        """休假 Domain → ORM"""
        from catalog.infrastructure.orm.models import StaffHolidayORM
        
        return StaffHolidayORM(
            id=domain.id,
            staff_id=domain.staff_id,
            merchant_id=domain.merchant_id,
            holiday_date=domain.holiday_date,
            name=domain.name,
            is_recurring=domain.is_recurring
        )
    
    def _update_holiday_orm_from_domain(self, orm: 'StaffHolidayORM', domain: 'StaffHoliday'):
        """更新休假 ORM"""
        orm.holiday_date = domain.holiday_date
        orm.name = domain.name
        orm.is_recurring = domain.is_recurring
    
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

