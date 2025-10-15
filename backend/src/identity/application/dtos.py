"""
Identity Context - Application Layer - DTOs
認證相關的 Request/Response DTOs
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    """註冊請求"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="密碼（至少 6 字元）")
    name: Optional[str] = Field(None, description="姓名")
    merchant_id: Optional[str] = Field(None, description="所屬商家 ID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "secret123",
                "name": "王小明",
                "merchant_id": "00000000-0000-0000-0000-000000000001"
            }
        }
    }


class LoginRequest(BaseModel):
    """登入請求"""
    email: EmailStr
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "secret123"
            }
        }
    }


class TokenResponse(BaseModel):
    """Token 回應"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token 有效期（秒）")
    user: "UserResponse"


class UserResponse(BaseModel):
    """用戶資訊回應"""
    id: str
    email: Optional[str]
    line_user_id: Optional[str]
    name: Optional[str]
    merchant_id: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "line_user_id": None,
                "name": "王小明",
                "merchant_id": "00000000-0000-0000-0000-000000000001",
                "role": "customer",
                "is_active": True,
                "is_verified": False
            }
        }
    }
