"""
簡化的後端啟動腳本 - 避免複雜依賴
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Multi-Merchant Nail Booking System",
    description="多商家美甲預約系統 API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬資料
mock_merchants = [
    {
        "id": "1",
        "name": "台北時尚美甲",
        "line_channel_id": "taipei_fashion_channel_1234567890abcdef",
        "liff_id": "liff-taipei-fashion-123",
        "timezone": "Asia/Taipei",
        "is_active": True,
        "created_at": "2024-01-15T00:00:00Z"
    },
    {
        "id": "2", 
        "name": "高雄藝術美甲",
        "line_channel_id": "kaohsiung_art_channel_1234567890abcdef",
        "liff_id": "liff-kaohsiung-art-456",
        "timezone": "Asia/Taipei",
        "is_active": True,
        "created_at": "2024-01-20T00:00:00Z"
    }
]

mock_users = [
    {
        "id": "1",
        "line_user_id": "U1234567890abcdef",
        "name": "張小明",
        "phone": "0912345678",
        "merchant_id": "1",
        "merchant_name": "台北時尚美甲",
        "created_at": "2024-01-15T10:00:00Z"
    }
]

# API Models
class MerchantResponse(BaseModel):
    id: str
    name: str
    line_channel_id: str
    liff_id: str
    timezone: str
    is_active: bool
    created_at: str

class UserResponse(BaseModel):
    id: str
    line_user_id: str
    name: str
    phone: str
    merchant_id: str
    merchant_name: str
    created_at: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# API Endpoints
@app.get("/")
async def root():
    """健康檢查"""
    return {
        "status": "ok", 
        "message": "多商家美甲預約系統 API 運行中！",
        "version": "1.0.0"
    }

@app.get("/api/v1/merchants", response_model=List[MerchantResponse])
async def get_merchants():
    """取得所有商家"""
    return mock_merchants

@app.get("/api/v1/merchants/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(merchant_id: str):
    """取得單一商家"""
    for merchant in mock_merchants:
        if merchant["id"] == merchant_id:
            return merchant
    raise HTTPException(status_code=404, detail="找不到指定的商家")

@app.get("/api/v1/users", response_model=List[UserResponse])
async def get_users(merchant_id: Optional[str] = None):
    """取得用戶列表"""
    if merchant_id:
        return [user for user in mock_users if user["merchant_id"] == merchant_id]
    return mock_users

@app.post("/api/v1/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """管理員登入"""
    if request.username == "admin" and request.password == "admin123":
        return LoginResponse(
            access_token="mock_admin_token_123456789",
            token_type="bearer",
            user={
                "id": "1",
                "username": "admin",
                "email": "admin@platform.com",
                "role": "super_admin",
                "permissions": ["merchant_management", "system_settings", "reports"]
            }
        )
    else:
        raise HTTPException(status_code=401, detail="用戶名或密碼錯誤")

@app.post("/api/v1/merchant-auth/email-login", response_model=LoginResponse)
async def merchant_email_login(email: str, password: str):
    """商家 Email 登入"""
    if email == "merchant@example.com" and password == "merchant123":
        return LoginResponse(
            access_token="mock_merchant_token_123456789",
            token_type="bearer",
            user={
                "id": "1",
                "name": "台北時尚美甲",
                "email": email,
                "line_channel_id": "taipei_fashion_channel_1234567890abcdef",
                "liff_id": "liff-taipei-fashion-123",
                "timezone": "Asia/Taipei",
                "is_active": True
            }
        )
    else:
        raise HTTPException(status_code=401, detail="Email 或密碼錯誤")

@app.get("/api/v1/admin/system-stats")
async def get_system_stats():
    """取得系統統計"""
    return {
        "total_merchants": len(mock_merchants),
        "active_merchants": len([m for m in mock_merchants if m["is_active"]]),
        "total_users": len(mock_users),
        "total_appointments": 0,
        "total_revenue": 0.0,
        "system_health": {
            "database": "healthy",
            "redis": "healthy", 
            "line_api": "healthy",
            "load_average": "normal"
        }
    }

@app.get("/api/v1/admin/merchants")
async def get_merchant_stats():
    """取得商家統計"""
    return [
        {
            "merchant_id": merchant["id"],
            "name": merchant["name"],
            "total_users": 1 if merchant["id"] == "1" else 0,
            "total_appointments": 0,
            "total_revenue": 0.0,
            "is_active": merchant["is_active"]
        }
        for merchant in mock_merchants
    ]

if __name__ == "__main__":
    print("🚀 啟動簡化版後端 API...")
    print("📱 前端訪問地址:")
    print("   商家後台:     http://localhost:3000")
    print("   顧客端:       http://localhost:3001")
    print("   平台管理員:   http://localhost:3002")
    print("🔧 後端 API:    http://localhost:8000")
    print("📖 API 文檔:    http://localhost:8000/docs")
    
    uvicorn.run("simple_backend:app", host="0.0.0.0", port=8000, reload=True)
