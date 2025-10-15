"""
Billing Context - API Layer - Router
訂閱與計費相關的 API 端點
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from billing.application.services import BillingService
from billing.domain.models import Subscription, Plan, SubscriptionStatus
from billing.domain.exceptions import (
    SubscriptionNotFoundError,
    NoActiveSubscriptionError,
    SubscriptionPastDueError,
    PlanNotFoundError,
    QuotaExceededError
)
from shared.dependencies import get_db
from sqlalchemy.orm import Session
from billing.infrastructure.repositories.sqlalchemy_subscription_repository import SQLAlchemySubscriptionRepository
from billing.infrastructure.repositories.sqlalchemy_plan_repository import SQLAlchemyPlanRepository

router = APIRouter(prefix="/billing", tags=["billing"])


# ========== DTOs ==========

class PlanResponse(BaseModel):
    """方案回應 DTO"""
    id: int
    tier: str
    name: str
    price_amount: float
    price_currency: str
    billing_interval: str
    features: dict
    is_active: bool
    description: Optional[str] = None

class SubscriptionResponse(BaseModel):
    """訂閱回應 DTO"""
    id: str
    merchant_id: str
    plan_id: int
    status: str
    current_period_start: str
    current_period_end: str
    trial_end: Optional[str] = None
    cancelled_at: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class CreateSubscriptionRequest(BaseModel):
    """建立訂閱請求 DTO"""
    merchant_id: str
    plan_id: int
    trial_days: int = 14

class SubscriptionStatusResponse(BaseModel):
    """訂閱狀態回應 DTO"""
    can_create_booking: bool
    status: str
    plan_name: str
    features: dict
    quota_info: Optional[dict] = None


# ========== Dependencies ==========

def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    """Dependency: 建立 BillingService"""
    subscription_repo = SQLAlchemySubscriptionRepository(db)
    plan_repo = SQLAlchemyPlanRepository(db)
    return BillingService(subscription_repo, plan_repo)


# ========== Plan Endpoints ==========

@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    列出所有啟用方案
    """
    try:
        plans = billing_service.list_active_plans()
        return [
            PlanResponse(
                id=plan.id,
                tier=plan.tier.value,
                name=plan.name,
                price_amount=float(plan.price.amount),
                price_currency=plan.price.currency,
                billing_interval=plan.billing_interval,
                features={
                    "max_bookings_per_month": plan.features.max_bookings_per_month,
                    "max_staff": plan.features.max_staff,
                    "max_services": plan.features.max_services,
                    "enable_line_notification": plan.features.enable_line_notification,
                    "enable_custom_branding": plan.features.enable_custom_branding,
                    "enable_analytics": plan.features.enable_analytics,
                    "support_level": plan.features.support_level
                },
                is_active=plan.is_active,
                description=plan.description
            )
            for plan in plans
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢方案失敗: {str(e)}"
        )


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    取得特定方案詳情
    """
    try:
        plan = billing_service.get_plan(plan_id)
        return PlanResponse(
            id=plan.id,
            tier=plan.tier.value,
            name=plan.name,
            price_amount=float(plan.price.amount),
            price_currency=plan.price.currency,
            billing_interval=plan.billing_interval,
            features={
                "max_bookings_per_month": plan.features.max_bookings_per_month,
                "max_staff": plan.features.max_staff,
                "max_services": plan.features.max_services,
                "enable_line_notification": plan.features.enable_line_notification,
                "enable_custom_branding": plan.features.enable_custom_branding,
                "enable_analytics": plan.features.enable_analytics,
                "support_level": plan.features.support_level
            },
            is_active=plan.is_active,
            description=plan.description
        )
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"方案不存在: {plan_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢方案失敗: {str(e)}"
        )


# ========== Subscription Endpoints ==========

@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    建立新訂閱（含試用期）
    """
    try:
        subscription = billing_service.create_subscription(
            merchant_id=request.merchant_id,
            plan_id=request.plan_id,
            trial_days=request.trial_days
        )
        
        return SubscriptionResponse(
            id=subscription.id,
            merchant_id=subscription.merchant_id,
            plan_id=subscription.plan_id,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat() if subscription.updated_at else None
        )
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"方案不存在: {request.plan_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立訂閱失敗: {str(e)}"
        )


@router.get("/merchants/{merchant_id}/subscription", response_model=SubscriptionResponse)
async def get_merchant_subscription(
    merchant_id: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    取得商家的啟用訂閱
    """
    try:
        subscription = billing_service.get_active_subscription(merchant_id)
        
        return SubscriptionResponse(
            id=subscription.id,
            merchant_id=subscription.merchant_id,
            plan_id=subscription.plan_id,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat() if subscription.updated_at else None
        )
    except NoActiveSubscriptionError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家 {merchant_id} 無啟用訂閱"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢訂閱失敗: {str(e)}"
        )


@router.get("/merchants/{merchant_id}/subscription/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    merchant_id: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    檢查商家訂閱狀態與功能權限
    """
    try:
        subscription = billing_service.get_active_subscription(merchant_id)
        plan = billing_service.get_plan(subscription.plan_id)
        
        return SubscriptionStatusResponse(
            can_create_booking=subscription.can_create_booking(),
            status=subscription.status.value,
            plan_name=plan.name,
            features={
                "max_bookings_per_month": plan.features.max_bookings_per_month,
                "max_staff": plan.features.max_staff,
                "max_services": plan.features.max_services,
                "enable_line_notification": plan.features.enable_line_notification,
                "enable_custom_branding": plan.features.enable_custom_branding,
                "enable_analytics": plan.features.enable_analytics,
                "support_level": plan.features.support_level
            }
        )
    except NoActiveSubscriptionError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商家 {merchant_id} 無啟用訂閱"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢訂閱狀態失敗: {str(e)}"
        )


@router.post("/subscriptions/{subscription_id}/activate", response_model=SubscriptionResponse)
async def activate_subscription(
    subscription_id: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    啟用訂閱（付款成功後）
    """
    try:
        subscription = billing_service.activate_subscription(subscription_id)
        
        return SubscriptionResponse(
            id=subscription.id,
            merchant_id=subscription.merchant_id,
            plan_id=subscription.plan_id,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat() if subscription.updated_at else None
        )
    except SubscriptionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"訂閱不存在: {subscription_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"啟用訂閱失敗: {str(e)}"
        )


@router.post("/subscriptions/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """
    取消訂閱
    """
    try:
        subscription = billing_service.cancel_subscription(subscription_id)
        
        return SubscriptionResponse(
            id=subscription.id,
            merchant_id=subscription.merchant_id,
            plan_id=subscription.plan_id,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat() if subscription.updated_at else None
        )
    except SubscriptionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"訂閱不存在: {subscription_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消訂閱失敗: {str(e)}"
        )


# ========== Webhook Endpoints ==========

@router.post("/webhooks/stripe")
async def stripe_webhook(
    # 這裡應該接收 Stripe 的 webhook 事件
    # 簡化版：僅記錄日誌
):
    """
    接收 Stripe 付款 webhook
    """
    # TODO: 實作 Stripe webhook 驗證與處理
    return {"status": "received"}
