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
def get_business_hours(service: ScheduleService = Depends(get_schedule_service)):
    """Get the weekly business hours."""
    try:
        return service.get_all_business_hours()
    except Exception as e:
        print(f"Business hours error: {e}")
        return []


@router.post("/schedule/business_hours", response_model=list[BusinessHour])
def set_business_hours(
    hours: list[BusinessHourIn],
    service: ScheduleService = Depends(get_schedule_service)
):
    """
    Set the weekly business hours.
    This will replace all existing business hours.
    """
    business_hours = [BusinessHour.model_validate(h.model_dump()) for h in hours]
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
    return service.add_time_off(**time_off_data.model_dump())


@router.delete("/schedule/time_off/{time_off_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_off(
    time_off_id: uuid.UUID,
    service: ScheduleService = Depends(get_schedule_service)
):
    """Delete a time off period."""
    if not service.delete_time_off(time_off_id):
        raise HTTPException(status_code=404, detail="Time off not found")
    return None
