from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.booking_service import BookingService
from app.application.service_service import ServiceService
from app.application.schedule_service import ScheduleService
from app.application.appointment_service import AppointmentService
from app.application.dashboard_service import DashboardService
from app.application.transaction_service import TransactionService
from app.domain.booking.repository import AbstractAppointmentRepository
from app.domain.booking.service_repository import AbstractServiceRepository
from app.domain.scheduling.repository import AbstractBusinessHourRepository, AbstractTimeOffRepository
from app.domain.transaction.repository import AbstractTransactionRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.sql_appointment_repository import SqlAppointmentRepository
from app.infrastructure.repositories.sql_business_hour_repository import SQLBusinessHourRepository
from app.infrastructure.repositories.sql_time_off_repository import SqlTimeOffRepository
from app.infrastructure.repositories.sql_service_repository import SqlServiceRepository
from app.infrastructure.repositories.sql_transaction_repository import SqlTransactionRepository


def get_db() -> Session:
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_appointment_repo(db: Session = Depends(get_db)) -> AbstractAppointmentRepository:
    """FastAPI dependency to get an appointment repository."""
    return SqlAppointmentRepository(db)


def get_business_hour_repo(db: Session = Depends(get_db)) -> AbstractBusinessHourRepository:
    """FastAPI dependency to get a business hour repository."""
    return SQLBusinessHourRepository(db)


def get_time_off_repo(db: Session = Depends(get_db)) -> AbstractTimeOffRepository:
    """FastAPI dependency to get a time off repository."""
    return SqlTimeOffRepository(db)


def get_service_repo(db: Session = Depends(get_db)) -> AbstractServiceRepository:
    """FastAPI dependency to get a service repository."""
    return SqlServiceRepository(db)


def get_booking_service(
    appointment_repo: AbstractAppointmentRepository = Depends(get_appointment_repo),
    business_hour_repo: AbstractBusinessHourRepository = Depends(get_business_hour_repo),
    time_off_repo: AbstractTimeOffRepository = Depends(get_time_off_repo),
) -> BookingService:
    """FastAPI dependency to get the booking service."""
    return BookingService(
        appointment_repo=appointment_repo,
        business_hour_repo=business_hour_repo,
        time_off_repo=time_off_repo,
    )


def get_service_service(
    service_repo: AbstractServiceRepository = Depends(get_service_repo),
) -> ServiceService:
    """FastAPI dependency to get the service service."""
    return ServiceService(service_repo)


def get_schedule_service(
    business_hour_repo: AbstractBusinessHourRepository = Depends(get_business_hour_repo),
    time_off_repo: AbstractTimeOffRepository = Depends(get_time_off_repo),
) -> ScheduleService:
    """FastAPI dependency to get the schedule service."""
    return ScheduleService(
        business_hour_repo=business_hour_repo,
        time_off_repo=time_off_repo,
    )


def get_appointment_service(
    appointment_repo: AbstractAppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentService:
    """FastAPI dependency to get the appointment service."""
    return AppointmentService(appointment_repo)


def get_dashboard_service(
    appointment_repo: AbstractAppointmentRepository = Depends(get_appointment_repo),
) -> DashboardService:
    """FastAPI dependency to get the dashboard service."""
    return DashboardService(appointment_repo)


def get_transaction_repo(db: Session = Depends(get_db)) -> AbstractTransactionRepository:
    """FastAPI dependency to get a transaction repository."""
    return SqlTransactionRepository(db)


def get_transaction_service(
    transaction_repo: AbstractTransactionRepository = Depends(get_transaction_repo),
) -> TransactionService:
    """FastAPI dependency to get the transaction service."""
    return TransactionService(transaction_repo)
