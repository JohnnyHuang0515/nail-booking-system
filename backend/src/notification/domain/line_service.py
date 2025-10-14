"""
Notification Context - Domain Layer - LINE Messaging Service
LINE Messaging API 封裝（值服務）
"""
from typing import Optional
import logging

# LINE SDK（在實際環境需安裝：pip install line-bot-sdk）
# from linebot import LineBotApi
# from linebot.models import TextSendMessage
# from linebot.exceptions import LineBotApiError

from notification.domain.models import LineMessage
from notification.domain.exceptions import NotificationSendError


logger = logging.getLogger(__name__)


class LineMessagingService:
    """
    LINE Messaging 服務（值服務）
    
    封裝 LINE Messaging API 的發送邏輯
    """
    
    def __init__(
        self,
        channel_access_token: Optional[str] = None
    ):
        self.channel_access_token = channel_access_token
        # self.line_bot_api = LineBotApi(channel_access_token) if channel_access_token else None
    
    def send_message(
        self,
        to: str,  # LINE User ID
        message: LineMessage
    ) -> bool:
        """
        發送 LINE 訊息
        
        Args:
            to: LINE User ID
            message: LineMessage 值物件
        
        Returns:
            是否發送成功
        
        Raises:
            NotificationSendError: 發送失敗
        """
        if not self.channel_access_token:
            logger.warning(f"LINE 憑證未配置，跳過發送訊息到 {to}")
            return False
        
        # 實際環境使用 LINE SDK
        # try:
        #     self.line_bot_api.push_message(
        #         to,
        #         TextSendMessage(text=message.text)
        #     )
        #     logger.info(f"LINE 訊息已發送到 {to}")
        #     return True
        # except LineBotApiError as e:
        #     logger.error(f"LINE 發送失敗: {e}")
        #     raise NotificationSendError("LINE", to, str(e))
        
        # 開發環境：模擬發送
        logger.info(f"[MOCK] LINE 訊息發送到 {to}: {message.text[:50]}...")
        return True
    
    def send_push_message(
        self,
        to: str,
        text: str
    ) -> bool:
        """
        發送純文字訊息（快捷方法）
        
        Args:
            to: LINE User ID
            text: 訊息內容
        
        Returns:
            是否發送成功
        """
        message = LineMessage(text=text)
        return self.send_message(to, message)
    
    def verify_webhook_signature(
        self,
        body: str,
        signature: str,
        channel_secret: str
    ) -> bool:
        """
        驗證 Webhook 簽章
        
        Args:
            body: Request body
            signature: X-Line-Signature header
            channel_secret: LINE Channel Secret
        
        Returns:
            簽章是否有效
        """
        # 實際環境使用 LINE SDK
        # from linebot import WebhookParser
        # parser = WebhookParser(channel_secret)
        # try:
        #     parser.parse(body, signature)
        #     return True
        # except Exception:
        #     return False
        
        # 開發環境：總是返回 True
        return True

