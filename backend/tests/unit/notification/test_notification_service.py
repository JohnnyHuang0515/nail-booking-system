"""
Notification Context - Unit Tests - NotificationService
測試通知服務的業務邏輯
"""
import pytest
from datetime import datetime, timezone as dt_timezone

from notification.domain.models import (
    MessageTemplate, NotificationType, ChannelType, LineMessage
)
from notification.application.services import NotificationService
from merchant.domain.models import Merchant, MerchantStatus, LineCredentials


class TestMessageTemplate:
    """MessageTemplate 聚合根測試"""
    
    def test_create_template(self):
        """✅ 測試案例：建立訊息模板"""
        # Act
        template = MessageTemplate(
            id=1,
            merchant_id="merchant-001",
            template_key=NotificationType.BOOKING_CONFIRMED,
            channel_type=ChannelType.LINE,
            template="您好 {customer_name}，您的預約已確認！"
        )
        
        # Assert
        assert template.id == 1
        assert template.template_key == NotificationType.BOOKING_CONFIRMED
        assert template.is_active is True
    
    def test_empty_template_raises_error(self):
        """✅ 測試案例：空模板應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="訊息模板內容不可為空"):
            MessageTemplate(
                id=1,
                merchant_id="merchant-001",
                template_key=NotificationType.BOOKING_CONFIRMED,
                channel_type=ChannelType.LINE,
                template=""  # 空字串
            )
    
    def test_render_template(self):
        """✅ 測試案例：渲染模板"""
        # Arrange
        template = MessageTemplate(
            id=1,
            merchant_id="merchant-001",
            template_key=NotificationType.BOOKING_CONFIRMED,
            channel_type=ChannelType.LINE,
            template="您好 {customer_name}，預約時間：{start_at}"
        )
        
        # Act
        rendered = template.render(
            customer_name="王小明",
            start_at="2025-10-16 14:00"
        )
        
        # Assert
        assert "王小明" in rendered
        assert "2025-10-16 14:00" in rendered
    
    def test_create_line_message(self):
        """✅ 測試案例：建立 LINE 訊息"""
        # Arrange
        template = MessageTemplate(
            id=1,
            merchant_id="merchant-001",
            template_key=NotificationType.BOOKING_CONFIRMED,
            channel_type=ChannelType.LINE,
            template="您好 {customer_name}"
        )
        
        # Act
        message = template.create_line_message(customer_name="王小明")
        
        # Assert
        assert isinstance(message, LineMessage)
        assert message.text == "您好 王小明"
        assert message.type == "text"


class TestLineMessage:
    """LineMessage 值物件測試"""
    
    def test_create_line_message(self):
        """✅ 測試案例：建立 LINE 訊息"""
        # Act
        message = LineMessage(text="測試訊息")
        
        # Assert
        assert message.text == "測試訊息"
        assert message.type == "text"
    
    def test_to_dict(self):
        """✅ 測試案例：轉換為 LINE API 格式"""
        # Arrange
        message = LineMessage(text="測試訊息")
        
        # Act
        result = message.to_dict()
        
        # Assert
        assert result == {"type": "text", "text": "測試訊息"}


class TestNotificationService:
    """NotificationService 測試"""
    
    def test_send_booking_confirmed_notification_without_line_credentials(self):
        """✅ 測試案例：無 LINE 憑證時跳過推播"""
        # Arrange
        service = NotificationService()
        merchant = Merchant(
            id="merchant-001",
            slug="test-salon",
            name="測試美甲沙龍",
            status=MerchantStatus.ACTIVE
        )
        
        # Act
        success = service.send_booking_confirmed_notification(
            merchant=merchant,
            customer_line_user_id="U123456789",
            customer_name="王小明",
            booking_id="booking-001",
            start_at="2025-10-16 14:00",
            service_name="凝膠指甲"
        )
        
        # Assert
        assert success is False  # 無憑證，返回 False
    
    def test_send_booking_confirmed_notification_with_line_credentials(self):
        """✅ 測試案例：有 LINE 憑證時發送推播（MOCK）"""
        # Arrange
        service = NotificationService()
        merchant = Merchant(
            id="merchant-001",
            slug="test-salon",
            name="測試美甲沙龍",
            status=MerchantStatus.ACTIVE,
            line_credentials=LineCredentials(
                channel_id="123456",
                channel_secret="secret",
                channel_access_token="mock_token",
                bot_basic_id="@bot"
            )
        )
        
        # Act
        success = service.send_booking_confirmed_notification(
            merchant=merchant,
            customer_line_user_id="U123456789",
            customer_name="王小明",
            booking_id="booking-001",
            start_at="2025-10-16 14:00",
            service_name="凝膠指甲"
        )
        
        # Assert
        assert success is True  # MOCK 發送成功
    
    def test_send_booking_cancelled_notification(self):
        """✅ 測試案例：發送取消通知"""
        # Arrange
        service = NotificationService()
        merchant = Merchant(
            id="merchant-001",
            slug="test-salon",
            name="測試美甲沙龍",
            status=MerchantStatus.ACTIVE,
            line_credentials=LineCredentials(
                channel_id="123456",
                channel_secret="secret",
                channel_access_token="mock_token"
            )
        )
        
        # Act
        success = service.send_booking_cancelled_notification(
            merchant=merchant,
            customer_line_user_id="U123456789",
            customer_name="王小明",
            booking_id="booking-001",
            start_at="2025-10-16 14:00",
            service_name="凝膠指甲"
        )
        
        # Assert
        assert success is True


class TestNotificationType:
    """NotificationType 枚舉測試"""
    
    def test_notification_types(self):
        """✅ 測試案例：通知類型枚舉值正確"""
        assert NotificationType.BOOKING_CONFIRMED.value == "booking_confirmed"
        assert NotificationType.BOOKING_CANCELLED.value == "booking_cancelled"
        assert NotificationType.BOOKING_REMINDER.value == "booking_reminder"
        assert NotificationType.BOOKING_COMPLETED.value == "booking_completed"


class TestChannelType:
    """ChannelType 枚舉測試"""
    
    def test_channel_types(self):
        """✅ 測試案例：渠道類型枚舉值正確"""
        assert ChannelType.LINE.value == "line"
        assert ChannelType.EMAIL.value == "email"
        assert ChannelType.SMS.value == "sms"

