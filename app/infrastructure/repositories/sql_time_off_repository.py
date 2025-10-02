from typing import List
import uuid
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date

from app.domain.scheduling.models import TimeOff as DomainTimeOff
from app.domain.scheduling.repository import AbstractTimeOffRepository
from app.infrastructure.database.models import TimeOff as OrmTimeOff


class SqlTimeOffRepository(AbstractTimeOffRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_by_date(self, for_date: date, merchant_id: uuid.UUID = None) -> List[DomainTimeOff]:
        """
        Lists all time off periods that overlap with the given date.
        """
        start_of_day = datetime.combine(for_date, time.min)
        end_of_day = datetime.combine(for_date, time.max)

        query = self.session.query(OrmTimeOff).filter(
            OrmTimeOff.start_datetime < end_of_day,
            OrmTimeOff.end_datetime > start_of_day
        )
        
        # 如果提供了商家ID，按商家過濾
        if merchant_id:
            query = query.filter(OrmTimeOff.merchant_id == merchant_id)
        
        orm_time_offs = query.all()
        return [DomainTimeOff.model_validate(orm_to) for orm_to in orm_time_offs]

    def list_all(self, merchant_id: uuid.UUID = None) -> List[DomainTimeOff]:
        """
        Lists all time off periods.
        """
        query = self.session.query(OrmTimeOff).order_by(OrmTimeOff.start_datetime)
        
        # 如果提供了商家ID，按商家過濾
        if merchant_id:
            query = query.filter(OrmTimeOff.merchant_id == merchant_id)
        
        orm_time_offs = query.all()
        return [DomainTimeOff.model_validate(orm_to) for orm_to in orm_time_offs]

    def add(self, time_off: DomainTimeOff) -> None:
        orm_time_off = OrmTimeOff(**time_off.model_dump())
        self.session.add(orm_time_off)
        self.session.commit()

    def get_by_id(self, time_off_id: uuid.UUID) -> DomainTimeOff | None:
        orm_time_off = self.session.query(OrmTimeOff).filter(OrmTimeOff.id == time_off_id).first()
        if orm_time_off:
            return DomainTimeOff.model_validate(orm_time_off)
        return None

    def delete(self, time_off_id: uuid.UUID) -> None:
        orm_time_off = self.session.query(OrmTimeOff).filter(OrmTimeOff.id == time_off_id).first()
        if orm_time_off:
            self.session.delete(orm_time_off)
            self.session.commit()
