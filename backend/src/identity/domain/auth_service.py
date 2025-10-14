"""
Identity Context - Domain Layer - Auth Service (值服務)
密碼雜湊與 JWT Token 處理
"""
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from shared.config import settings


class PasswordService:
    """密碼服務（值服務）"""
    
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        """雜湊密碼"""
        return cls._pwd_context.hash(plain_password)
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        return cls._pwd_context.verify(plain_password, hashed_password)


class TokenService:
    """JWT Token 服務（值服務）"""
    
    @classmethod
    def create_access_token(
        cls,
        user_id: str,
        merchant_id: Optional[str] = None,
        role: str = "customer",
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        建立 Access Token
        
        Args:
            user_id: 用戶 ID
            merchant_id: 商家 ID（租戶邊界）
            role: 角色
            expires_delta: 過期時間（預設從設定讀取）
        
        Returns:
            JWT token 字串
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
        
        expire = datetime.now(dt_timezone.utc) + expires_delta
        
        to_encode = {
            "sub": user_id,  # Subject: 用戶 ID
            "merchant_id": merchant_id,
            "role": role,
            "exp": expire,
            "iat": datetime.now(dt_timezone.utc),  # Issued At
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        解碼並驗證 Token
        
        Args:
            token: JWT token
        
        Returns:
            Token payload
        
        Raises:
            JWTError: Token 無效或過期
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise JWTError(f"Token 驗證失敗: {str(e)}")
    
    @classmethod
    def get_user_id_from_token(cls, token: str) -> Optional[str]:
        """從 Token 提取用戶 ID"""
        try:
            payload = cls.decode_token(token)
            return payload.get("sub")
        except JWTError:
            return None
    
    @classmethod
    def get_merchant_id_from_token(cls, token: str) -> Optional[str]:
        """從 Token 提取商家 ID"""
        try:
            payload = cls.decode_token(token)
            return payload.get("merchant_id")
        except JWTError:
            return None

