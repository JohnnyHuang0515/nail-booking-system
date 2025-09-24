import uuid
from datetime import date, time
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    """Represents a user in the system."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    line_user_id: str
    name: str | None = None
    phone: str | None = None


class Service(BaseModel):
    """Represents a service offered by the nail artist."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    price: float
    duration_minutes: int
    is_active: bool = True


class AppointmentStatus(str, Enum):
    """Enum for the status of an appointment."""
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class Appointment(BaseModel):
    """Represents an appointment, the aggregate root for the booking context."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    service_id: uuid.UUID
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus = AppointmentStatus.BOOKED
    
    # 關聯資料 (可選)
    user: User | None = None
    service: Service | None = None

    def cancel(self) -> None:
        """Cancels the appointment."""
        if self.status not in [AppointmentStatus.BOOKED]:
            raise ValueError("Only booked appointments can be cancelled.")
        self.status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        """Marks the appointment as completed."""
        if self.status not in [AppointmentStatus.BOOKED]:
            raise ValueError("Only a booked appointment can be completed.")
        self.status = AppointmentStatus.COMPLETED
