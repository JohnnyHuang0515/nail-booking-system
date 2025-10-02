"""
商家上下文 API：為 LIFF 應用提供商家資訊
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid

from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.liff_auth import liff_security_middleware

router = APIRouter()


class LIFFLoginRequest(BaseModel):
    """LIFF 登入請求"""
    id_token: str
    access_token: Optional[str] = None


class MerchantContextResponse(BaseModel):
    """商家上下文回應"""
    merchant_id: str
    merchant_name: str
    liff_id: str
    timezone: str
    is_active: bool


@router.post("/merchant-context/liff-login", response_model=MerchantContextResponse)
async def liff_login_for_merchant_context(
    request: LIFFLoginRequest,
    db_session = Depends(get_db_session)
):
    """
    LIFF 登入並獲取商家上下文
    這個端點用於前端初始化時獲取商家資訊
    """
    try:
        # 從 URL 參數或 Header 中獲取 merchant_id
        # 在實際部署時，merchant_id 應該從 LIFF 的 context 中獲取
        # 這裡我們先使用查詢參數的方式
        
        # 暫時使用測試商家 ID，實際應該從 LIFF context 獲取
        merchant_id_str = '5a89c20e-befd-4bb3-a43b-e185ab0e4841'
        
        try:
            merchant_id = uuid.UUID(merchant_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="無效的商家ID格式")
        
        # 驗證 LIFF token 和取得用戶資訊
        auth_result = await liff_security_middleware.verify_request(
            id_token=request.id_token,
            merchant_id=merchant_id,
            access_token=request.access_token
        )
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="LIFF 驗證失敗")
        
        # 取得商家資訊
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        return MerchantContextResponse(
            merchant_id=str(merchant.id),
            merchant_name=merchant.name,
            liff_id=merchant.liff_id or '',
            timezone=merchant.timezone,
            is_active=merchant.is_active
        )
        
    except Exception as e:
        print(f"LIFF 登入錯誤: {e}")
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")


@router.get("/merchant-context/{merchant_id}", response_model=MerchantContextResponse)
async def get_merchant_context(
    merchant_id: str,
    db_session = Depends(get_db_session)
):
    """
    根據商家 ID 獲取商家上下文資訊
    用於非 LIFF 環境或開發測試
    """
    try:
        merchant_uuid = uuid.UUID(merchant_id)
        
        # 取得商家資訊
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_uuid)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        return MerchantContextResponse(
            merchant_id=str(merchant.id),
            merchant_name=merchant.name,
            liff_id=merchant.liff_id or '',
            timezone=merchant.timezone,
            is_active=merchant.is_active
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的商家ID格式")
    except Exception as e:
        print(f"獲取商家上下文錯誤: {e}")
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")
