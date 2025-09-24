import uuid
from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user, the aggregate root for the membership context."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    line_user_id: str
    name: str | None = None
    phone: str | None = None
