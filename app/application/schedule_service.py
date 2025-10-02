from typing import List
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

    def get_all_business_hours(self, merchant_id: uuid.UUID = None) -> List[BusinessHour]:
        all_hours = []
        for i in range(7):
            hours = self.business_hour_repo.get_by_day(i, merchant_id)
            if hours:
                all_hours.append(hours)
        return all_hours

    def set_business_hours(self, hours: list[BusinessHour]) -> List[BusinessHour]:
        if hours:
            # 只刪除該商家的營業時間
            merchant_id = hours[0].merchant_id
            self.business_hour_repo.delete_by_merchant(merchant_id)
            for hour in hours:
                self.business_hour_repo.add(hour)
        # Return the hours that were passed in, as they have been added.
        return hours

    # --- TimeOff Methods ---

    def get_time_offs_by_date(self, for_date: date, merchant_id: uuid.UUID = None) -> List[TimeOff]:
        return self.time_off_repo.list_by_date(for_date, merchant_id)

    def get_all_time_offs(self, merchant_id: uuid.UUID = None) -> List[TimeOff]:
        return self.time_off_repo.list_all(merchant_id)

    def add_time_off(self, merchant_id: uuid.UUID, start_datetime: datetime, end_datetime: datetime, reason: str | None, branch_id: uuid.UUID | None = None, staff_id: uuid.UUID | None = None) -> TimeOff:
        time_off = TimeOff(
            merchant_id=merchant_id,
            branch_id=branch_id,
            staff_id=staff_id,
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
