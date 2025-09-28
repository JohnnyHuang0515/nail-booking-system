from typing import List
import abc
import uuid
from datetime import date

from app.domain.booking.models import Appointment


class AbstractAppointmentRepository(abc.ABC):
    """Abstract interface for an appointment repository."""

    @abc.abstractmethod
    def add(self, appointment: Appointment) -> None:
        """Adds a new appointment to the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        """Gets an appointment by its unique ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_by_date(self, appointment_date: date) -> List[Appointment]:
        """Lists all appointments for a specific date."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_by_date_range(self, start_date: date, end_date: date) -> List[Appointment]:
        """Lists all appointments within a specific date range."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, appointment: Appointment) -> None:
        """Updates an existing appointment."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, appointment_id: uuid.UUID) -> None:
        """Deletes an appointment by its unique ID."""
        raise NotImplementedError
