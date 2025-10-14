"""
Merchant Context - Domain Layer - Aggregates
Merchant 聚合根
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
from enum import Enum
from typing import Optional


class MerchantStatus(str, Enum):
    """商家狀態"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


@dataclass
class LineCredentials:
    """
    LINE 憑證（值物件）
    
    注意：實際環境中應加密儲存
    """
    channel_id: Optional[str] = None
    channel_secret: Optional[str] = None
    channel_access_token: Optional[str] = None
    bot_basic_id: Optional[str] = None
    
    def is_configured(self) -> bool:
        """檢查 LINE 憑證是否已配置"""
        return (
            self.channel_id is not None 
            and self.channel_secret is not None 
            and self.channel_access_token is not None
        )


class Merchant:
    """
    Merchant 聚合根
    
    不變式：
    1. slug 必須唯一
    2. status 為 active 才能接受預約
    3. LINE 憑證應加密儲存（Infrastructure 層處理）
    4. timezone 必須為有效的 IANA 時區
    """
    
    def __init__(
        self,
        id: str,  # UUID
        slug: str,
        name: str,
        status: MerchantStatus = MerchantStatus.ACTIVE,
        timezone: str = "Asia/Taipei",
        address: Optional[str] = None,
        phone: Optional[str] = None,
        line_credentials: Optional[LineCredentials] = None,
        metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.slug = slug
        self.name = name
        self.status = status
        self.timezone = timezone
        self.address = address
        self.phone = phone
        self.line_credentials = line_credentials or LineCredentials()
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(dt_timezone.utc)
        self.updated_at = updated_at
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if not self.slug:
            raise ValueError("商家 slug 不可為空")
        
        if not self.name:
            raise ValueError("商家名稱不可為空")
        
        # 驗證 slug 格式（小寫字母、數字、連字符）
        import re
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            raise ValueError("商家 slug 只能包含小寫字母、數字和連字符")
        
        # 驗證時區（簡化版，生產環境應使用 pytz）
        valid_timezones = [
            "Asia/Taipei", "Asia/Tokyo", "Asia/Hong_Kong", 
            "Asia/Singapore", "UTC"
        ]
        if self.timezone not in valid_timezones:
            raise ValueError(f"無效的時區：{self.timezone}")
    
    def is_active(self) -> bool:
        """檢查商家是否為啟用狀態"""
        return self.status == MerchantStatus.ACTIVE
    
    def can_accept_booking(self) -> bool:
        """
        檢查商家是否可接受預約
        
        條件：
        1. 狀態為 active
        2. （未來可加入訂閱檢查）
        """
        return self.is_active()
    
    def activate(self):
        """啟用商家"""
        self.status = MerchantStatus.ACTIVE
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def suspend(self):
        """暫停商家"""
        self.status = MerchantStatus.SUSPENDED
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def cancel(self):
        """取消商家（不可恢復）"""
        self.status = MerchantStatus.CANCELLED
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def update_line_credentials(
        self,
        channel_id: str,
        channel_secret: str,
        channel_access_token: str,
        bot_basic_id: Optional[str] = None
    ):
        """更新 LINE 憑證"""
        self.line_credentials = LineCredentials(
            channel_id=channel_id,
            channel_secret=channel_secret,
            channel_access_token=channel_access_token,
            bot_basic_id=bot_basic_id
        )
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def update_info(
        self,
        name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        timezone: Optional[str] = None
    ):
        """更新商家基本資訊"""
        if name is not None:
            self.name = name
        if address is not None:
            self.address = address
        if phone is not None:
            self.phone = phone
        if timezone is not None:
            # 驗證時區
            valid_timezones = [
                "Asia/Taipei", "Asia/Tokyo", "Asia/Hong_Kong", 
                "Asia/Singapore", "UTC"
            ]
            if timezone not in valid_timezones:
                raise ValueError(f"無效的時區：{timezone}")
            self.timezone = timezone
        
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def __repr__(self) -> str:
        return f"<Merchant(id={self.id}, slug={self.slug}, status={self.status.value})>"

