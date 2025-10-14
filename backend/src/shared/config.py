"""
Shared Kernel - Configuration
使用 Pydantic Settings 管理環境變數
"""
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用配置 - 從環境變數載入"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "LINE Nail Booking System"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # Database - PostgreSQL
    database_url: PostgresDsn = Field(
        default="postgresql://dev:dev123@localhost:5432/nail_booking"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 0
    database_echo: bool = False
    
    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    
    # JWT Authentication
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32
    )
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    
    # LINE Integration
    line_channel_secret: Optional[str] = None
    line_channel_access_token: Optional[str] = None
    
    # Stripe Integration
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "ap-northeast-1"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",  # Admin Panel
        "http://localhost:3001",  # Customer Booking
        "https://liff.line.me",   # LINE LIFF
    ]
    
    # Timezone
    default_timezone: str = "Asia/Taipei"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # Observability
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"


# 全局設定實例
settings = Settings()

