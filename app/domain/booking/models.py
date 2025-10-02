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
    merchant_id: uuid.UUID
    name: str
    price: float
    duration_minutes: int
    is_active: bool = True


class AppointmentStatus(str, Enum):
    """Enum for the status of an appointment."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"


class Appointment(BaseModel):
    """Represents an appointment, the aggregate root for the booking context."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    merchant_id: uuid.UUID
    user_id: uuid.UUID | None = None  # 可選，支援直接預約
    service_id: uuid.UUID
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus = AppointmentStatus.PENDING
    
    # 直接預約欄位 (當沒有user_id時使用)
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    notes: str | None = None
    
    # 關聯資料 (可選)
    user: User | None = None
    service: Service | None = None

    def cancel(self) -> None:
        """Cancels the appointment."""
        if self.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            raise ValueError("Only pending or confirmed appointments can be cancelled.")
        self.status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        """Marks the appointment as completed."""
        if self.status not in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]:
            raise ValueError("Only confirmed or in-progress appointments can be completed.")
        self.status = AppointmentStatus.COMPLETED
