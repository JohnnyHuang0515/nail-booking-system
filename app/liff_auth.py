"""
LIFF 身分驗證和 LINE 用戶身分對應
"""
import httpx
import json
from typing import Optional, Dict, Any
from uuid import UUID
import jwt
from jwt.exceptions import InvalidTokenError
import logging

from app.context import RequestContext
from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository

logger = logging.getLogger(__name__)


class LIFFAuthManager:
    """LIFF 身分驗證管理器"""
    
    def __init__(self):
        self.line_verify_url = "https://api.line.me/oauth2/v2.1/verify"
        self.line_profile_url = "https://api.line.me/v2/profile"
    
    async def verify_id_token(self, id_token: str, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        驗證 LIFF idToken
        
        Args:
            id_token: LIFF idToken
            channel_id: LINE Channel ID
            
        Returns:
            Optional[Dict]: 驗證成功返回用戶資訊，失敗返回 None
        """
        try:
            # 使用 LINE Verify API 驗證 idToken
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.line_verify_url,
                    params={
                        "id_token": id_token,
                        "client_id": channel_id
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"LIFF token 驗證失敗: {response.status_code} - {response.text}")
                    return None
                
                # 解析回應
                token_data = response.json()
                
                # 驗證 token 結構
                if not self._validate_token_data(token_data):
                    logger.error("無效的 token 資料結構")
                    return None
                
                return token_data
                
        except httpx.TimeoutException:
            logger.error("LIFF token 驗證超時")
            return None
        except Exception as e:
            logger.error(f"LIFF token 驗證異常: {str(e)}")
            return None
    
    def _validate_token_data(self, token_data: Dict[str, Any]) -> bool:
        """驗證 token 資料結構"""
        required_fields = ["sub", "aud", "exp", "iat"]
        return all(field in token_data for field in required_fields)
    
    async def get_line_user_profile(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        取得 LINE 用戶資料
        
        Args:
            access_token: LINE Access Token
            
        Returns:
            Optional[Dict]: 用戶資料或 None
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(self.line_profile_url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"取得 LINE 用戶資料失敗: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"取得 LINE 用戶資料異常: {str(e)}")
            return None
    
    async def authenticate_user(
        self, 
        id_token: str, 
        merchant_id: UUID,
        access_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        完整的用戶身分驗證流程
        
        Args:
            id_token: LIFF idToken
            merchant_id: 商家ID
            access_token: 可選的 Access Token（用於取得詳細資料）
            
        Returns:
            Optional[Dict]: 驗證成功返回用戶資訊，失敗返回 None
        """
        try:
            # 1. 取得商家資訊
            with get_db_session() as db_session:
                merchant_repo = SQLMerchantRepository(db_session)
                merchant = merchant_repo.find_by_id(merchant_id)
                
                if not merchant:
                    logger.error(f"找不到商家: {merchant_id}")
                    return None
                
                # 2. 驗證 idToken
                token_data = await self.verify_id_token(id_token, merchant.line_channel_id)
                if not token_data:
                    return None
                
                # 3. 取得或創建用戶
                user_repo = SQLUserRepository(db_session)
                line_user_id = token_data.get("sub")
                
                if not line_user_id:
                    logger.error("idToken 中缺少用戶ID")
                    return None
                
                # 4. 取得或創建用戶記錄
                user = user_repo.get_or_create_by_line_user_id(merchant_id, line_user_id)
                
                # 5. 如果有 access_token，取得詳細用戶資料
                if access_token:
                    profile_data = await self.get_line_user_profile(access_token)
                    if profile_data:
                        # 更新用戶資料
                        user.name = profile_data.get("displayName", user.name)
                        db_session.commit()
                
                return {
                    "user_id": str(user.id),
                    "line_user_id": user.line_user_id,
                    "name": user.name,
                    "phone": user.phone,
                    "merchant_id": str(merchant_id),
                    "merchant_name": merchant.name,
                    "token_data": token_data
                }
                
        except Exception as e:
            logger.error(f"用戶身分驗證異常: {str(e)}")
            return None


class LIFFSecurityMiddleware:
    """LIFF 安全中介軟體"""
    
    def __init__(self):
        self.auth_manager = LIFFAuthManager()
    
    async def verify_request(
        self, 
        id_token: str, 
        merchant_id: UUID,
        access_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        驗證 LIFF 請求
        
        Args:
            id_token: LIFF idToken
            merchant_id: 商家ID
            access_token: 可選的 Access Token
            
        Returns:
            Optional[Dict]: 驗證結果
        """
        try:
            # 執行完整驗證流程
            auth_result = await self.auth_manager.authenticate_user(
                id_token, merchant_id, access_token
            )
            
            if not auth_result:
                return None
            
            # 設定請求上下文
            RequestContext.set_merchant_context(
                merchant_id=UUID(auth_result["merchant_id"]),
                line_token=None,  # LIFF 請求不需要 LINE Bot token
                merchant_data={
                    "name": auth_result["merchant_name"],
                    "user_id": auth_result["user_id"],
                    "line_user_id": auth_result["line_user_id"]
                }
            )
            
            return auth_result
            
        except Exception as e:
            logger.error(f"LIFF 請求驗證異常: {str(e)}")
            return None


# 全域實例
liff_auth_manager = LIFFAuthManager()
liff_security_middleware = LIFFSecurityMiddleware()


# 使用範例和測試函數
async def test_liff_auth():
    """測試 LIFF 驗證功能"""
    test_id_token = "test_id_token"
    test_merchant_id = UUID("12345678-1234-1234-1234-123456789012")
    
    # 測試驗證
    result = await liff_auth_manager.authenticate_user(test_id_token, test_merchant_id)
    
    if result:
        print("LIFF 驗證成功:")
        print(f"  用戶ID: {result['user_id']}")
        print(f"  商家ID: {result['merchant_id']}")
        print(f"  用戶名稱: {result['name']}")
    else:
        print("LIFF 驗證失敗")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_liff_auth())
