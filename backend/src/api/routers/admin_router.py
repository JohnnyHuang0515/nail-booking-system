"""
系統管理員 API 路由
提供系統管理員專用的管理功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from shared.database import get_db
from identity.domain.models import User, RoleType, Permission
from identity.infrastructure.dependencies import get_current_user, require_permission
from merchant.domain.models import Merchant
from merchant.application.services import MerchantService
from merchant.infrastructure.repositories.sqlalchemy_merchant_repository import SQLAlchemyMerchantRepository
from billing.application.services import BillingService
from billing.infrastructure.repositories.sqlalchemy_billing_repository import SQLAlchemyBillingRepository

router = APIRouter(prefix="/admin", tags=["System Admin"])

# ========== DTOs ==========

class MerchantSummary(BaseModel):
    """商家摘要資訊"""
    id: str
    name: str
    email: str
    slug: str
    is_active: bool
    created_at: str
    subscription_status: Optional[str] = None
    total_bookings: int = 0
    total_revenue: float = 0.0

class CreateMerchantRequest(BaseModel):
    """建立商家請求"""
    name: str
    email: str
    slug: str
    line_channel_id: Optional[str] = None
    line_channel_secret: Optional[str] = None
    liff_id: Optional[str] = None
    timezone: str = "Asia/Taipei"

class UpdateMerchantRequest(BaseModel):
    """更新商家請求"""
    name: Optional[str] = None
    email: Optional[str] = None
    slug: Optional[str] = None
    line_channel_id: Optional[str] = None
    line_channel_secret: Optional[str] = None
    liff_id: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

class SystemStats(BaseModel):
    """系統統計資訊"""
    total_merchants: int
    active_merchants: int
    total_bookings: int
    total_revenue: float
    subscription_stats: dict

# ========== Dependencies ==========

def get_merchant_service(db: Session = Depends(get_db)) -> MerchantService:
    """Dependency: 建立 MerchantService"""
    merchant_repo = SQLAlchemyMerchantRepository(db)
    return MerchantService(merchant_repo)

def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    """Dependency: 建立 BillingService"""
    billing_repo = SQLAlchemyBillingRepository(db)
    return BillingService(billing_repo)

# ========== 系統統計 ==========

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service),
    billing_service: BillingService = Depends(get_billing_service),
    db: Session = Depends(get_db)
):
    """
    取得系統統計資訊
    只有系統管理員可以訪問
    """
    try:
        # 取得商家統計
        merchants = merchant_service.list_merchants()
        total_merchants = len(merchants)
        active_merchants = len([m for m in merchants if m.is_active])
        
        # TODO: 實現預約和收入統計
        total_bookings = 0
        total_revenue = 0.0
        
        # TODO: 實現訂閱統計
        subscription_stats = {
            "active": 0,
            "past_due": 0,
            "canceled": 0
        }
        
        return SystemStats(
            total_merchants=total_merchants,
            active_merchants=active_merchants,
            total_bookings=total_bookings,
            total_revenue=total_revenue,
            subscription_stats=subscription_stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得系統統計失敗: {str(e)}"
        )

# ========== 商家管理 ==========

@router.get("/merchants", response_model=List[MerchantSummary])
async def list_merchants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service),
    db: Session = Depends(get_db)
):
    """
    列出所有商家
    只有系統管理員可以訪問
    """
    try:
        merchants = merchant_service.list_merchants()
        
        # 簡單的搜尋過濾
        if search:
            merchants = [m for m in merchants if search.lower() in m.name.lower() or search.lower() in m.email.lower()]
        
        # 分頁
        merchants = merchants[skip:skip + limit]
        
        # 轉換為摘要格式
        merchant_summaries = []
        for merchant in merchants:
            # TODO: 取得訂閱狀態、預約數量、收入等資訊
            summary = MerchantSummary(
                id=merchant.id,
                name=merchant.name,
                email=merchant.email,
                slug=merchant.slug,
                is_active=merchant.is_active,
                created_at=merchant.created_at.isoformat() if merchant.created_at else "",
                subscription_status=None,
                total_bookings=0,
                total_revenue=0.0
            )
            merchant_summaries.append(summary)
        
        return merchant_summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"列出商家失敗: {str(e)}"
        )

@router.get("/merchants/{merchant_id}", response_model=MerchantSummary)
async def get_merchant(
    merchant_id: str,
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    取得特定商家詳情
    只有系統管理員可以訪問
    """
    try:
        merchant = merchant_service.get_merchant(merchant_id)
        
        # TODO: 取得訂閱狀態、預約數量、收入等資訊
        return MerchantSummary(
            id=merchant.id,
            name=merchant.name,
            email=merchant.email,
            slug=merchant.slug,
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat() if merchant.created_at else "",
            subscription_status=None,
            total_bookings=0,
            total_revenue=0.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家不存在: {merchant_id}"
        )

@router.post("/merchants", response_model=MerchantSummary, status_code=status.HTTP_201_CREATED)
async def create_merchant(
    request: CreateMerchantRequest,
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    建立新商家
    只有系統管理員可以訪問
    """
    try:
        # 建立商家
        merchant = merchant_service.create_merchant(
            name=request.name,
            email=request.email,
            slug=request.slug,
            line_channel_id=request.line_channel_id,
            line_channel_secret=request.line_channel_secret,
            liff_id=request.liff_id,
            timezone=request.timezone
        )
        
        return MerchantSummary(
            id=merchant.id,
            name=merchant.name,
            email=merchant.email,
            slug=merchant.slug,
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat() if merchant.created_at else "",
            subscription_status=None,
            total_bookings=0,
            total_revenue=0.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"建立商家失敗: {str(e)}"
        )

@router.put("/merchants/{merchant_id}", response_model=MerchantSummary)
async def update_merchant(
    merchant_id: str,
    request: UpdateMerchantRequest,
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    更新商家資訊
    只有系統管理員可以訪問
    """
    try:
        # 準備更新資料
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.email is not None:
            update_data["email"] = request.email
        if request.slug is not None:
            update_data["slug"] = request.slug
        if request.line_channel_id is not None:
            update_data["line_channel_id"] = request.line_channel_id
        if request.line_channel_secret is not None:
            update_data["line_channel_secret"] = request.line_channel_secret
        if request.liff_id is not None:
            update_data["liff_id"] = request.liff_id
        if request.timezone is not None:
            update_data["timezone"] = request.timezone
        if request.is_active is not None:
            update_data["is_active"] = request.is_active
        
        # 更新商家
        merchant = merchant_service.update_merchant(merchant_id, **update_data)
        
        return MerchantSummary(
            id=merchant.id,
            name=merchant.name,
            email=merchant.email,
            slug=merchant.slug,
            is_active=merchant.is_active,
            created_at=merchant.created_at.isoformat() if merchant.created_at else "",
            subscription_status=None,
            total_bookings=0,
            total_revenue=0.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新商家失敗: {str(e)}"
        )

@router.delete("/merchants/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_merchant(
    merchant_id: str,
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    刪除商家
    只有系統管理員可以訪問
    """
    try:
        merchant_service.delete_merchant(merchant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"刪除商家失敗: {str(e)}"
        )

# ========== 用戶管理 ==========

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    merchant_id: Optional[str] = Query(None),
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    db: Session = Depends(get_db)
):
    """
    列出所有用戶
    只有系統管理員可以訪問
    """
    try:
        # TODO: 實現用戶列表查詢
        return {"message": "用戶管理功能待實現"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"列出用戶失敗: {str(e)}"
        )

# ========== 系統設定 ==========

@router.get("/settings")
async def get_system_settings(
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL))
):
    """
    取得系統設定
    只有系統管理員可以訪問
    """
    try:
        # TODO: 實現系統設定管理
        return {"message": "系統設定功能待實現"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得系統設定失敗: {str(e)}"
        )

@router.put("/settings")
async def update_system_settings(
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL))
):
    """
    更新系統設定
    只有系統管理員可以訪問
    """
    try:
        # TODO: 實現系統設定更新
        return {"message": "系統設定更新功能待實現"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新系統設定失敗: {str(e)}"
        )
