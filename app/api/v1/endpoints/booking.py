from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from app.application.booking_service import BookingService
from app.application.appointment_service import AppointmentService
from app.api.v1.dependencies import get_booking_service, get_appointment_service
from app.domain.booking.models import Appointment, AppointmentStatus

router = APIRouter()


class BookingRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    service_id: str
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None
    # LINE 用戶資訊
    line_user_id: Optional[str] = None
    line_display_name: Optional[str] = None
    line_picture_url: Optional[str] = None


class TimeSlot(BaseModel):
    time: str
    available: bool
    bookedBy: Optional[str] = None


@router.get("/slots/{for_date}", response_model=List[TimeSlot])
def get_available_slots(
    for_date: date, 
    merchant_id: str,
    service: BookingService = Depends(get_booking_service)
):
    """
    Endpoint to get all appointment slots for a given date (both available and booked).
    """
    try:
        import uuid
        merchant_uuid = uuid.UUID(merchant_id)
        
        # 獲取所有可能的時段和已預約的時段
        all_slots_data = service.get_all_slots_with_booking_status(for_date, merchant_uuid)
        # 轉換為 TimeSlot 物件
        return [
            TimeSlot(
                time=slot["time"],
                available=slot["available"],
                bookedBy=slot["bookedBy"]
            )
            for slot in all_slots_data
        ]
    except Exception as e:
        print(f"Booking slots error: {e}")
        return []


@router.post("/bookings", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingRequest,
    merchant_id: str,
    appointment_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Endpoint to create a new booking.
    """
    try:
        import uuid
        merchant_uuid = uuid.UUID(merchant_id)
        
        # 創建預約
        appointment = appointment_service.create_appointment(
            customer_name=booking_data.customer_name,
            customer_phone=booking_data.customer_phone,
            customer_email=booking_data.customer_email,
            service_id=booking_data.service_id,
            appointment_date=booking_data.appointment_date,
            appointment_time=booking_data.appointment_time,
            notes=booking_data.notes,
            merchant_id=merchant_uuid
        )
        return appointment
    except Exception as e:
        print(f"Create booking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法創建預約: {str(e)}"
        )
