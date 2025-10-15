"""
API Gateway - FastAPI Main Application
BFF (Backend for Frontend) 主入口
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import SessionLocal
from identity.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from identity.application.services import PasswordService

# 建立 FastAPI 應用
app = FastAPI(
    title="LINE 美甲預約系統 API",
    description="基於 DDD × BDD × TDD 的多租戶預約系統",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 中介層
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Admin Panel
        "http://localhost:3001",  # Customer Booking
        "http://localhost:3002",  # System Admin Panel
        "https://liff.line.me",   # LINE LIFF
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 資料模型 ===

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str = None
    user: dict = None
    message: str = None

# === 資料庫依賴 ===

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === 認證端點 ===

@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest, db = Depends(get_db)):
    """用戶登入"""
    user_repo = SQLAlchemyUserRepository(db)
    
    # 查找用戶
    user = user_repo.find_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )
    
    # 驗證密碼
    if not PasswordService.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )
    
    # 檢查用戶是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="帳號已被停用"
        )
    
    # 生成響應
    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.name.value
    }
    
    # 如果是商家用戶，添加 merchant_id
    if user.merchant_id:
        user_data["merchant_id"] = user.merchant_id
    
    return LoginResponse(
        success=True,
        token=f"jwt-token-{user.id}",  # 簡化的 token
        user=user_data,
        message="登入成功"
    )

@app.get("/api/v1/auth/me", tags=["Authentication"])
async def get_current_user():
    """獲取當前用戶資訊"""
    return {
        "id": "system-admin-001",
        "email": "system@nailbooking.com",
        "name": "系統管理員",
        "role": "ADMIN"
    }

# === 系統管理員端點 ===

@app.get("/api/v1/admin/stats", tags=["System Admin"])
async def get_admin_stats():
    """獲取系統統計數據"""
    return {
        "total_merchants": 5,
        "active_merchants": 4,
        "total_bookings": 128,
        "total_revenue": 25600.50
    }

@app.get("/api/v1/admin/merchants", tags=["System Admin"])
async def get_merchants():
    """獲取商家列表"""
    return [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "美甲沙龍 A",
            "slug": "nail-salon-a",
            "email": "merchant@nailbooking.com",
            "is_active": True,
            "total_bookings": 45,
            "total_revenue": 8900.00
        },
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "name": "美甲沙龍 B",
            "slug": "nail-salon-b",
            "email": "merchant2@nailbooking.com",
            "is_active": True,
            "total_bookings": 32,
            "total_revenue": 6400.00
        },
        {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "美甲沙龍 C",
            "slug": "nail-salon-c",
            "email": "merchant3@nailbooking.com",
            "is_active": False,
            "total_bookings": 18,
            "total_revenue": 3600.00
        }
    ]

# === 健康檢查 ===

@app.get("/health", tags=["System"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "nail-booking-api",
        "version": "0.1.0",
        "environment": "development"
    }

@app.get("/", tags=["System"])
async def root():
    """API 根路徑"""
    return {
        "message": "LINE 美甲預約系統 API",
        "docs": "/docs",
        "health": "/health"
    }

# === 全局異常處理 ===

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局異常處理"""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "系統發生錯誤，請稍後再試"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )