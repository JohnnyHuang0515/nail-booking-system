from datetime import time, datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class BusinessHour(BaseModel):
    """Represents the operating hours for a specific day of the week."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    day_of_week: int  # Monday=0, Sunday=6
    start_time: time
    end_time: time


class TimeOff(BaseModel):
    """Represents a block of time when the service is unavailable."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = None
