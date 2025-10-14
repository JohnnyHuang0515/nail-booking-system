"""
Booking Context - Domain Layer - Exceptions
Booking 領域特定異常
"""
from datetime import datetime
from shared.exceptions import DomainException


class BookingOverlapError(DomainException):
    """預約時段重疊異常"""
    
    def __init__(
        self,
        staff_id: int,
        start_at: datetime,
        end_at: datetime,
        conflicting_booking_id: str | None = None
    ):
        super().__init__(
            message=f"時段衝突：員工 {staff_id} 在 {start_at} - {end_at} 已有預約",
            error_code="booking_overlap",
            details={
                "staff_id": staff_id,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "conflicting_booking_id": conflicting_booking_id
            }
        )


class StaffInactiveError(DomainException):
    """員工停用異常"""
    
    def __init__(self, staff_id: int):
        super().__init__(
            message=f"員工 {staff_id} 已停用，無法接受預約",
            error_code="staff_inactive",
            details={"staff_id": staff_id}
        )


class ServiceInactiveError(DomainException):
    """服務停用異常"""
    
    def __init__(self, service_id: int):
        super().__init__(
            message=f"服務 {service_id} 已停用或不存在",
            error_code="service_inactive",
            details={"service_id": service_id}
        )


class OutsideWorkingHoursError(DomainException):
    """超出工作時間異常"""
    
    def __init__(self, staff_id: int, requested_time: datetime):
        super().__init__(
            message=f"員工 {staff_id} 在 {requested_time} 不在工作時間",
            error_code="outside_working_hours",
            details={
                "staff_id": staff_id,
                "requested_time": requested_time.isoformat()
            }
        )


class InvalidTimeSlotError(DomainException):
    """無效時段異常"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"無效的預約時段: {reason}",
            error_code="invalid_time_slot"
        )


class BookingAlreadyCancelledError(DomainException):
    """預約已取消異常"""
    
    def __init__(self, booking_id: str):
        super().__init__(
            message=f"預約 {booking_id} 已被取消",
            error_code="booking_already_cancelled",
            details={"booking_id": booking_id}
        )


class BookingAlreadyCompletedError(DomainException):
    """預約已完成異常"""
    
    def __init__(self, booking_id: str):
        super().__init__(
            message=f"預約 {booking_id} 已完成，無法修改",
            error_code="booking_already_completed",
            details={"booking_id": booking_id}
        )

