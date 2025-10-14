"""
Shared Kernel - Timezone Utilities
時區處理工具，確保所有時間都正確處理時區
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

from .config import settings


def get_default_timezone() -> ZoneInfo:
    """取得預設時區"""
    return ZoneInfo(settings.default_timezone)


def now_utc() -> datetime:
    """取得當前 UTC 時間（aware）"""
    return datetime.now(timezone.utc)


def now_local() -> datetime:
    """取得當前本地時間（預設時區）"""
    return datetime.now(get_default_timezone())


def to_utc(dt: datetime) -> datetime:
    """
    轉換為 UTC 時間
    
    Args:
        dt: 任意時區的 datetime（必須是 aware）
    
    Returns:
        UTC 時間的 datetime
    """
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


def to_local(dt: datetime, tz: Optional[str] = None) -> datetime:
    """
    轉換為本地時間
    
    Args:
        dt: UTC datetime
        tz: 時區名稱（如 None 則使用預設時區）
    
    Returns:
        本地時間的 datetime
    """
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    
    target_tz = ZoneInfo(tz) if tz else get_default_timezone()
    return dt.astimezone(target_tz)


def make_aware(dt: datetime, tz: Optional[str] = None) -> datetime:
    """
    將 naive datetime 轉換為 aware datetime
    
    Args:
        dt: naive datetime
        tz: 時區名稱（如 None 則使用預設時區）
    
    Returns:
        aware datetime
    """
    if dt.tzinfo is not None:
        return dt
    
    target_tz = ZoneInfo(tz) if tz else get_default_timezone()
    return dt.replace(tzinfo=target_tz)


# 常用時區常數
TZ_TAIPEI = ZoneInfo("Asia/Taipei")
TZ_UTC = timezone.utc

