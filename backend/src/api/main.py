"""
API Gateway - FastAPI Main Application
BFF (Backend for Frontend) 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

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