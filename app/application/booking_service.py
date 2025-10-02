from typing import List
import uuid
from datetime import date, time, datetime, timezone

from app.domain.booking.repository import AbstractAppointmentRepository
from app.domain.scheduling.repository import AbstractBusinessHourRepository, AbstractTimeOffRepository

# Predefined, fixed appointment slots
AVAILABLE_TIMES = [time(12, 0), time(15, 0), time(18, 0)]

# 固定時段，不受營業時間限制
FIXED_TIME_SLOTS = [time(12, 0), time(15, 0), time(18, 0)]


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

    def get_available_slots(self, for_date: date, merchant_id: uuid.UUID) -> List[time]:
        """
        Calculates available appointment slots for a given date by checking
        business hours, existing appointments, and time-off periods.
        """
        # 1. 檢查是否有營業（只檢查是否存在營業時間設定）
        day_of_week = for_date.weekday()  # Monday is 0 and Sunday is 6
        business_hours = self.business_hour_repo.find_by_merchant_and_day(merchant_id, day_of_week)
        if not business_hours:
            return []  # Shop is closed on this day

        # 2. 使用固定的時段
        slots = FIXED_TIME_SLOTS.copy()

        # 3. Filter by booked appointments (按商家過濾)
        booked_appointments = self.appointment_repo.list_by_merchant_and_date(merchant_id, for_date)
        booked_times = {apt.appointment_time for apt in booked_appointments}
        slots = [t for t in slots if t not in booked_times]

        # 4. Filter by time-offs (按商家過濾)
        time_offs = self.time_off_repo.list_by_date(for_date, merchant_id)
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

    def get_all_slots_with_booking_status(self, for_date: date, merchant_id: uuid.UUID) -> List[dict]:
        """
        返回指定日期的所有時段及其預約狀態
        """
        
        # 1. 檢查是否有營業（只檢查是否存在營業時間設定，不檢查具體時間）
        day_of_week = for_date.weekday()
        business_hours = self.business_hour_repo.find_by_merchant_and_day(merchant_id, day_of_week)
        if not business_hours:
            return []  # 當日不營業

        # 2. 使用固定的時段（12:00, 15:00, 18:00）
        all_possible_slots = FIXED_TIME_SLOTS

        # 3. 獲取已預約的時段（按商家過濾）
        booked_appointments = self.appointment_repo.list_by_merchant_and_date(merchant_id, for_date)
        booked_times = {apt.appointment_time: apt.customer_name for apt in booked_appointments}

        # 4. 獲取休假時段（按商家過濾）
        time_offs = self.time_off_repo.list_by_date(for_date, merchant_id)
        
        result = []
        for slot in all_possible_slots:
            slot_datetime = datetime.combine(for_date, slot).replace(tzinfo=timezone.utc)
            
            # 檢查是否在休假時段內
            is_time_off = any(
                to.start_datetime <= slot_datetime < to.end_datetime
                for to in time_offs
            )
            
            if is_time_off:
                # 休假時段
                result.append({
                    "time": slot.strftime("%H:%M"),
                    "available": False,
                    "bookedBy": "休假時間"
                })
            elif slot in booked_times:
                # 已預約時段
                result.append({
                    "time": slot.strftime("%H:%M"),
                    "available": False,
                    "bookedBy": booked_times[slot]
                })
            else:
                # 可用時段
                result.append({
                    "time": slot.strftime("%H:%M"),
                    "available": True,
                    "bookedBy": None
                })
        
        return result
