"""
商家設定管理 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.infrastructure.database.session import get_db_session
from app.services.merchant_settings_service import MerchantSettingsService

router = APIRouter()


class BasicSettingsUpdate(BaseModel):
    """基本設定更新請求"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    brand_icon: Optional[str] = None
    ig_link: Optional[str] = None
    timezone: Optional[str] = None


class BusinessRulesUpdate(BaseModel):
    """營業規則更新請求"""
    booking_advance_hours: Optional[int] = None
    cancellation_hours: Optional[int] = None
    no_show_penalty: Optional[bool] = None
    max_advance_days: Optional[int] = None


class LiffSettingsUpdate(BaseModel):
    """LIFF 設定更新請求"""
    liff_id: str


class RichMenuPublishRequest(BaseModel):
    """Rich Menu 發布請求"""
    rich_menu_id: Optional[str] = None


class RichMenuRollbackRequest(BaseModel):
    """Rich Menu 回滾請求"""
    previous_rich_menu_id: str


class ServiceTemplateApplyRequest(BaseModel):
    """服務項目範本套用請求"""
    template_id: str


@router.get("/merchants/{merchant_id}/settings/basic")
async def get_basic_settings(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得商家基本設定"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.get_basic_settings(merchant_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得基本設定失敗: {str(e)}")


@router.put("/merchants/{merchant_id}/settings/basic")
async def update_basic_settings(
    merchant_id: UUID,
    settings: BasicSettingsUpdate,
    db_session = Depends(get_db_session)
):
    """更新商家基本設定"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.update_basic_settings(
            merchant_id=merchant_id,
            name=settings.name,
            address=settings.address,
            phone=settings.phone,
            brand_icon=settings.brand_icon,
            ig_link=settings.ig_link,
            timezone=settings.timezone
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新基本設定失敗: {str(e)}")


@router.put("/merchants/{merchant_id}/settings/business-rules")
async def update_business_rules(
    merchant_id: UUID,
    rules: BusinessRulesUpdate,
    db_session = Depends(get_db_session)
):
    """更新營業規則"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.update_business_rules(
            merchant_id=merchant_id,
            booking_advance_hours=rules.booking_advance_hours,
            cancellation_hours=rules.cancellation_hours,
            no_show_penalty=rules.no_show_penalty,
            max_advance_days=rules.max_advance_days
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新營業規則失敗: {str(e)}")


@router.put("/merchants/{merchant_id}/settings/liff")
async def update_liff_settings(
    merchant_id: UUID,
    settings: LiffSettingsUpdate,
    db_session = Depends(get_db_session)
):
    """更新 LIFF 設定"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.update_liff_settings(
            merchant_id=merchant_id,
            liff_id=settings.liff_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新 LIFF 設定失敗: {str(e)}")


@router.post("/merchants/{merchant_id}/rich-menu/publish")
async def publish_rich_menu(
    merchant_id: UUID,
    request: RichMenuPublishRequest,
    db_session = Depends(get_db_session)
):
    """發布 Rich Menu"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.publish_rich_menu(
            merchant_id=merchant_id,
            rich_menu_id=request.rich_menu_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發布 Rich Menu 失敗: {str(e)}")


@router.post("/merchants/{merchant_id}/rich-menu/rollback")
async def rollback_rich_menu(
    merchant_id: UUID,
    request: RichMenuRollbackRequest,
    db_session = Depends(get_db_session)
):
    """回滾 Rich Menu"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.rollback_rich_menu(
            merchant_id=merchant_id,
            previous_rich_menu_id=request.previous_rich_menu_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回滾 Rich Menu 失敗: {str(e)}")


@router.get("/templates")
async def get_template_library(db_session = Depends(get_db_session)):
    """取得範本庫"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.get_template_library()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得範本庫失敗: {str(e)}")


@router.post("/merchants/{merchant_id}/templates/services/apply")
async def apply_service_template(
    merchant_id: UUID,
    request: ServiceTemplateApplyRequest,
    db_session = Depends(get_db_session)
):
    """套用服務項目範本"""
    try:
        settings_service = MerchantSettingsService(db_session)
        result = await settings_service.apply_service_template(
            merchant_id=merchant_id,
            template_id=request.template_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"套用服務項目範本失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/settings")
async def get_merchant_settings(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得商家設定"""
    try:
        settings_service = MerchantSettingsService(db_session)
        
        # 這裡可以實作取得商家所有設定的邏輯
        # 包括基本設定、營業規則、LIFF 設定、Rich Menu 狀態等
        
        return {
            "status": "success",
            "merchant_id": str(merchant_id),
            "settings": {
                "basic": {
                    "name": "商家名稱",
                    "address": "商家地址",
                    "phone": "聯絡電話",
                    "brand_icon": "品牌圖示URL",
                    "ig_link": "Instagram連結",
                    "timezone": "Asia/Taipei"
                },
                "business_rules": {
                    "booking_advance_hours": 24,
                    "cancellation_hours": 24,
                    "no_show_penalty": True,
                    "max_advance_days": 30
                },
                "liff": {
                    "liff_id": "liff-1234567890",
                    "status": "active"
                },
                "rich_menu": {
                    "current_id": "richmenu-1234567890",
                    "status": "published"
                }
            },
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得商家設定失敗: {str(e)}")
