from sqlalchemy.orm import Session

from app.domain.scheduling.models import BusinessHour as DomainBusinessHour
from app.domain.scheduling.repository import AbstractBusinessHourRepository
from app.infrastructure.database.models import BusinessHour as OrmBusinessHour


class SqlBusinessHourRepository(AbstractBusinessHourRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_day(self, day_of_week: int) -> DomainBusinessHour | None:
        orm_business_hour = self.session.query(OrmBusinessHour).filter(OrmBusinessHour.day_of_week == day_of_week).first()
        if orm_business_hour:
            return DomainBusinessHour.model_validate(orm_business_hour)
        return None

    def add(self, business_hour: DomainBusinessHour) -> None:
        orm_business_hour = OrmBusinessHour(**business_hour.model_dump())
        self.session.add(orm_business_hour)
        self.session.commit()

    def delete_all(self) -> None:
        self.session.query(OrmBusinessHour).delete()
