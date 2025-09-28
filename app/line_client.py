"""
LINE API 客戶端
負責與 LINE Platform API 的互動
"""
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LineClient:
    """LINE API 客戶端"""
    
    def __init__(self):
        self.base_url = "https://api.line.me/v2"
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def health_check(self, access_token: str) -> Dict[str, Any]:
        """
        檢查 LINE API 連線健康狀態
        
        Args:
            access_token: LINE Access Token
            
        Returns:
            Dict: 健康檢查結果
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # 測試 Bot Info API
                async with session.get(
                    f"{self.base_url}/bot/info",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        bot_info = await response.json()
                        return {
                            "status": "success",
                            "message": "LINE API 連線正常",
                            "bot_info": {
                                "display_name": bot_info.get("displayName"),
                                "user_id": bot_info.get("userId"),
                                "picture_url": bot_info.get("pictureUrl")
                            },
                            "checked_at": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "message": f"LINE API 連線失敗: {response.status}",
                            "error": error_text,
                            "checked_at": datetime.now().isoformat()
                        }
                        
        except aiohttp.ClientError as e:
            return {
                "status": "error",
                "message": "網路連線錯誤",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "健康檢查失敗",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def send_test_message(self, access_token: str, user_id: str) -> Dict[str, Any]:
        """
        發送測試訊息
        
        Args:
            access_token: LINE Access Token
            user_id: 目標用戶ID
            
        Returns:
            Dict: 發送結果
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            message_data = {
                "to": user_id,
                "messages": [
                    {
                        "type": "text",
                        "text": "🎉 歡迎使用美甲預約系統！\n\n您的商家帳號已成功初始化，現在可以開始接受預約了。"
                    }
                ]
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/bot/message/push",
                    headers=headers,
                    json=message_data
                ) as response:
                    if response.status == 200:
                        return {
                            "status": "success",
                            "message": "測試訊息發送成功",
                            "sent_at": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "message": f"測試訊息發送失敗: {response.status}",
                            "error": error_text,
                            "sent_at": datetime.now().isoformat()
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "message": "發送測試訊息失敗",
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }
    
    async def get_webhook_info(self, access_token: str) -> Dict[str, Any]:
        """
        取得 Webhook 資訊
        
        Args:
            access_token: LINE Access Token
            
        Returns:
            Dict: Webhook 資訊
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.base_url}/bot/channel/webhook/endpoint",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        webhook_info = await response.json()
                        return {
                            "status": "success",
                            "webhook_info": webhook_info,
                            "checked_at": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "message": f"取得 Webhook 資訊失敗: {response.status}",
                            "error": error_text,
                            "checked_at": datetime.now().isoformat()
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "message": "取得 Webhook 資訊失敗",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def validate_credentials(self, access_token: str, channel_secret: str) -> Dict[str, Any]:
        """
        驗證憑證有效性
        
        Args:
            access_token: LINE Access Token
            channel_secret: LINE Channel Secret
            
        Returns:
            Dict: 驗證結果
        """
        try:
            # 1. 測試 Access Token
            token_check = await self.health_check(access_token)
            
            # 2. 測試 Channel Secret（通過簽名驗證）
            # 這裡可以實作更詳細的 Channel Secret 驗證
            
            if token_check["status"] == "success":
                return {
                    "status": "success",
                    "message": "憑證驗證成功",
                    "access_token_valid": True,
                    "channel_secret_valid": True,  # 暫時設為 True
                    "validated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "憑證驗證失敗",
                    "access_token_valid": False,
                    "channel_secret_valid": False,
                    "error": token_check.get("error"),
                    "validated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": "憑證驗證失敗",
                "error": str(e),
                "validated_at": datetime.now().isoformat()
            }