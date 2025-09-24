import uuid
from datetime import date, time
from app.domain.booking.models import Appointment, AppointmentStatus
from app.domain.booking.repository import AbstractAppointmentRepository


class AppointmentService:
    def __init__(self, appointment_repo: AbstractAppointmentRepository):
        self.appointment_repo = appointment_repo

    def get_appointments_by_date_range(self, start_date: date, end_date: date) -> list[Appointment]:
        # This requires a new repository method.
        return self.appointment_repo.list_by_date_range(start_date, end_date)

    def create_appointment(
        self, user_id: uuid.UUID, service_id: uuid.UUID, appointment_date: date, appointment_time: time
    ) -> Appointment:
        appointment = Appointment(
            user_id=user_id,
            service_id=service_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )
        self.appointment_repo.add(appointment)
        return appointment

    def update_appointment(
        self, 
        appointment_id: uuid.UUID, 
        user_id: uuid.UUID, 
        service_id: uuid.UUID, 
        appointment_date: date, 
        appointment_time: time, 
        status: AppointmentStatus
    ) -> Appointment | None:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            return None

        # 更新所有欄位
        appointment.user_id = user_id
        appointment.service_id = service_id
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.status = status
        
        self.appointment_repo.update(appointment)
        return appointment

    def update_appointment_status(self, appointment_id: uuid.UUID, status: AppointmentStatus) -> Appointment | None:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            return None

        if status == AppointmentStatus.CANCELLED:
            appointment.cancel()
        elif status == AppointmentStatus.COMPLETED:
            appointment.complete()
        else:
            appointment.status = status
        
        self.appointment_repo.update(appointment)
        return appointment

    def delete_appointment(self, appointment_id: uuid.UUID) -> bool:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if appointment:
            self.appointment_repo.delete(appointment_id)
            return True
        return False
