from typing import List
import uuid
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.booking.models import Appointment as DomainAppointment, AppointmentStatus
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
        stmt = select(OrmAppointment).where(OrmAppointment.id == appointment_id)
        orm_appointment = self.session.execute(stmt).scalar_one_or_none()
        if orm_appointment:
            return DomainAppointment.model_validate(orm_appointment)
        return None

    def find_by_id(self, appointment_id: uuid.UUID) -> OrmAppointment | None:
        """根據ID查找預約（返回ORM對象）"""
        stmt = select(OrmAppointment).where(OrmAppointment.id == appointment_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_date(self, appointment_date: date) -> List[DomainAppointment]:
        stmt = select(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).where(OrmAppointment.appointment_date == appointment_date)
        orm_appointments = self.session.execute(stmt).scalars().all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def list_by_merchant_and_date(self, merchant_id: uuid.UUID, appointment_date: date) -> List[DomainAppointment]:
        """列出指定商家和日期的預約"""
        stmt = select(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).where(
            OrmAppointment.merchant_id == merchant_id,
            OrmAppointment.appointment_date == appointment_date
        )
        orm_appointments = self.session.execute(stmt).scalars().all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def list_by_user_id(self, user_id: uuid.UUID) -> List[DomainAppointment]:
        """列出指定用戶的所有預約"""
        stmt = select(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).where(OrmAppointment.user_id == user_id)
        orm_appointments = self.session.execute(stmt).scalars().all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def list_by_date_range(self, start_date: date, end_date: date) -> List[DomainAppointment]:
        stmt = select(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).where(
            OrmAppointment.appointment_date >= start_date,
            OrmAppointment.appointment_date <= end_date
        )
        orm_appointments = self.session.execute(stmt).scalars().all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def list_by_merchant_and_date_range(self, merchant_id: uuid.UUID, start_date: date, end_date: date) -> List[DomainAppointment]:
        """列出指定商家和日期範圍的預約"""
        stmt = select(OrmAppointment).options(
            joinedload(OrmAppointment.user),
            joinedload(OrmAppointment.service)
        ).where(
            OrmAppointment.merchant_id == merchant_id,
            OrmAppointment.appointment_date >= start_date,
            OrmAppointment.appointment_date <= end_date
        )
        orm_appointments = self.session.execute(stmt).scalars().all()
        return [DomainAppointment.model_validate(orm_apt) for orm_apt in orm_appointments]

    def cancel_appointment(self, appointment_id: uuid.UUID) -> bool:
        """取消預約"""
        stmt = select(OrmAppointment).where(OrmAppointment.id == appointment_id)
        orm_appointment = self.session.execute(stmt).scalar_one_or_none()
        
        if not orm_appointment:
            return False
        
        orm_appointment.status = AppointmentStatus.CANCELLED
        self.session.add(orm_appointment)
        self.session.commit()
        return True

    def update(self, appointment: DomainAppointment) -> None:
        stmt = select(OrmAppointment).where(OrmAppointment.id == appointment.id)
        orm_appointment = self.session.execute(stmt).scalar_one_or_none()
        if orm_appointment:
            update_data = appointment.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(orm_appointment, key, value)
            self.session.add(orm_appointment)
            self.session.commit()

    def delete(self, appointment_id: uuid.UUID) -> None:
        stmt = select(OrmAppointment).where(OrmAppointment.id == appointment_id)
        orm_appointment = self.session.execute(stmt).scalar_one_or_none()
        if orm_appointment:
            self.session.delete(orm_appointment)
            self.session.commit()


# 向後兼容的別名
SQLAppointmentRepository = SqlAppointmentRepository
