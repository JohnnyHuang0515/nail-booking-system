from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class BillingRecordResponse(BaseModel):
    id: str
    merchant_id: str
    merchant_name: str
    plan: str
    amount: float
    status: str
    billing_period: str
    due_date: str
    paid_at: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class BillingSummaryResponse(BaseModel):
    total_revenue: float
    pending_amount: float
    overdue_amount: float
    active_merchants: int
    
    class Config:
        from_attributes = True


class BillingRecordCreate(BaseModel):
    merchant_id: str
    plan: str
    amount: float
    billing_period_start: date
    billing_period_end: date
    due_date: date
    status: str = "pending"


class BillingRecordUpdate(BaseModel):
    plan: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None
