import abc
import uuid
from app.domain.booking.models import Service


class AbstractServiceRepository(abc.ABC):
    """Abstract interface for a service repository."""

    @abc.abstractmethod
    def add(self, service: Service) -> None:
        """Adds a new service to the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, service_id: uuid.UUID) -> Service | None:
        """Gets a service by its unique ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[Service]:
        """Lists all services."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, service: Service) -> None:
        """Updates an existing service."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, service_id: uuid.UUID) -> None:
        """Deletes a service by its unique ID."""
        raise NotImplementedError
