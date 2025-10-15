"""
Public API Router
公開 API（無需認證）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional

from booking.application.dtos import SlotResponse
from booking.application.services import BookingService
from booking.infrastructure.repositories.sqlalchemy_booking_repository import (
    SQLAlchemyBookingRepository
)
from booking.infrastructure.repositories.sqlalchemy_booking_lock_repository import (
    SQLAlchemyBookingLockRepository
)
from catalog.application.services import CatalogService
from catalog.infrastructure.repositories.sqlalchemy_service_repository import (
    SQLAlchemyServiceRepository
)
from catalog.infrastructure.repositories.sqlalchemy_staff_repository import (
    SQLAlchemyStaffRepository
)
from merchant.application.services import MerchantService
from merchant.infrastructure.repositories.sqlalchemy_merchant_repository import (
    SQLAlchemyMerchantRepository
)
from merchant.domain.exceptions import MerchantNotFoundError
from shared.database import get_db
from datetime import timezone, timedelta

TZ = timezone(timedelta(hours=8))  # Asia/Taipei


router = APIRouter(prefix="/public", tags=["Public"])


def get_merchant_service(db: Session = Depends(get_db)) -> MerchantService:
    """Dependency: 建立 MerchantService"""
    merchant_repo = SQLAlchemyMerchantRepository(db)
    return MerchantService(merchant_repo)


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    """Dependency: 建立 CatalogService"""
    from catalog.infrastructure.repositories.sqlalchemy_holiday_repository import SQLAlchemyHolidayRepository
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    holiday_repo = SQLAlchemyHolidayRepository(db)
    return CatalogService(service_repo, staff_repo, holiday_repo)


def get_booking_service_for_slots(db: Session = Depends(get_db)) -> BookingService:
    """Dependency: 建立 BookingService（用於時段查詢）"""
    from catalog.infrastructure.repositories.sqlalchemy_holiday_repository import SQLAlchemyHolidayRepository
    booking_repo = SQLAlchemyBookingRepository(db)
    booking_lock_repo = SQLAlchemyBookingLockRepository(db)
    
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    holiday_repo = SQLAlchemyHolidayRepository(db)
    catalog_service = CatalogService(service_repo, staff_repo, holiday_repo)
    
    return BookingService(booking_repo, booking_lock_repo, catalog_service)


@router.get("/merchants/{slug}")
async def get_merchant_info(
    slug: str,
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    取得商家公開資訊
    
    - **slug**: 商家 slug（URL 友好名稱）
    """
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
        
        return {
            "id": merchant.id,
            "slug": merchant.slug,
            "name": merchant.name,
            "status": merchant.status.value,
            "timezone": merchant.timezone,
            "address": merchant.address,
            "phone": merchant.phone
        }
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )


@router.get("/merchants/{slug}/categories")
async def get_merchant_categories(
    slug: str,
    merchant_service: MerchantService = Depends(get_merchant_service),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    取得商家使用的所有服務分類
    
    - **slug**: 商家 slug
    
    返回該商家所有服務使用的分類清單（去重）
    """
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )
    
    try:
        services = await catalog_service.list_services(merchant.id, is_active_only=False)
        
        # 收集所有分類（去重）
        categories = set()
        for service in services:
            if service.category:
                categories.add(service.category)
        
        return sorted(list(categories))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢分類失敗: {str(e)}"
        )


@router.get("/merchants/{slug}/services")
async def get_merchant_services(
    slug: str,
    merchant_service: MerchantService = Depends(get_merchant_service),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    取得商家的服務列表
    
    - **slug**: 商家 slug
    
    返回該商家的所有啟用服務
    """
    # 查詢商家
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )
    
    # 查詢服務列表
    try:
        services = await catalog_service.list_services(merchant.id, is_active_only=True)
        
        return [
            {
                "id": service.id,
                "merchant_id": service.merchant_id,
                "name": service.name,
                "description": service.description,
                "base_price": service.base_price.amount,
                "duration_minutes": service.base_duration.minutes,
                "is_active": service.is_active,
                "category": service.category
            }
            for service in services
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢服務失敗: {str(e)}"
        )


@router.get("/merchants/{slug}/staff")
async def get_merchant_staff(
    slug: str,
    merchant_service: MerchantService = Depends(get_merchant_service),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    取得商家的美甲師列表
    
    - **slug**: 商家 slug
    
    返回該商家的所有啟用美甲師
    """
    # 查詢商家
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )
    
    # 查詢美甲師列表
    try:
        staff_list = await catalog_service.list_staff(merchant.id, is_active_only=True)
        
        return [
            {
                "id": staff.id,
                "merchant_id": staff.merchant_id,
                "name": staff.name,
                "email": staff.email,
                "phone": staff.phone,
                "is_active": staff.is_active,
                "skills": staff.skills
            }
            for staff in staff_list
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢美甲師失敗: {str(e)}"
        )


@router.get("/merchants/{slug}/slots", response_model=list[SlotResponse])
async def get_available_slots(
    slug: str,
    target_date: date = Query(..., description="目標日期（YYYY-MM-DD）"),
    staff_id: Optional[int] = Query(None, description="員工 ID（可選）"),
    service_ids: list[int] = Query([], description="服務 ID 列表（可使用多個 service_ids 參數）"),
    merchant_service: MerchantService = Depends(get_merchant_service),
    booking_service: BookingService = Depends(get_booking_service_for_slots)
):
    """
    查詢可訂時段（核心功能！）⭐
    
    - **slug**: 商家 slug
    - **target_date**: 目標日期（YYYY-MM-DD）
    - **staff_id**: 指定員工（可選）
    - **service_ids**: 服務 ID 列表（可選，可使用多個 service_ids 參數，如 service_ids=1&service_ids=2）
    
    返回該日期的所有可用時段
    """
    # 查詢商家
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )
    
    # 計算服務總時長（從 service_ids 查詢）
    service_duration = 60  # 預設 60 分鐘
    if service_ids:
        try:
            from catalog.application.services import CatalogService
            from catalog.infrastructure.repositories.sqlalchemy_service_repository import SQLAlchemyServiceRepository
            from catalog.infrastructure.repositories.sqlalchemy_staff_repository import SQLAlchemyStaffRepository
            from shared.database import get_db
            
            # 獲取 catalog_service（這裡暫時使用簡化方式）
            total_duration = 0
            for sid in service_ids:
                # 簡化：假設每個服務 30 分鐘（實際應查詢資料庫）
                total_duration += 30
            service_duration = total_duration if total_duration > 0 else 60
        except Exception:
            service_duration = 60
    
    # 查詢可訂時段
    try:
        # 如果沒有指定員工，返回錯誤（因為 calculate_available_slots 需要 staff_id）
        if staff_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必須指定員工 ID (staff_id)"
            )
        
        slots = await booking_service.calculate_available_slots(
            merchant_id=merchant.id,
            staff_id=staff_id,
            target_date=target_date,
            service_duration_min=service_duration,
            interval_min=30
        )
        return slots
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢時段失敗: {str(e)}"
        )


@router.get("/merchants/{slug}/holidays")
async def get_merchant_holidays(
    slug: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    merchant_service: MerchantService = Depends(get_merchant_service),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    取得商家的休假日列表（公開 API）
    
    - **slug**: 商家 slug
    - **start_date**: 開始日期（可選）
    - **end_date**: 結束日期（可選）
    
    返回該商家的休假日列表
    """
    try:
        merchant = merchant_service.get_merchant_by_slug(slug)
    except MerchantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {slug}"
        )
    
    try:
        holidays = await catalog_service.list_holidays(merchant.id, start_date, end_date)
        
        return [
            {
                "id": h.id,
                "holiday_date": h.holiday_date.isoformat(),
                "name": h.name,
                "is_recurring": h.is_recurring
            }
            for h in holidays
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢休假日失敗: {str(e)}"
        )

