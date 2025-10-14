"""
Booking Context - Application Layer - DTOs
Data Transfer Objects: API 請求/響應結構
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# === 請求 DTOs ===

class CustomerDTO(BaseModel):
    """客戶資訊 DTO"""
    line_user_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^09\d{8}$")
    email: Optional[str] = None


class BookingItemRequest(BaseModel):
    """預約項目請求"""
    service_id: int = Field(..., gt=0)
    option_ids: list[int] = Field(default_factory=list)


class CreateBookingRequest(BaseModel):
    """建立預約請求"""
    merchant_id: str = Field(..., pattern=r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$")
    customer: CustomerDTO
    staff_id: int = Field(..., gt=0)
    start_at: datetime
    items: list[BookingItemRequest] = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator("start_at")
    @classmethod
    def validate_start_at(cls, v: datetime) -> datetime:
        """驗證開始時間"""
        if v.tzinfo is None:
            raise ValueError("start_at 必須包含時區資訊")
        
        # 確保是未來時間（允許5分鐘誤差）
        from shared.timezone import now_utc
        from datetime import timedelta
        if v < (now_utc() - timedelta(minutes=5)):
            raise ValueError("預約時間不可為過去時間")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer": {
                    "line_user_id": "U1234567890abcdef",
                    "name": "王小明",
                    "phone": "0912345678"
                },
                "staff_id": 1,
                "start_at": "2025-10-16T14:00:00+08:00",
                "items": [
                    {
                        "service_id": 1,
                        "option_ids": [1, 2]
                    }
                ],
                "notes": "第一次來訪"
            }
        }


class CancelBookingRequest(BaseModel):
    """取消預約請求"""
    booking_id: str
    merchant_id: str
    requester_line_id: str
    reason: Optional[str] = Field(None, max_length=200)


class GetSlotsRequest(BaseModel):
    """查詢可訂時段請求"""
    merchant_id: str
    staff_id: Optional[int] = None
    target_date: date
    service_ids: list[int] = Field(default_factory=list)


# === 響應 DTOs ===

class BookingItemResponse(BaseModel):
    """預約項目響應"""
    service_id: int
    service_name: str
    service_price: Decimal
    service_duration_minutes: int
    option_ids: list[int]
    option_names: list[str]
    total_price: Decimal
    total_duration_minutes: int


class BookingResponse(BaseModel):
    """預約響應"""
    id: str
    merchant_id: str
    customer: CustomerDTO
    staff_id: int
    status: str
    start_at: datetime
    end_at: datetime
    items: list[BookingItemResponse]
    total_price: Decimal
    total_duration_minutes: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SlotResponse(BaseModel):
    """可訂時段響應"""
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    available: bool
    duration_minutes: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "14:00",
                "end_time": "15:00",
                "available": True,
                "duration_minutes": 60
            }
        }

