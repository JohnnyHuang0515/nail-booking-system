from pydantic import BaseModel
from typing import Optional, Any
import uuid
from decimal import Decimal
from datetime import datetime


class Transaction(BaseModel):
    """Domain model for Transaction."""
    id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    appointment_id: Optional[uuid.UUID] = None
    amount: Decimal
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # 動態屬性，用於關聯資料
    user: Optional[Any] = None
    appointment: Optional[Any] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
