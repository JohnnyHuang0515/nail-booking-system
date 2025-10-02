import uuid
from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.application.appointment_service import AppointmentService
from app.domain.booking.models import Appointment, AppointmentStatus
from app.api.v1.dependencies import get_appointment_service

router = APIRouter()


class AppointmentCreate(BaseModel):
    user_id: uuid.UUID
    service_id: uuid.UUID
    appointment_date: date
    appointment_time: time


class AppointmentUpdate(BaseModel):
    user_id: uuid.UUID
    service_id: uuid.UUID
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus


@router.get("/appointments")
def list_appointments(
    merchant_id: str,
    start_date: date = Query(..., description="Start date for filtering appointments"),
    end_date: date = Query(..., description="End date for filtering appointments"),
    service: AppointmentService = Depends(get_appointment_service),
):
    """Get a list of appointments within a date range."""
    try:
        import uuid
        merchant_uuid = uuid.UUID(merchant_id)
        return service.get_appointments_by_date_range(start_date, end_date, merchant_uuid)
    except Exception as e:
        print(f"Appointments error: {e}")
        return []


@router.post("/appointments", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Create a new appointment manually (for admin)."""
    return service.create_appointment(**appointment_data.model_dump())


@router.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(
    appointment_id: uuid.UUID,
    update_data: AppointmentUpdate,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Update an appointment."""
    updated_appointment = service.update_appointment(appointment_id, **update_data.model_dump())
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment


@router.put("/appointments/{appointment_id}/status", response_model=Appointment)
def update_appointment_status(
    appointment_id: uuid.UUID,
    update_data: AppointmentUpdate,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Update the status of an appointment."""
    updated_appointment = service.update_appointment_status(appointment_id, update_data.status)
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: uuid.UUID,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Delete an appointment."""
    if not service.delete_appointment(appointment_id):
        raise HTTPException(status_code=404, detail="Appointment not found")
    return None
