import abc
import uuid

from app.domain.membership.models import User


class AbstractUserRepository(abc.ABC):
    """Abstract interface for a user repository."""

    @abc.abstractmethod
    def add(self, user: User) -> None:
        """Adds a new user to the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Gets a user by their unique ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_line_user_id(self, line_user_id: str) -> User | None:
        """Gets a user by their LINE user ID."""
        raise NotImplementedError
