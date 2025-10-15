"""
Notification Context - API Layer - Router
通知與 LINE 推播相關的 API 端點
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from notification.application.services import NotificationService
from notification.domain.models import NotificationType, ChannelType
from notification.domain.exceptions import (
    TemplateNotFoundError,
    TemplateRenderError,
    NotificationSendError,
    LineCredentialsNotConfiguredError
)
from merchant.application.services import MerchantService
from merchant.domain.repositories import MerchantRepository
from merchant.infrastructure.repositories.sqlalchemy_merchant_repository import SQLAlchemyMerchantRepository
from shared.dependencies import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ========== DTOs ==========

class SendNotificationRequest(BaseModel):
    """發送通知請求 DTO"""
    merchant_id: str
    recipient: str  # LINE User ID
    notification_type: str
    variables: dict

class NotificationResponse(BaseModel):
    """通知回應 DTO"""
    success: bool
    message: str
    notification_id: Optional[str] = None

class TestNotificationRequest(BaseModel):
    """測試通知請求 DTO"""
    merchant_id: str
    recipient: str
    message: str


# ========== Dependencies ==========

def get_notification_service() -> NotificationService:
    """Dependency: 建立 NotificationService"""
    return NotificationService()

def get_merchant_service(db: Session = Depends(get_db)) -> MerchantService:
    """Dependency: 建立 MerchantService"""
    merchant_repo = SQLAlchemyMerchantRepository(db)
    return MerchantService(merchant_repo)


# ========== Notification Endpoints ==========

@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    notification_service: NotificationService = Depends(get_notification_service),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    發送通知（預約確認、取消等）
    """
    try:
        # 取得商家資訊
        merchant = merchant_service.get_merchant_by_id(request.merchant_id)
        
        # 根據通知類型發送
        notification_type = NotificationType(request.notification_type)
        
        if notification_type == NotificationType.BOOKING_CONFIRMED:
            success = notification_service.send_booking_confirmed_notification(
                merchant=merchant,
                customer_line_user_id=request.recipient,
                customer_name=request.variables.get("customer_name", "客戶"),
                booking_id=request.variables.get("booking_id", ""),
                start_at=request.variables.get("start_at", ""),
                service_name=request.variables.get("service_name", "")
            )
        elif notification_type == NotificationType.BOOKING_CANCELLED:
            success = notification_service.send_booking_cancelled_notification(
                merchant=merchant,
                customer_line_user_id=request.recipient,
                customer_name=request.variables.get("customer_name", "客戶"),
                booking_id=request.variables.get("booking_id", ""),
                start_at=request.variables.get("start_at", ""),
                service_name=request.variables.get("service_name", "")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支援的通知類型: {notification_type}"
            )
        
        return NotificationResponse(
            success=success,
            message="通知發送成功" if success else "通知發送失敗"
        )
        
    except TemplateNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板不存在: {str(e)}"
        )
    except TemplateRenderError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"模板渲染失敗: {str(e)}"
        )
    except LineCredentialsNotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LINE 憑證未配置: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"發送通知失敗: {str(e)}"
        )


@router.post("/test", response_model=NotificationResponse)
async def test_notification(
    request: TestNotificationRequest,
    notification_service: NotificationService = Depends(get_notification_service),
    merchant_service: MerchantService = Depends(get_merchant_service)
):
    """
    測試通知發送（用於驗證 LINE 憑證）
    """
    try:
        # 取得商家資訊
        merchant = merchant_service.get_merchant_by_id(request.merchant_id)
        
        # 建立測試模板
        from notification.domain.models import MessageTemplate
        
        test_template = MessageTemplate(
            id=0,
            merchant_id=request.merchant_id,
            template_key=NotificationType.BOOKING_CONFIRMED,
            channel_type=ChannelType.LINE,
            template=request.message,
            is_active=True
        )
        
        # 發送測試訊息
        from notification.domain.line_service import LineMessagingService
        
        if merchant.line_credentials and merchant.line_credentials.is_configured():
            line_service = LineMessagingService(
                channel_access_token=merchant.line_credentials.channel_access_token
            )
            
            from notification.domain.models import LineMessage
            test_message = LineMessage(text=request.message)
            
            success = line_service.send_message(
                to=request.recipient,
                message=test_message
            )
            
            return NotificationResponse(
                success=success,
                message="測試通知發送成功" if success else "測試通知發送失敗"
            )
        else:
            raise LineCredentialsNotConfiguredError(request.merchant_id)
            
    except LineCredentialsNotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LINE 憑證未配置: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"測試通知失敗: {str(e)}"
        )


@router.get("/templates")
async def list_notification_templates():
    """
    列出可用的通知模板類型
    """
    return {
        "templates": [
            {
                "type": NotificationType.BOOKING_CONFIRMED.value,
                "name": "預約確認通知",
                "description": "客戶預約成功後發送"
            },
            {
                "type": NotificationType.BOOKING_CANCELLED.value,
                "name": "預約取消通知", 
                "description": "客戶取消預約後發送"
            },
            {
                "type": NotificationType.BOOKING_REMINDER.value,
                "name": "預約提醒通知",
                "description": "預約前提醒客戶"
            },
            {
                "type": NotificationType.BOOKING_COMPLETED.value,
                "name": "服務完成通知",
                "description": "服務完成後發送"
            }
        ]
    }


# ========== Webhook Endpoints ==========

@router.post("/webhooks/line")
async def line_webhook(
    # 這裡應該接收 LINE 的 webhook 事件
    # 簡化版：僅記錄日誌
):
    """
    接收 LINE Bot webhook
    """
    # TODO: 實作 LINE webhook 驗證與處理
    return {"status": "received"}
