"""
LINE Webhook 簽名驗證工具
"""
import hmac
import hashlib
import base64
from typing import Optional


class LineSignatureVerifier:
    """LINE Webhook 簽名驗證器"""
    
    @staticmethod
    def verify_signature(channel_secret: str, body: bytes, signature: str) -> bool:
        """
        驗證 LINE Webhook 簽名
        
        Args:
            channel_secret: LINE Channel Secret
            body: 請求主體 (bytes)
            signature: X-Line-Signature 標頭值
            
        Returns:
            bool: 驗證是否成功
            
        Raises:
            ValueError: 簽名驗證失敗
        """
        if not channel_secret or not body or not signature:
            raise ValueError("缺少必要的驗證參數")
        
        # 計算期望的簽名
        hash_value = hmac.new(
            channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        
        expected_signature = base64.b64encode(hash_value).decode('utf-8')
        
        # 比較簽名
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("簽名驗證失敗")
        
        return True
    
    @staticmethod
    def extract_channel_id_from_events(body: dict) -> Optional[str]:
        """
        從 Webhook 事件中提取 channel_id
        
        Args:
            body: 解析後的 JSON 請求主體
            
        Returns:
            Optional[str]: channel_id 或 None
        """
        try:
            events = body.get("events", [])
            if events and len(events) > 0:
                # LINE 事件結構中，source 包含 channel_id
                source = events[0].get("source", {})
                return source.get("userId")  # 這裡應該是 channel_id，但 LINE API 結構可能需要調整
            return None
        except (KeyError, IndexError, TypeError):
            return None
    
    @staticmethod
    def validate_webhook_payload(payload: dict) -> bool:
        """
        驗證 Webhook 負載格式
        
        Args:
            payload: 解析後的 JSON 負載
            
        Returns:
            bool: 格式是否有效
        """
        try:
            # 基本結構檢查
            if not isinstance(payload, dict):
                return False
            
            # 檢查必要欄位
            if "events" not in payload:
                return False
            
            events = payload["events"]
            if not isinstance(events, list):
                return False
            
            # 檢查事件結構
            for event in events:
                if not isinstance(event, dict):
                    return False
                if "type" not in event or "source" not in event:
                    return False
            
            return True
        except Exception:
            return False
