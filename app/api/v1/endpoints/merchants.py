"""
商家管理 API：平台管理多商家
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.database.session import get_db_session
from app.services.merchant_initialization_service import MerchantInitializationService
from app.line_client import LineClient

router = APIRouter()


class MerchantCreate(BaseModel):
    """創建商家請求"""
    name: str
    line_channel_id: str
    line_channel_secret: str
    line_channel_access_token: str
    liff_id: Optional[str] = None
    timezone: str = 'Asia/Taipei'
    contact_info: Optional[dict] = None


class MerchantUpdate(BaseModel):
    """更新商家請求"""
    name: Optional[str] = None
    line_channel_secret: Optional[str] = None
    line_channel_access_token: Optional[str] = None
    liff_id: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class MerchantResponse(BaseModel):
    """商家回應"""
    id: UUID
    name: str
    line_channel_id: str
    liff_id: Optional[str] = None
    timezone: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class MerchantCredentialsUpdate(BaseModel):
    """商家憑證更新請求"""
    line_channel_secret: Optional[str] = None
    line_channel_access_token: Optional[str] = None


@router.post("/merchants", response_model=MerchantResponse)
async def create_merchant(
    merchant_data: MerchantCreate,
    db_session = Depends(get_db_session)
):
    """創建新商家（完整初始化）"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        
        # 檢查 Channel ID 是否已存在
        existing_merchant = merchant_repo.find_by_channel_id(merchant_data.line_channel_id)
        if existing_merchant:
            raise HTTPException(status_code=400, detail="LINE Channel ID 已存在")
        
        # 驗證 LINE 憑證
        line_client = LineClient()
        validation_result = await line_client.validate_credentials(
            access_token=merchant_data.line_channel_access_token,
            channel_secret=merchant_data.line_channel_secret
        )
        
        if validation_result["status"] != "success":
            raise HTTPException(
                status_code=400, 
                detail=f"LINE 憑證驗證失敗: {validation_result.get('message', '未知錯誤')}"
            )
        
        # 使用初始化服務創建商家
        init_service = MerchantInitializationService(db_session)
        result = await init_service.initialize_merchant(
            name=merchant_data.name,
            line_channel_id=merchant_data.line_channel_id,
            line_channel_secret=merchant_data.line_channel_secret,
            line_channel_access_token=merchant_data.line_channel_access_token,
            liff_id=merchant_data.liff_id,
            timezone=merchant_data.timezone,
            contact_info=merchant_data.contact_info
        )
        
        # 取得創建的商家資料
        merchant = merchant_repo.find_by_id(UUID(result["merchant_id"]))
        
        return MerchantResponse(
            id=merchant.id,
            name=merchant.name,
            line_channel_id=merchant.line_channel_id,
            liff_id=merchant.liff_id,
            timezone=merchant.timezone,
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"創建商家失敗: {str(e)}")


@router.get("/merchants", response_model=List[MerchantResponse])
async def list_merchants(
    active_only: bool = True,
    db_session = Depends(get_db_session)
):
    """列出所有商家"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        
        if active_only:
            merchants = merchant_repo.list_active()
        else:
            # 如果需要列出所有商家（包括非活躍），需要實作相應方法
            merchants = merchant_repo.list_active()
        
        return [
            MerchantResponse(
                id=merchant.id,
                name=merchant.name,
                line_channel_id=merchant.line_channel_id,
                timezone=merchant.timezone or 'Asia/Taipei',  # 提供預設值
                is_active=merchant.is_active,
                created_at=merchant.created_at.isoformat()
            )
            for merchant in merchants
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得商家列表失敗: {str(e)}")


@router.get("/merchants/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得指定商家資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        return MerchantResponse(
            id=merchant.id,
            name=merchant.name,
            line_channel_id=merchant.line_channel_id,
            liff_id=merchant.liff_id,
            timezone=merchant.timezone or 'Asia/Taipei',  # 提供預設值
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得商家資料失敗: {str(e)}")


@router.put("/merchants/{merchant_id}", response_model=MerchantResponse)
async def update_merchant(
    merchant_id: UUID,
    merchant_data: MerchantUpdate,
    db_session = Depends(get_db_session)
):
    """更新商家資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        # 更新資料
        if merchant_data.name is not None:
            merchant.name = merchant_data.name
        if merchant_data.timezone is not None:
            merchant.timezone = merchant_data.timezone
        if merchant_data.is_active is not None:
            merchant.is_active = merchant_data.is_active
        
        # 更新憑證（如果提供）
        if merchant_data.line_channel_secret or merchant_data.line_channel_access_token:
            updated_merchant = merchant_repo.update_credentials(
                merchant_id=merchant_id,
                line_channel_secret=merchant_data.line_channel_secret,
                line_channel_access_token=merchant_data.line_channel_access_token
            )
            if updated_merchant:
                merchant = updated_merchant
        
        db_session.commit()
        db_session.refresh(merchant)
        
        return MerchantResponse(
            id=merchant.id,
            name=merchant.name,
            line_channel_id=merchant.line_channel_id,
            liff_id=merchant.liff_id,
            timezone=merchant.timezone,
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"更新商家資料失敗: {str(e)}")


@router.put("/merchants/{merchant_id}/credentials")
async def update_merchant_credentials(
    merchant_id: UUID,
    credentials: MerchantCredentialsUpdate,
    db_session = Depends(get_db_session)
):
    """更新商家 LINE 憑證"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        updated_merchant = merchant_repo.update_credentials(
            merchant_id=merchant_id,
            line_channel_secret=credentials.line_channel_secret,
            line_channel_access_token=credentials.line_channel_access_token
        )
        
        if not updated_merchant:
            raise HTTPException(status_code=500, detail="更新憑證失敗")
        
        db_session.commit()
        
        return {"status": "success", "message": "憑證更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"更新憑證失敗: {str(e)}")


@router.post("/merchants/{merchant_id}/rotate-token")
async def rotate_merchant_token(
    merchant_id: UUID,
    new_token: str,
    new_secret: Optional[str] = None,
    db_session = Depends(get_db_session)
):
    """輪替商家憑證並進行健康檢查"""
    try:
        init_service = MerchantInitializationService(db_session)
        result = await init_service.rotate_credentials(
            merchant_id=merchant_id,
            new_access_token=new_token,
            new_secret=new_secret
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"憑證輪替失敗: {str(e)}")


@router.post("/merchants/{merchant_id}/toggle-status")
async def toggle_merchant_status(
    merchant_id: UUID,
    is_active: bool,
    db_session = Depends(get_db_session)
):
    """切換商家狀態（啟用/停用）"""
    try:
        init_service = MerchantInitializationService(db_session)
        result = await init_service.toggle_merchant_status(
            merchant_id=merchant_id,
            is_active=is_active
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切換商家狀態失敗: {str(e)}")


@router.delete("/merchants/{merchant_id}")
async def deactivate_merchant(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """停用商家（軟刪除）"""
    try:
        init_service = MerchantInitializationService(db_session)
        result = await init_service.toggle_merchant_status(
            merchant_id=merchant_id,
            is_active=False
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停用商家失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/stats")
async def get_merchant_stats(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得商家統計資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        # 這裡可以添加統計資料查詢
        # 例如：用戶數量、預約數量、交易金額等
        
        return {
            "merchant_id": str(merchant_id),
            "name": merchant.name,
            "status": "active" if merchant.is_active else "inactive",
            "stats": {
                "total_users": 0,  # 待實作
                "total_appointments": 0,  # 待實作
                "total_revenue": 0.0  # 待實作
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得統計資料失敗: {str(e)}")
