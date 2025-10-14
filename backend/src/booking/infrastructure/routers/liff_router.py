"""
Booking Context - Infrastructure Layer - LIFF API Router
LIFF 客戶端使用的預約 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from booking.application.services import BookingService
from booking.application.dtos import (
    CreateBookingRequest,
    BookingResponse,
    CancelBookingRequest
)
from booking.domain.exceptions import (
    BookingOverlapError,
    StaffInactiveError,
    ServiceInactiveError
)
from booking.domain.models import Customer
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
from shared.exceptions import (
    MerchantInactiveError,
    SubscriptionPastDueError,
    EntityNotFoundError,
    PermissionDeniedError
)

router = APIRouter(prefix="/liff", tags=["LIFF Booking"])


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """Dependency: 建立 BookingService 實例（含 CatalogService 整合）"""
    # Booking Repositories
    booking_repo = SQLAlchemyBookingRepository(db)
    booking_lock_repo = SQLAlchemyBookingLockRepository(db)
    
    # Catalog Repositories
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    
    # CatalogService
    catalog_service = CatalogService(service_repo, staff_repo)
    
    # BookingService（整合 CatalogService）
    return BookingService(booking_repo, booking_lock_repo, catalog_service)


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: CreateBookingRequest,
    service: BookingService = Depends(get_booking_service),
    db: Session = Depends(get_db)
):
    """
    建立預約（LIFF 客戶端）
    
    流程：
    1. 驗證商家與訂閱狀態
    2. 計算價格與時長
    3. 檢查時段衝突
    4. 建立 BookingLock + Booking
    5. 發布 BookingConfirmed 事件
    6. LINE 推播（異步）
    
    Raises:
        403: 商家停用或訂閱逾期
        400: 員工停用、服務停用、時段衝突
    """
    try:
        # 轉換 DTO 為 Domain 物件
        customer = Customer(
            line_user_id=request.customer.line_user_id,
            name=request.customer.name,
            phone=request.customer.phone,
            email=request.customer.email
        )
        
        # 建立預約
        booking = await service.create_booking(
            merchant_id=request.merchant_id,
            customer=customer,
            staff_id=request.staff_id,
            start_at=request.start_at,
            items_data=[
                {"service_id": item.service_id, "option_ids": item.option_ids}
                for item in request.items
            ],
            notes=request.notes
        )
        
        # 提交交易
        db.commit()
        
        # 轉換為響應 DTO
        return _booking_to_response(booking)
    
    except MerchantInactiveError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    
    except SubscriptionPastDueError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    
    except (BookingOverlapError, StaffInactiveError, ServiceInactiveError) as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"建立預約失敗: {str(e)}")


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_200_OK)
async def cancel_booking(
    booking_id: str,
    request: CancelBookingRequest,
    service: BookingService = Depends(get_booking_service),
    db: Session = Depends(get_db)
):
    """
    取消預約（LIFF 客戶端）
    
    驗證：
    - 只有預約擁有者可取消
    - 狀態必須為 confirmed 或 pending
    
    Raises:
        404: 預約不存在
        403: 無權取消
        400: 已完成無法取消
    """
    try:
        booking = await service.cancel_booking(
            booking_id=booking_id,
            merchant_id=request.merchant_id,
            requester_line_id=request.requester_line_id,
            reason=request.reason or ""
        )
        
        db.commit()
        
        return {"message": "預約已取消", "booking_id": booking.id}
    
    except EntityNotFoundError:
        db.rollback()
        raise HTTPException(status_code=404, detail="預約不存在")
    
    except PermissionDeniedError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    merchant_id: str,
    service: BookingService = Depends(get_booking_service)
):
    """查詢預約詳情"""
    booking = await service.get_booking(booking_id, merchant_id)
    
    if not booking:
        raise HTTPException(status_code=404, detail="預約不存在")
    
    return _booking_to_response(booking)


# === Helper Functions ===

def _booking_to_response(booking) -> BookingResponse:
    """Domain Booking → Response DTO"""
    from booking.application.dtos import BookingItemResponse, CustomerDTO
    
    items_response = []
    for item in booking.items:
        items_response.append(BookingItemResponse(
            service_id=item.service_id,
            service_name=item.service_name,
            service_price=item.service_price.amount,
            service_duration_minutes=item.service_duration.minutes,
            option_ids=item.option_ids,
            option_names=item.option_names,
            total_price=item.total_price().amount,
            total_duration_minutes=item.total_duration().minutes
        ))
    
    return BookingResponse(
        id=booking.id,
        merchant_id=booking.merchant_id,
        customer=CustomerDTO(
            line_user_id=booking.customer.line_user_id,
            name=booking.customer.name,
            phone=booking.customer.phone,
            email=booking.customer.email
        ),
        staff_id=booking.staff_id,
        status=booking.status.value,
        start_at=booking.start_at,
        end_at=booking.end_at,
        items=items_response,
        total_price=booking.total_price().amount,
        total_duration_minutes=booking.total_duration().minutes,
        notes=booking.notes,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        cancelled_at=booking.cancelled_at,
        completed_at=booking.completed_at
    )

