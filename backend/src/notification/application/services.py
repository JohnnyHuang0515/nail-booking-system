"""
Notification Context - Application Layer - Services
NotificationService 協調訊息發送邏輯
"""
from typing import Optional
import logging
from uuid import uuid4

from notification.domain.models import (
    MessageTemplate, NotificationType, ChannelType, NotificationRecord
)
from notification.domain.line_service import LineMessagingService
from notification.domain.exceptions import (
    TemplateNotFoundError,
    TemplateRenderError,
    NotificationSendError,
    LineCredentialsNotConfiguredError
)
from merchant.domain.models import Merchant


logger = logging.getLogger(__name__)


class NotificationService:
    """
    NotificationService 應用服務
    
    職責：
    1. 訊息模板渲染
    2. 訊息發送（LINE、Email、SMS）
    3. 通知記錄追蹤
    4. 領域事件訂閱
    """
    
    def __init__(
        self,
        # template_repo: MessageTemplateRepository,  # 簡化：不使用 Repository
        # notification_repo: NotificationRepository
    ):
        # self.template_repo = template_repo
        # self.notification_repo = notification_repo
        pass
    
    def send_booking_confirmed_notification(
        self,
        merchant: Merchant,
        customer_line_user_id: str,
        customer_name: str,
        booking_id: str,
        start_at: str,
        service_name: str
    ) -> bool:
        """
        發送預約確認通知
        
        Args:
            merchant: 商家聚合
            customer_line_user_id: 客戶 LINE User ID
            customer_name: 客戶姓名
            booking_id: 預約 ID
            start_at: 預約時間
            service_name: 服務名稱
        
        Returns:
            是否發送成功
        """
        # 建立預設模板（實際環境從 Repository 讀取）
        template = self._get_default_template(
            NotificationType.BOOKING_CONFIRMED,
            merchant.id
        )
        
        # 渲染訊息
        try:
            message = template.create_line_message(
                customer_name=customer_name,
                merchant_name=merchant.name,
                service_name=service_name,
                start_at=start_at,
                booking_id=booking_id
            )
        except Exception as e:
            logger.error(f"模板渲染失敗: {e}")
            raise TemplateRenderError(template.template_key.value, str(e))
        
        # 發送 LINE 訊息
        if merchant.line_credentials and merchant.line_credentials.is_configured():
            line_service = LineMessagingService(
                channel_access_token=merchant.line_credentials.channel_access_token
            )
            
            try:
                success = line_service.send_message(
                    to=customer_line_user_id,
                    message=message
                )
                
                # 記錄通知（簡化：僅 log）
                logger.info(
                    f"預約確認通知已發送: {booking_id} -> {customer_line_user_id}"
                )
                
                return success
            except Exception as e:
                logger.error(f"LINE 發送失敗: {e}")
                return False
        else:
            logger.warning(f"商家 {merchant.id} 未配置 LINE 憑證，跳過推播")
            return False
    
    def send_booking_cancelled_notification(
        self,
        merchant: Merchant,
        customer_line_user_id: str,
        customer_name: str,
        booking_id: str,
        start_at: str,
        service_name: str
    ) -> bool:
        """發送預約取消通知"""
        template = self._get_default_template(
            NotificationType.BOOKING_CANCELLED,
            merchant.id
        )
        
        try:
            message = template.create_line_message(
                customer_name=customer_name,
                merchant_name=merchant.name,
                service_name=service_name,
                start_at=start_at,
                booking_id=booking_id
            )
        except Exception as e:
            raise TemplateRenderError(template.template_key.value, str(e))
        
        if merchant.line_credentials and merchant.line_credentials.is_configured():
            line_service = LineMessagingService(
                channel_access_token=merchant.line_credentials.channel_access_token
            )
            
            try:
                success = line_service.send_message(
                    to=customer_line_user_id,
                    message=message
                )
                
                logger.info(
                    f"預約取消通知已發送: {booking_id} -> {customer_line_user_id}"
                )
                
                return success
            except Exception as e:
                logger.error(f"LINE 發送失敗: {e}")
                return False
        else:
            logger.warning(f"商家 {merchant.id} 未配置 LINE 憑證，跳過推播")
            return False
    
    def _get_default_template(
        self,
        template_type: NotificationType,
        merchant_id: str
    ) -> MessageTemplate:
        """
        取得預設模板（簡化版）
        
        實際環境應從 Repository 讀取客製化模板
        """
        templates = {
            NotificationType.BOOKING_CONFIRMED: """
🎉 預約確認通知

親愛的 {customer_name}，您好！

您在 {merchant_name} 的預約已確認：

📅 預約時間: {start_at}
💅 服務項目: {service_name}
🔖 預約編號: {booking_id}

期待您的光臨！如需取消或變更，請提前聯繫我們。

{merchant_name} 敬上
            """.strip(),
            
            NotificationType.BOOKING_CANCELLED: """
❌ 預約取消通知

親愛的 {customer_name}，您好！

您的預約已成功取消：

📅 原預約時間: {start_at}
💅 服務項目: {service_name}
🔖 預約編號: {booking_id}

如有需要，歡迎隨時再次預約！

{merchant_name} 敬上
            """.strip()
        }
        
        return MessageTemplate(
            id=0,
            merchant_id=merchant_id,
            template_key=template_type,
            channel_type=ChannelType.LINE,
            template=templates.get(template_type, "預設訊息模板"),
            is_active=True
        )

