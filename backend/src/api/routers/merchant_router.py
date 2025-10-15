"""
Merchant API Router
商家端 API（需要認證，scope=merchant）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

from booking.application.dtos import BookingResponse
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
from shared.database import get_db
from identity.infrastructure.dependencies import get_current_user
from identity.domain.models import User

router = APIRouter(prefix="/merchant", tags=["Merchant"])


# ========== DTOs ==========
class CreateStaffRequest(BaseModel):
    """新增員工請求"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[int]] = None
    is_active: bool = True


class UpdateStaffRequest(BaseModel):
    """更新員工請求"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[int]] = None
    is_active: Optional[bool] = None


class CreateHolidayRequest(BaseModel):
    """新增休假日請求"""
    holiday_date: date
    name: str
    is_recurring: bool = False


class UpdateHolidayRequest(BaseModel):
    """更新休假日請求"""
    holiday_date: Optional[date] = None
    name: Optional[str] = None
    is_recurring: Optional[bool] = None


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    """Dependency: 建立 CatalogService"""
    from catalog.infrastructure.repositories.sqlalchemy_holiday_repository import SQLAlchemyHolidayRepository
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    holiday_repo = SQLAlchemyHolidayRepository(db)
    return CatalogService(service_repo, staff_repo, holiday_repo)


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """Dependency: 建立 BookingService"""
    from catalog.infrastructure.repositories.sqlalchemy_holiday_repository import SQLAlchemyHolidayRepository
    booking_repo = SQLAlchemyBookingRepository(db)
    booking_lock_repo = SQLAlchemyBookingLockRepository(db)
    
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    holiday_repo = SQLAlchemyHolidayRepository(db)
    catalog_service = CatalogService(service_repo, staff_repo, holiday_repo)
    
    return BookingService(booking_repo, booking_lock_repo, catalog_service)


@router.get("/bookings")
async def list_bookings(
    start_date: Optional[date] = Query(None, description="開始日期"),
    end_date: Optional[date] = Query(None, description="結束日期"),
    staff_id: Optional[int] = Query(None, description="員工 ID"),
    status: Optional[str] = Query(None, description="預約狀態"),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    查詢商家預約列表
    
    - **start_date**: 開始日期（可選）
    - **end_date**: 結束日期（可選）
    - **staff_id**: 員工ID篩選（可選）
    - **status**: 狀態篩選（可選）
    """
    # 從 current_user 取得 merchant_id
    merchant_id = current_user.merchant_id
    if not merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無法取得商家資訊"
        )
    
    # 查詢預約列表
    from booking.domain.models import BookingStatus
    status_enum = BookingStatus(status) if status else None
    
    bookings = await booking_service.list_bookings(
        merchant_id=merchant_id,
        start_date=start_date,
        end_date=end_date,
        status=status_enum
    )
    
    # 如果有staff_id篩選，過濾結果
    if staff_id:
        bookings = [b for b in bookings if b.staff_id == staff_id]
    
    # 轉換為JSON可序列化格式
    result = []
    for booking in bookings:
        time_slot = booking.time_slot()
        result.append({
            "id": str(booking.id),
            "merchant_id": booking.merchant_id,
            "customer": booking.customer,
            "staff_id": booking.staff_id,
            "start_at": time_slot.start_at.isoformat(),
            "end_at": time_slot.end_at.isoformat(),
            "status": booking.status.value,
            "total_price": float(booking.total_price().amount),
            "total_duration": booking.total_duration().minutes,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "items": [
                {
                    "service_id": item.service_id,
                    "service_name": item.service_name,
                    "service_price": float(item.service_price.amount),
                    "service_duration": item.service_duration.minutes,
                    "option_ids": item.option_ids,
                    "option_names": item.option_names,
                }
                for item in booking.items
            ]
        })
    
    return result


@router.get("/services")
async def list_services(
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    查詢商家服務列表
    
    返回該商家的所有服務（包含已停用的）
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        services = await catalog_service.list_services(merchant_id, is_active_only=False)
        
        return [
            {
                "id": service.id,
                "merchant_id": service.merchant_id,
                "name": service.name,
                "description": service.description,
                "base_price": service.base_price.amount,
                "duration_minutes": service.base_duration.minutes,
                "is_active": service.is_active,
                "category": service.category,
                "allow_stack": service.allow_stack
            }
            for service in services
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢服務失敗: {str(e)}"
        )


@router.get("/staff")
async def list_staff(
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    查詢商家員工列表
    
    返回該商家的所有員工（包含已停用的）
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        staff_list = await catalog_service.list_staff(merchant_id, is_active_only=False)
        
        return [
            {
                "id": staff.id,
                "merchant_id": staff.merchant_id,
                "name": staff.name,
                "email": staff.email,
                "phone": staff.phone,
                "is_active": staff.is_active,
                "skills": staff.skills,
                "working_hours": [
                    {
                        "day_of_week": wh.day_of_week.name,
                        "start_time": wh.start_time.strftime("%H:%M"),
                        "end_time": wh.end_time.strftime("%H:%M")
                    }
                    for wh in staff.working_hours
                ]
            }
            for staff in staff_list
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢員工失敗: {str(e)}"
        )


@router.post("/staff", status_code=status.HTTP_201_CREATED)
async def create_staff(
    request: CreateStaffRequest,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    新增員工
    
    - **name**: 員工姓名（必填）
    - **email**: Email（可選）
    - **phone**: 電話（可選）
    - **skills**: 技能服務ID列表（可選）
    - **is_active**: 是否啟用（預設 True）
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        staff = await catalog_service.create_staff(
            merchant_id=merchant_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            skills=request.skills,
            is_active=request.is_active
        )
        
        return {
            "id": staff.id,
            "merchant_id": staff.merchant_id,
            "name": staff.name,
            "email": staff.email,
            "phone": staff.phone,
            "is_active": staff.is_active,
            "skills": staff.skills,
            "working_hours": [
                {
                    "day_of_week": wh.day_of_week.name,
                    "start_time": wh.start_time.strftime("%H:%M"),
                    "end_time": wh.end_time.strftime("%H:%M")
                }
                for wh in staff.working_hours
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"新增員工失敗: {str(e)}"
        )


@router.put("/staff/{staff_id}")
async def update_staff(
    staff_id: int,
    request: UpdateStaffRequest,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    更新員工資訊
    
    - **staff_id**: 員工 ID
    - **name**: 員工姓名（可選）
    - **email**: Email（可選）
    - **phone**: 電話（可選）
    - **skills**: 技能服務ID列表（可選）
    - **is_active**: 是否啟用（可選）
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        staff = await catalog_service.update_staff(
            staff_id=staff_id,
            merchant_id=merchant_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            skills=request.skills,
            is_active=request.is_active
        )
        
        return {
            "id": staff.id,
            "merchant_id": staff.merchant_id,
            "name": staff.name,
            "email": staff.email,
            "phone": staff.phone,
            "is_active": staff.is_active,
            "skills": staff.skills,
            "working_hours": [
                {
                    "day_of_week": wh.day_of_week.name,
                    "start_time": wh.start_time.strftime("%H:%M"),
                    "end_time": wh.end_time.strftime("%H:%M")
                }
                for wh in staff.working_hours
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新員工失敗: {str(e)}"
        )


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: int,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    刪除員工（軟刪除）
    
    - **staff_id**: 員工 ID
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        await catalog_service.delete_staff(staff_id, merchant_id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除員工失敗: {str(e)}"
        )


# ========== Holiday Endpoints ==========

@router.get("/holidays")
async def list_holidays(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    查詢商家的休假日列表
    
    - **start_date**: 開始日期（可選，用於範圍查詢）
    - **end_date**: 結束日期（可選，用於範圍查詢）
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        holidays = await catalog_service.list_holidays(merchant_id, start_date, end_date)
        
        return [
            {
                "id": h.id,
                "merchant_id": h.merchant_id,
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


@router.post("/holidays", status_code=status.HTTP_201_CREATED)
async def create_holiday(
    request: CreateHolidayRequest,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    新增休假日
    
    - **holiday_date**: 休假日期
    - **name**: 休假名稱
    - **is_recurring**: 是否每年重複
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        holiday = await catalog_service.create_holiday(
            merchant_id=merchant_id,
            holiday_date=request.holiday_date,
            name=request.name,
            is_recurring=request.is_recurring
        )
        
        return {
            "id": holiday.id,
            "merchant_id": holiday.merchant_id,
            "holiday_date": holiday.holiday_date.isoformat(),
            "name": holiday.name,
            "is_recurring": holiday.is_recurring
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"新增休假日失敗: {str(e)}"
        )


@router.put("/holidays/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    request: UpdateHolidayRequest,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    更新休假日
    
    - **holiday_id**: 休假日 ID
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        holiday = await catalog_service.update_holiday(
            holiday_id=holiday_id,
            merchant_id=merchant_id,
            holiday_date=request.holiday_date,
            name=request.name,
            is_recurring=request.is_recurring
        )
        
        return {
            "id": holiday.id,
            "merchant_id": holiday.merchant_id,
            "holiday_date": holiday.holiday_date.isoformat(),
            "name": holiday.name,
            "is_recurring": holiday.is_recurring
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新休假日失敗: {str(e)}"
        )


@router.delete("/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_id: int,
    current_user: User = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    刪除休假日
    
    - **holiday_id**: 休假日 ID
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        await catalog_service.delete_holiday(holiday_id, merchant_id)
        
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除休假日失敗: {str(e)}"
        )


# ========== Booking Update/Delete Endpoints ==========

@router.put("/bookings/{booking_id}")
async def update_booking(
    booking_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    更新預約資訊
    
    - **booking_id**: 預約 ID
    - 可更新: status, start_at (日期時間)
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        # 取得原預約
        booking = booking_service.booking_repo.find_by_id(booking_id, merchant_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"預約不存在: {booking_id}"
            )
        
        # 更新狀態
        if 'status' in request:
            from booking.domain.models import BookingStatus
            new_status = BookingStatus(request['status'])
            
            if new_status == BookingStatus.CANCELLED:
                # 商家端取消，使用客戶的 line_user_id（如果有）
                requester_line_id = booking.customer.line_user_id or "merchant"
                await booking_service.cancel_booking(booking_id, merchant_id, requester_line_id, "商家取消")
            else:
                # 直接更新狀態
                booking.status = new_status
                booking_service.booking_repo.save(booking)
        
        # 重新載入並返回
        updated_booking = booking_service.booking_repo.find_by_id(booking_id, merchant_id)
        
        time_slot = updated_booking.time_slot()
        return {
            "id": str(updated_booking.id),
            "merchant_id": updated_booking.merchant_id,
            "customer": updated_booking.customer,
            "staff_id": updated_booking.staff_id,
            "start_at": time_slot.start_at.isoformat(),
            "end_at": time_slot.end_at.isoformat(),
            "status": updated_booking.status.value,
            "total_price": float(updated_booking.total_price().amount),
            "total_duration": updated_booking.total_duration().minutes,
            "notes": updated_booking.notes,
            "items": [
                {
                    "service_id": item.service_id,
                    "service_name": item.service_name,
                    "service_price": float(item.service_price.amount),
                    "service_duration": item.service_duration.minutes,
                    "option_ids": item.option_ids,
                    "option_names": item.option_names,
                }
                for item in updated_booking.items
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新預約失敗: {str(e)}"
        )


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    刪除預約（取消預約）
    
    - **booking_id**: 預約 ID
    """
    try:
        merchant_id = current_user.merchant_id
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法取得商家資訊"
            )
        
        # 取得預約以獲取 line_user_id
        booking = booking_service.booking_repo.find_by_id(booking_id, merchant_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"預約不存在: {booking_id}"
            )
        
        # 取消預約
        requester_line_id = booking.customer.line_user_id or "merchant"
        await booking_service.cancel_booking(booking_id, merchant_id, requester_line_id, "商家刪除")
        
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除預約失敗: {str(e)}"
        )

