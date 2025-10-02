"""
多商家美甲預約系統配置
"""
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 基本設定
    app_name: str = "Multi-Merchant Nail Booking System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 資料庫設定
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/nail_booking_db")
    
    # Redis 設定（用於快取和任務佇列）
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # LINE Bot 設定
    line_webhook_path: str = "/api/v1/line/webhook"
    line_webhook_timeout: int = 30
    
    # 多商家設定
    max_merchants: int = 1000
    default_timezone: str = "Asia/Taipei"
    
    # 安全設定
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = 30
    
    # 排程設定
    reminder_check_interval: int = 3600  # 秒
    status_update_interval: int = 1800   # 秒
    cleanup_interval: int = 86400        # 秒
    
    # 預約設定
    max_advance_booking_days: int = 30
    min_advance_booking_hours: int = 2
    default_appointment_duration: int = 60  # 分鐘
    
    # 通知設定
    enable_email_notifications: bool = False
    enable_sms_notifications: bool = False
    enable_push_notifications: bool = True
    
    # 檔案上傳設定
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # 日誌設定
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 監控設定
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


class MerchantConfig:
    """商家配置管理"""
    
    @staticmethod
    def validate_channel_id(channel_id: str) -> bool:
        """驗證 LINE Channel ID 格式"""
        if not channel_id:
            return False
        
        # LINE Channel ID 通常是 32 字元的十六進位字串
        if len(channel_id) != 32:
            return False
        
        try:
            int(channel_id, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_timezone(timezone: str) -> bool:
        """驗證時區格式"""
        try:
            import pytz
            pytz.timezone(timezone)
            return True
        except:
            return False
    
    @staticmethod
    def get_default_business_hours() -> List[Dict[str, Any]]:
        """取得預設營業時間"""
        return [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "18:00"},  # 週一
            {"day_of_week": 2, "start_time": "09:00", "end_time": "18:00"},  # 週二
            {"day_of_week": 3, "start_time": "09:00", "end_time": "18:00"},  # 週三
            {"day_of_week": 4, "start_time": "09:00", "end_time": "18:00"},  # 週四
            {"day_of_week": 5, "start_time": "09:00", "end_time": "18:00"},  # 週五
            {"day_of_week": 6, "start_time": "09:00", "end_time": "17:00"},  # 週六
            {"day_of_week": 0, "start_time": "10:00", "end_time": "16:00"},  # 週日
        ]
    
    @staticmethod
    def get_default_services() -> List[Dict[str, Any]]:
        """取得預設服務項目"""
        return [
            {"name": "基礎美甲", "price": 800, "duration_minutes": 60},
            {"name": "法式美甲", "price": 1200, "duration_minutes": 90},
            {"name": "彩繪美甲", "price": 1500, "duration_minutes": 120},
            {"name": "光療美甲", "price": 1800, "duration_minutes": 120},
            {"name": "指甲護理", "price": 600, "duration_minutes": 45},
        ]


class SecurityConfig:
    """安全配置"""
    
    # API 速率限制
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # 秒
    
    # Webhook 安全設定
    webhook_signature_validation: bool = True
    webhook_timeout: int = 30
    
    # 資料隔離設定
    enable_row_level_security: bool = False
    force_merchant_isolation: bool = True
    
    # 敏感資料加密
    encrypt_sensitive_data: bool = True
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")


class NotificationConfig:
    """通知配置"""
    
    # LINE 通知設定
    line_notification_enabled: bool = True
    line_retry_attempts: int = 3
    line_retry_delay: int = 5  # 秒
    
    # 提醒時間設定
    reminder_times: List[int] = [24, 2]  # 小時前提醒
    
    # 通知模板設定
    enable_custom_templates: bool = True
    default_language: str = "zh-TW"


# 全域設定實例
settings = Settings()

# 配置驗證函數
def validate_config():
    """驗證配置設定"""
    errors = []
    
    # 驗證必要的環境變數
    required_env_vars = ["DATABASE_URL"]
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"缺少必要的環境變數: {var}")
    
    # 驗證資料庫 URL 格式
    if not settings.database_url.startswith(("postgresql://", "sqlite:///")):
        errors.append("無效的資料庫 URL 格式")
    
    # 驗證 Redis URL 格式
    if not settings.redis_url.startswith("redis://"):
        errors.append("無效的 Redis URL 格式")
    
    if errors:
        raise ValueError(f"配置驗證失敗: {', '.join(errors)}")
    
    return True


# 初始化時驗證配置
try:
    validate_config()
    print("配置驗證通過")
except ValueError as e:
    print(f"配置驗證失敗: {str(e)}")
    raise
