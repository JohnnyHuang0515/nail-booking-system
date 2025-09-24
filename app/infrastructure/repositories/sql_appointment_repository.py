import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.domain.booking.models import Appointment as DomainAppointment
from app.domain.booking.repository import AbstractAppointmentRepository
from app.infrastructure.database.models import Appointment as OrmAppointment
from sqlalchemy.orm import joinedload


class SqlAppointmentRepository(AbstractAppointmentRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, appointment: DomainAppointment) -> None:
        # 只包含必要的字段，排除關聯資料
        appointment_data = appointment.model_dump(exclude={'user', 'service'})
        orm_appointment = OrmAppointment(**appointment_data)
        self.session.add(orm_appointment)
        self.session.commit()

    def get_by_id(self, appointment_id: uuid.UUID) -> DomainAppointment | None:
        orm_appointment = self.session.query(OrmAppointment).filter(OrmAppointment.id == appointment_id).first()
        if orm_appointment:
            return DomainAppointment.model_validate(orm_appointment)
        return None

    def list_by_date(self, appointment_date: date) -> list[DomainAppointment]:
        orm_appointments = self.session.query(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).filter(OrmAppointment.appointment_date == appointment_date).all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def list_by_date_range(self, start_date: date, end_date: date) -> list[DomainAppointment]:
        orm_appointments = self.session.query(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).filter(
            OrmAppointment.appointment_date >= start_date,
            OrmAppointment.appointment_date <= end_date
        ).all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def update(self, appointment: DomainAppointment) -> None:
        orm_appointment = self.session.query(OrmAppointment).filter(OrmAppointment.id == appointment.id).first()
        if orm_appointment:
            update_data = appointment.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(orm_appointment, key, value)
            self.session.add(orm_appointment)
            self.session.commit()

    def delete(self, appointment_id: uuid.UUID) -> None:
        orm_appointment = self.session.query(OrmAppointment).filter(OrmAppointment.id == appointment_id).first()
        if orm_appointment:
            self.session.delete(orm_appointment)
            self.session.commit()
