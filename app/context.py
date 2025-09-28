"""
請求上下文管理：多商家架構下的 merchant_id 和 LINE token 管理
"""
from contextvars import ContextVar
from typing import Optional, Dict, Any
from uuid import UUID

# 全域請求上下文變數
merchant_id_ctx: ContextVar[Optional[UUID]] = ContextVar("merchant_id", default=None)
line_token_ctx: ContextVar[Optional[str]] = ContextVar("line_token", default=None)
merchant_data_ctx: ContextVar[Optional[Dict[str, Any]]] = ContextVar("merchant_data", default=None)


class RequestContext:
    """請求上下文管理器"""
    
    @staticmethod
    def set_merchant_context(merchant_id: UUID, line_token: str, merchant_data: Dict[str, Any] = None):
        """設定當前請求的商家上下文"""
        merchant_id_ctx.set(merchant_id)
        line_token_ctx.set(line_token)
        merchant_data_ctx.set(merchant_data or {})
    
    @staticmethod
    def get_merchant_id() -> Optional[UUID]:
        """取得當前請求的商家ID"""
        return merchant_id_ctx.get()
    
    @staticmethod
    def get_line_token() -> Optional[str]:
        """取得當前請求的 LINE token"""
        return line_token_ctx.get()
    
    @staticmethod
    def get_merchant_data() -> Optional[Dict[str, Any]]:
        """取得當前請求的商家資料"""
        return merchant_data_ctx.get()
    
    @staticmethod
    def clear_context():
        """清除當前請求上下文"""
        merchant_id_ctx.set(None)
        line_token_ctx.set(None)
        merchant_data_ctx.set(None)
    
    @staticmethod
    def require_merchant_id() -> UUID:
        """要求必須有商家ID，否則拋出異常"""
        merchant_id = merchant_id_ctx.get()
        if merchant_id is None:
            raise ValueError("商家ID未設定，請確保在正確的請求上下文中")
        return merchant_id
    
    @staticmethod
    def require_line_token() -> str:
        """要求必須有 LINE token，否則拋出異常"""
        line_token = line_token_ctx.get()
        if line_token is None:
            raise ValueError("LINE token 未設定，請確保在正確的請求上下文中")
        return line_token
