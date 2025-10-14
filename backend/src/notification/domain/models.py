"""
Notification Context - Domain Layer - Aggregates
MessageTemplate 訊息模板聚合
"""
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from enum import Enum
from typing import Optional


class NotificationType(str, Enum):
    """通知類型"""
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_COMPLETED = "booking_completed"


class ChannelType(str, Enum):
    """通知渠道"""
    LINE = "line"
    EMAIL = "email"
    SMS = "sms"


@dataclass
class LineMessage:
    """
    LINE 訊息（值物件）
    
    封裝 LINE Messaging API 的訊息格式
    """
    text: str
    type: str = "text"
    
    def to_dict(self) -> dict:
        """轉換為 LINE API 格式"""
        return {
            "type": self.type,
            "text": self.text
        }


class MessageTemplate:
    """
    MessageTemplate 聚合根（訊息模板）
    
    不變式：
    1. template_key 唯一識別模板
    2. channel_type 決定發送渠道
    3. template 包含變數佔位符（如 {customer_name}）
    """
    
    def __init__(
        self,
        id: int,
        merchant_id: str,
        template_key: NotificationType,
        channel_type: ChannelType,
        template: str,
        subject: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.template_key = template_key
        self.channel_type = channel_type
        self.template = template
        self.subject = subject
        self.is_active = is_active
        self.created_at = created_at or datetime.now(dt_timezone.utc)
        self.updated_at = updated_at
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if not self.template:
            raise ValueError("訊息模板內容不可為空")
    
    def render(self, **kwargs) -> str:
        """
        渲染模板（替換變數）
        
        Args:
            **kwargs: 變數字典
        
        Returns:
            渲染後的訊息
        """
        return self.template.format(**kwargs)
    
    def create_line_message(self, **kwargs) -> LineMessage:
        """
        建立 LINE 訊息
        
        Args:
            **kwargs: 變數字典
        
        Returns:
            LineMessage 值物件
        """
        text = self.render(**kwargs)
        return LineMessage(text=text)
    
    def __repr__(self) -> str:
        return f"<MessageTemplate(id={self.id}, key={self.template_key.value})>"


@dataclass
class NotificationRecord:
    """
    通知記錄（實體）
    
    記錄每次發送的通知，用於追蹤與除錯
    """
    id: str  # UUID
    merchant_id: str
    recipient: str  # LINE User ID, Email, or Phone
    channel_type: ChannelType
    notification_type: NotificationType
    message: str
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(dt_timezone.utc)
    
    def mark_as_sent(self):
        """標記為已發送"""
        self.status = "sent"
        self.sent_at = datetime.now(dt_timezone.utc)
    
    def mark_as_failed(self, error: str):
        """標記為失敗"""
        self.status = "failed"
        self.error_message = error

