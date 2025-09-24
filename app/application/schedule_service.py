import uuid
from datetime import date, datetime
from app.domain.scheduling.models import BusinessHour, TimeOff
from app.domain.scheduling.repository import AbstractBusinessHourRepository, AbstractTimeOffRepository


class ScheduleService:
    def __init__(
        self,
        business_hour_repo: AbstractBusinessHourRepository,
        time_off_repo: AbstractTimeOffRepository,
    ):
        self.business_hour_repo = business_hour_repo
        self.time_off_repo = time_off_repo

    # ... (BusinessHour methods remain the same)

    def get_all_business_hours(self) -> list[BusinessHour]:
        all_hours = []
        for i in range(7):
            hours = self.business_hour_repo.get_by_day(i)
            if hours:
                all_hours.append(hours)
        return all_hours

    def set_business_hours(self, hours: list[BusinessHour]) -> list[BusinessHour]:
        self.business_hour_repo.delete_all()
        for hour in hours:
            self.business_hour_repo.add(hour)
        # Return the hours that were passed in, as they have been added.
        return hours

    # --- TimeOff Methods ---

    def get_time_offs_by_date(self, for_date: date) -> list[TimeOff]:
        return self.time_off_repo.list_by_date(for_date)

    def get_all_time_offs(self) -> list[TimeOff]:
        return self.time_off_repo.list_all()

    def add_time_off(self, start_datetime: datetime, end_datetime: datetime, reason: str | None) -> TimeOff:
        time_off = TimeOff(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=reason,
        )
        self.time_off_repo.add(time_off)
        return time_off

    def delete_time_off(self, time_off_id: uuid.UUID) -> bool:
        time_off = self.time_off_repo.get_by_id(time_off_id)
        if time_off:
            self.time_off_repo.delete(time_off_id)
            return True
        return False
