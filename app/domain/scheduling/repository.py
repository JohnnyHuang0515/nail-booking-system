import abc
import uuid
from datetime import date
from app.domain.scheduling.models import BusinessHour, TimeOff


class AbstractBusinessHourRepository(abc.ABC):
    """Abstract interface for a business hour repository."""

    @abc.abstractmethod
    def get_by_day(self, day_of_week: int) -> BusinessHour | None:
        """Gets business hours for a specific day of the week."""
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, business_hour: BusinessHour) -> None:
        """Adds a new business hour setting."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """Deletes all business hour settings."""
        raise NotImplementedError


class AbstractTimeOffRepository(abc.ABC):
    """Abstract interface for a time off repository."""

    @abc.abstractmethod
    def list_by_date(self, for_date: date) -> list[TimeOff]:
        """Lists all time off periods that overlap with a specific date."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_all(self) -> list[TimeOff]:
        """Lists all time off periods."""
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, time_off: TimeOff) -> None:
        """Adds a new time off period."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, time_off_id: uuid.UUID) -> TimeOff | None:
        """Gets a time off period by its unique ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, time_off_id: uuid.UUID) -> None:
        """Deletes a time off period by its unique ID."""
        raise NotImplementedError
