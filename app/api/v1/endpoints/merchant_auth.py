"""
商家後台認證 API - 支援 LINE Login 和 Email 登入
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import httpx

from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository

router = APIRouter()
security = HTTPBearer()


class MerchantInfo(BaseModel):
    """商家基本資訊"""
    id: str
    name: str
    merchant_code: str
    email: str
    is_active: bool


@router.get("/merchant-auth/merchant/{merchant_code}", response_model=MerchantInfo)
async def get_merchant_info(merchant_code: str, db_session = Depends(get_db_session)):
    """根據商家代碼獲取商家基本資訊（用於登入頁面顯示）"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_code(merchant_code)
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的商家"
            )
        
        if not merchant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家帳號已停用"
            )
        
        return MerchantInfo(
            id=str(merchant.id),
            name=merchant.name,
            merchant_code=merchant.merchant_code,
            email="merchant@example.com",  # 暫時使用固定 email
            is_active=merchant.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取商家資訊失敗: {str(e)}"
        )

# JWT 設定
MERCHANT_SECRET_KEY = os.getenv("MERCHANT_SECRET_KEY", "your-merchant-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class MerchantLoginRequest(BaseModel):
    """商家登入請求"""
    account: str
    password: str


class MerchantLineLoginRequest(BaseModel):
    """商家 LINE Login 請求"""
    code: str
    state: str  # 包含 merchant_id 的 state


class MerchantLoginResponse(BaseModel):
    """商家登入回應"""
    access_token: str
    token_type: str
    merchant: dict


class MerchantProfileResponse(BaseModel):
    """商家資料回應"""
    id: str
    name: str
    email: str
    line_channel_id: str
    liff_id: str
    timezone: str
    is_active: bool
    login_type: str  # 'email' 或 'line'

    class Config:
        from_attributes = True


def create_merchant_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """創建商家訪問令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, MERCHANT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_merchant_password(plain_password: str, hashed_password: str) -> bool:
    """驗證商家密碼"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_merchant_password_hash(password: str) -> str:
    """加密商家密碼"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def verify_line_login_code(code: str, merchant_id: str) -> Optional[dict]:
    """驗證 LINE Login code"""
    try:
        # 取得商家的 LINE Channel 資訊
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            merchant = merchant_repo.get_decrypted_merchant(UUID(merchant_id))
            
            if not merchant:
                return None
            
            # 使用 LINE Login API 驗證 code
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 交換 access token
                token_response = await client.post(
                    "https://api.line.me/oauth2/v2.1/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": f"https://your-domain.com/merchant-auth/line-callback",
                        "client_id": merchant["line_channel_id"],
                        "client_secret": merchant["line_channel_secret"]
                    }
                )
                
                if token_response.status_code != 200:
                    return None
                
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                
                # 取得用戶資料
                profile_response = await client.get(
                    "https://api.line.me/v2/profile",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if profile_response.status_code != 200:
                    return None
                
                profile_data = profile_response.json()
                
                return {
                    "line_user_id": profile_data.get("userId"),
                    "display_name": profile_data.get("displayName"),
                    "picture_url": profile_data.get("pictureUrl"),
                    "access_token": access_token
                }
                
    except Exception as e:
        print(f"LINE Login 驗證失敗: {str(e)}")
        return None


def get_current_merchant(credentials: HTTPAuthorizationCredentials = Depends(security), 
                        db_session = Depends(get_db_session)) -> dict:
    """取得當前商家"""
    try:
        payload = jwt.decode(credentials.credentials, MERCHANT_SECRET_KEY, algorithms=[ALGORITHM])
        merchant_id: str = payload.get("merchant_id")
        if merchant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 從資料庫查詢商家資料
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.get_decrypted_merchant(UUID(merchant_id))
        
        if not merchant or not merchant["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="商家不存在或已停用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return merchant
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/merchant-auth/login", response_model=MerchantLoginResponse)
async def merchant_login(request: MerchantLoginRequest, db_session = Depends(get_db_session)):
    """商家登入"""
    try:
        # 根據帳號查找商家
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_account(request.account)
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="帳號或密碼錯誤"
            )
        
        # 驗證密碼
        if not merchant.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="帳號未設置密碼，請聯繫管理員"
            )
        
        if not bcrypt.checkpw(request.password.encode('utf-8'), merchant.password_hash.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="帳號或密碼錯誤"
            )
        
        # 登入成功，創建 JWT token
        merchant_data = {
            "id": str(merchant.id),
            "name": merchant.name,
            "account": merchant.account,
            "merchant_code": merchant.merchant_code,
            "line_channel_id": merchant.line_channel_id,
            "liff_id": merchant.liff_id or "default-liff-id",
            "timezone": merchant.timezone,
            "is_active": merchant.is_active
        }
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_merchant_access_token(
            data={"merchant_id": merchant_data["id"], "login_type": "account"}, 
            expires_delta=access_token_expires
        )
        
        return MerchantLoginResponse(
            access_token=access_token,
            token_type="bearer",
            merchant=merchant_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登入失敗: {str(e)}"
        )


@router.post("/merchant-auth/line-login", response_model=MerchantLoginResponse)
async def merchant_line_login(request: MerchantLineLoginRequest, db_session = Depends(get_db_session)):
    """商家 LINE Login"""
    try:
        # 從 state 中取得 merchant_id
        # state 格式: "merchant_id:uuid"
        try:
            merchant_id = request.state.split(":")[1]
        except (IndexError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的 state 參數"
            )
        
        # 驗證 LINE Login code
        line_user_data = await verify_line_login_code(request.code, merchant_id)
        if not line_user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="LINE Login 驗證失敗"
            )
        
        # 取得商家資料
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.get_decrypted_merchant(UUID(merchant_id))
        
        if not merchant or not merchant["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="商家不存在或已停用"
            )
        
        # 創建訪問令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_merchant_access_token(
            data={
                "merchant_id": str(merchant["id"]), 
                "login_type": "line",
                "line_user_id": line_user_data["line_user_id"]
            }, 
            expires_delta=access_token_expires
        )
        
        merchant_response = {
            "id": str(merchant["id"]),
            "name": merchant["name"],
            "email": f"{merchant['name']}@line-login.com",  # LINE Login 沒有 email
            "line_channel_id": merchant["line_channel_id"],
            "liff_id": merchant["liff_id"],
            "timezone": merchant["timezone"],
            "is_active": merchant["is_active"],
            "login_type": "line",
            "line_user": {
                "display_name": line_user_data["display_name"],
                "picture_url": line_user_data["picture_url"]
            }
        }
        
        return MerchantLoginResponse(
            access_token=access_token,
            token_type="bearer",
            merchant=merchant_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LINE Login 失敗: {str(e)}"
        )


@router.get("/merchant-auth/profile", response_model=MerchantProfileResponse)
async def get_merchant_profile(current_merchant: dict = Depends(get_current_merchant)):
    """取得商家個人資料"""
    return MerchantProfileResponse(
        id=str(current_merchant["id"]),
        name=current_merchant["name"],
        email=current_merchant.get("email", ""),
        line_channel_id=current_merchant["line_channel_id"],
        liff_id=current_merchant["liff_id"],
        timezone=current_merchant["timezone"],
        is_active=current_merchant["is_active"],
        login_type="line"  # 需要從 token 中取得
    )


@router.get("/merchant-auth/line-login-url/{merchant_id}")
async def get_line_login_url(merchant_id: UUID, db_session = Depends(get_db_session)):
    """取得 LINE Login URL"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.get_decrypted_merchant(merchant_id)
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的商家"
            )
        
        # 構建 LINE Login URL
        state = f"merchant_login:{merchant_id}"
        line_login_url = (
            f"https://access.line.me/oauth2/v2.1/authorize?"
            f"response_type=code&"
            f"client_id={merchant['line_channel_id']}&"
            f"redirect_uri=http://localhost:3001/merchant-auth/line-callback&"
            f"state={state}&"
            f"scope=profile"
        )
        
        return {
            "line_login_url": line_login_url,
            "merchant_name": merchant["name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得 LINE Login URL 失敗: {str(e)}"
        )


@router.post("/merchant-auth/refresh-token")
async def refresh_merchant_token(current_merchant: dict = Depends(get_current_merchant)):
    """刷新商家訪問令牌"""
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_merchant_access_token(
            data={"merchant_id": str(current_merchant["id"])}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失敗: {str(e)}"
        )
