"""
API Gateway - FastAPI Main Application
BFF (Backend for Frontend) 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from shared.config import settings
from shared.database import engine, Base
from booking.infrastructure.routers import liff_router

# 設定日誌
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

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
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 路由註冊 ===

# 註冊路由
from identity.infrastructure.routers import auth_router
from api.routers import public_router

# Identity Context - 認證 API
app.include_router(auth_router.router)

# Public API - 公開查詢（無需認證）
app.include_router(public_router.router)

# Booking Context - LIFF 客戶端 API
app.include_router(liff_router.router)

# Merchant API - 商家端
try:
    from api.routers import merchant_router
    app.include_router(merchant_router.router)
    logger.info("✅ Merchant router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load merchant router: {e}")
    import traceback
    traceback.print_exc()

# TODO: 新增系統管理員路由
# app.include_router(admin_router.router)


# === 健康檢查 ===

@app.get("/health", tags=["System"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "nail-booking-api",
        "version": "0.1.0",
        "environment": settings.environment
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
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "系統發生錯誤，請稍後再試"
        }
    )


# === 啟動事件 ===

@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    logger.info("🚀 API Server starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # 開發環境：自動建立資料表（生產環境應使用 Alembic）
    if settings.debug:
        logger.warning("Debug mode: Creating database tables...")
        Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    logger.info("👋 API Server shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

