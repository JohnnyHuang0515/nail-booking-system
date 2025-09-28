"""
LINE Webhook 中介軟體：處理多商家請求路由和上下文設定
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import json

from app.context import RequestContext
from app.line_signature import LineSignatureVerifier
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.database.session import get_db_session


class LineWebhookMiddleware(BaseHTTPMiddleware):
    """LINE Webhook 中介軟體"""
    
    def __init__(self, app, webhook_paths: list = None):
        super().__init__(app)
        self.webhook_paths = webhook_paths or ["/line/webhook", "/api/v1/line/webhook"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """處理請求"""
        # 清除之前的上下文
        RequestContext.clear_context()
        
        try:
            # 檢查是否為 LINE Webhook 請求
            if any(request.url.path.startswith(path) for path in self.webhook_paths):
                await self._handle_line_webhook(request)
            
            # 處理請求
            response = await call_next(request)
            return response
            
        except Exception as e:
            # 發生錯誤時清除上下文
            RequestContext.clear_context()
            raise e
        finally:
            # 確保請求結束後清除上下文
            RequestContext.clear_context()
    
    async def _handle_line_webhook(self, request: Request):
        """處理 LINE Webhook 請求"""
        # 取得簽名
        signature = request.headers.get("X-Line-Signature")
        if not signature:
            raise HTTPException(status_code=400, detail="缺少 X-Line-Signature 標頭")
        
        # 讀取請求主體
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="請求主體為空")
        
        # 嘗試解析 JSON
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="無效的 JSON 格式")
        
        # 驗證負載格式
        if not LineSignatureVerifier.validate_webhook_payload(payload):
            raise HTTPException(status_code=400, detail="無效的 Webhook 負載格式")
        
        # 從請求中提取商家資訊
        merchant = await self._identify_merchant(request, payload, body, signature)
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到對應的商家")
        
        # 設定請求上下文
        merchant_data = {
            "name": merchant.name,
            "timezone": merchant.timezone,
            "line_channel_id": merchant.line_channel_id
        }
        RequestContext.set_merchant_context(
            merchant_id=merchant.id,
            line_token=merchant.line_channel_access_token,
            merchant_data=merchant_data
        )
        
        # 將解析後的負載存儲到 request.state 供後續使用
        request.state.line_payload = payload
    
    async def _identify_merchant(self, request: Request, payload: dict, body: bytes, signature: str):
        """識別請求對應的商家"""
        # 方法1: 從 Header 中取得 Channel ID (如果代理伺服器有設定)
        channel_id = request.headers.get("X-Line-Channel-Id")
        
        # 方法2: 從請求參數中取得
        if not channel_id:
            channel_id = request.query_params.get("channel_id")
        
        # 方法3: 從事件中提取 (需要根據實際 LINE API 結構調整)
        if not channel_id:
            # 注意：實際的 LINE API 可能不直接在事件中包含 channel_id
            # 這裡需要根據實際情況調整
            pass
        
        if not channel_id:
            raise HTTPException(status_code=400, detail="無法識別 LINE Channel ID")
        
        # 查找商家
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            merchant = merchant_repo.find_by_channel_id(channel_id)
            
            if not merchant:
                raise HTTPException(status_code=404, detail=f"找不到 Channel ID: {channel_id} 對應的商家")
            
            # 驗證簽名
            try:
                LineSignatureVerifier.verify_signature(
                    merchant.line_channel_secret,
                    body,
                    signature
                )
            except ValueError as e:
                raise HTTPException(status_code=401, detail=f"簽名驗證失敗: {str(e)}")
            
            return merchant


class MultiTenantMiddleware(BaseHTTPMiddleware):
    """多租戶中介軟體：為一般 API 請求提供商家上下文"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """處理請求"""
        # 清除之前的上下文
        RequestContext.clear_context()
        
        try:
            # 檢查是否為需要商家上下文的 API 請求
            if self._requires_merchant_context(request):
                await self._handle_merchant_context(request)
            
            # 處理請求
            response = await call_next(request)
            return response
            
        except Exception as e:
            # 發生錯誤時清除上下文
            RequestContext.clear_context()
            raise e
        finally:
            # 確保請求結束後清除上下文
            RequestContext.clear_context()
    
    def _requires_merchant_context(self, request: Request) -> bool:
        """檢查請求是否需要商家上下文"""
        api_paths = ["/api/v1/services", "/api/v1/appointments", "/api/v1/transactions", "/api/v1/users"]
        return any(request.url.path.startswith(path) for path in api_paths)
    
    async def _handle_merchant_context(self, request: Request):
        """處理商家上下文"""
        # 從查詢參數中取得 merchant_id
        merchant_id_str = request.query_params.get("merchant_id")
        
        if not merchant_id_str:
            # 如果沒有 merchant_id，嘗試從 Header 中取得
            merchant_id_str = request.headers.get("X-Merchant-ID")
        
        if not merchant_id_str:
            raise HTTPException(status_code=400, detail="缺少 merchant_id 參數")
        
        try:
            from uuid import UUID
            merchant_id = UUID(merchant_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="無效的 merchant_id 格式")
        
        # 查找商家並設定上下文
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            merchant = merchant_repo.find_by_id(merchant_id)
            
            if not merchant:
                raise HTTPException(status_code=404, detail="找不到指定的商家")
            
            merchant_data = {
                "name": merchant.name,
                "timezone": merchant.timezone,
                "line_channel_id": merchant.line_channel_id
            }
            RequestContext.set_merchant_context(
                merchant_id=merchant.id,
                line_token=merchant.line_channel_access_token,
                merchant_data=merchant_data
            )
