"""
Holiday Repository - SQLAlchemy Implementation
"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from catalog.domain.holiday import Holiday
from catalog.infrastructure.orm.models import HolidayORM


class SQLAlchemyHolidayRepository:
    """休假日 Repository - SQLAlchemy 實作"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, holiday: Holiday) -> Holiday:
        """儲存休假日"""
        if holiday.id:
            # 更新
            orm = self.db.query(HolidayORM).filter_by(id=holiday.id).first()
            if orm:
                orm.merchant_id = holiday.merchant_id
                orm.holiday_date = holiday.holiday_date
                orm.name = holiday.name
                orm.is_recurring = holiday.is_recurring
            else:
                raise ValueError(f"Holiday not found: {holiday.id}")
        else:
            # 新增
            orm = HolidayORM(
                merchant_id=holiday.merchant_id,
                holiday_date=holiday.holiday_date,
                name=holiday.name,
                is_recurring=holiday.is_recurring
            )
            self.db.add(orm)
        
        self.db.flush()
        return self._to_domain(orm)
    
    def find_by_id(self, holiday_id: int, merchant_id: str) -> Optional[Holiday]:
        """根據 ID 查詢休假日"""
        orm = self.db.query(HolidayORM).filter_by(
            id=holiday_id,
            merchant_id=merchant_id
        ).first()
        
        if orm:
            return self._to_domain(orm)
        return None
    
    def find_by_merchant(self, merchant_id: str) -> list[Holiday]:
        """查詢商家的所有休假日"""
        orms = self.db.query(HolidayORM).filter_by(
            merchant_id=merchant_id
        ).order_by(HolidayORM.holiday_date).all()
        
        return [self._to_domain(orm) for orm in orms]
    
    def find_by_date_range(
        self,
        merchant_id: str,
        start_date: date,
        end_date: date
    ) -> list[Holiday]:
        """查詢日期範圍內的休假日"""
        orms = self.db.query(HolidayORM).filter(
            HolidayORM.merchant_id == merchant_id,
            HolidayORM.holiday_date >= start_date,
            HolidayORM.holiday_date <= end_date
        ).order_by(HolidayORM.holiday_date).all()
        
        return [self._to_domain(orm) for orm in orms]
    
    def delete(self, holiday_id: int, merchant_id: str) -> bool:
        """刪除休假日"""
        result = self.db.query(HolidayORM).filter_by(
            id=holiday_id,
            merchant_id=merchant_id
        ).delete()
        
        return result > 0
    
    def _to_domain(self, orm: HolidayORM) -> Holiday:
        """ORM 轉 Domain"""
        return Holiday(
            id=orm.id,
            merchant_id=orm.merchant_id,
            holiday_date=orm.holiday_date,
            name=orm.name,
            is_recurring=orm.is_recurring
        )

