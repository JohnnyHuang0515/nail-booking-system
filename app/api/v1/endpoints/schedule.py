import uuid
from datetime import time, date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.application.schedule_service import ScheduleService
from app.domain.scheduling.models import BusinessHour, TimeOff
from app.api.v1.dependencies import get_schedule_service

router = APIRouter()


# --- Business Hours Models and Endpoints ---

class BusinessHourIn(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time


@router.get("/schedule/business_hours")
def get_business_hours(
    merchant_id: str,
    service: ScheduleService = Depends(get_schedule_service)
):
    """Get the weekly business hours."""
    try:
        import uuid
        merchant_uuid = uuid.UUID(merchant_id)
        return service.get_all_business_hours(merchant_uuid)
    except Exception as e:
        print(f"Business hours error: {e}")
        return []


@router.post("/schedule/business_hours", response_model=list[BusinessHour])
def set_business_hours(
    hours: list[BusinessHourIn],
    merchant_id: str,
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Set the weekly business hours.
    This will replace all existing business hours.
    """
    merchant_uuid = uuid.UUID(merchant_id)
    business_hours = []
    for h in hours:
        business_hour = BusinessHour(
            merchant_id=merchant_uuid,
            day_of_week=h.day_of_week,
            start_time=h.start_time,
            end_time=h.end_time
        )
        business_hours.append(business_hour)
    return service.set_business_hours(business_hours)


# --- Time Off Models and Endpoints ---

class TimeOffIn(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = None


@router.get("/schedule/time_off")
def get_time_off_for_date(
    for_date: date,
    service: ScheduleService = Depends(get_schedule_service)
):
    """Get all time off periods for a specific date."""
    try:
        return service.get_time_offs_by_date(for_date)
    except Exception as e:
        print(f"Time off error: {e}")
        return []


@router.get("/schedule/time_off/all")
def get_all_time_offs(service: ScheduleService = Depends(get_schedule_service)):
    """Get all time off periods."""
    try:
        return service.get_all_time_offs()
    except Exception as e:
        print(f"All time off error: {e}")
        return []


@router.post("/schedule/time_off", response_model=TimeOff, status_code=status.HTTP_201_CREATED)
def add_time_off(
    time_off_data: TimeOffIn,
    service: ScheduleService = Depends(get_schedule_service)
):
    """Add a new time off period."""
    # 使用正確的測試商家 ID
    merchant_id = uuid.UUID("c9a8982e-5f17-459b-a83e-690057e4da71")
    return service.add_time_off(merchant_id=merchant_id, **time_off_data.model_dump())


@router.delete("/schedule/time_off/{time_off_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_off(
    time_off_id: uuid.UUID,
    service: ScheduleService = Depends(get_schedule_service)
):
    """Delete a time off period."""
    if not service.delete_time_off(time_off_id):
        raise HTTPException(status_code=404, detail="Time off not found")
    return None
