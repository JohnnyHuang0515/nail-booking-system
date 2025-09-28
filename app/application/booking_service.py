from typing import List
from datetime import date, time, datetime, timezone

from app.domain.booking.repository import AbstractAppointmentRepository
from app.domain.scheduling.repository import AbstractBusinessHourRepository, AbstractTimeOffRepository

# Predefined, fixed appointment slots
AVAILABLE_TIMES = [time(12, 0), time(15, 0), time(18, 0)]


class BookingService:
    def __init__(
        self,
        appointment_repo: AbstractAppointmentRepository,
        business_hour_repo: AbstractBusinessHourRepository,
        time_off_repo: AbstractTimeOffRepository,
    ):
        self.appointment_repo = appointment_repo
        self.business_hour_repo = business_hour_repo
        self.time_off_repo = time_off_repo

    def get_available_slots(self, for_date: date) -> List[time]:
        """
        Calculates available appointment slots for a given date by checking
        business hours, existing appointments, and time-off periods.
        """
        # 1. Filter by business hours
        day_of_week = for_date.weekday()  # Monday is 0 and Sunday is 6
        business_hours = self.business_hour_repo.get_by_day(day_of_week)
        if not business_hours:
            return []  # Shop is closed on this day

        slots = [
            t for t in AVAILABLE_TIMES
            if business_hours.start_time <= t < business_hours.end_time
        ]

        # 2. Filter by booked appointments
        booked_appointments = self.appointment_repo.list_by_date(for_date)
        booked_times = {apt.appointment_time for apt in booked_appointments}
        slots = [t for t in slots if t not in booked_times]

        # 3. Filter by time-offs
        time_offs = self.time_off_repo.list_by_date(for_date)
        if not time_offs:
            return slots

        final_slots = []
        for slot in slots:
            # 創建 timezone-aware 的 datetime 進行比較
            slot_datetime = datetime.combine(for_date, slot).replace(tzinfo=timezone.utc)
            is_blocked = any(
                to.start_datetime <= slot_datetime < to.end_datetime
                for to in time_offs
            )
            if not is_blocked:
                final_slots.append(slot)

        return final_slots
