from datetime import date, time

from fastapi import APIRouter, Depends

from app.application.booking_service import BookingService
from app.api.v1.dependencies import get_booking_service

router = APIRouter()


@router.get("/slots/{for_date}")
def get_available_slots(for_date: date, service: BookingService = Depends(get_booking_service)):
    """
    Endpoint to get available appointment slots for a given date.
    """
    try:
        slots = service.get_available_slots(for_date)
        # 轉換為前端期望的格式
        return [
            {
                "time": slot.strftime("%H:%M"),
                "available": True
            }
            for slot in slots
        ]
    except Exception as e:
        print(f"Booking slots error: {e}")
        return []
