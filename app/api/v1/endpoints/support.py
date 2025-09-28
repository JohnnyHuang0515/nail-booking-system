"""
支援與運維 API
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.infrastructure.database.session import get_db_session
from app.services.support_service import (
    SupportService, TicketStatus, TicketPriority, TicketCategory,
    NotificationType
)
from app.services.rbac_service import RBACService, Permission

router = APIRouter()


# 工單相關模型
class TicketCreateRequest(BaseModel):
    """創建工單請求"""
    title: str
    description: str
    category: str  # technical, billing, feature_request, bug_report, general
    priority: str  # low, medium, high, urgent
    merchant_id: Optional[str] = None


class TicketUpdateRequest(BaseModel):
    """更新工單請求"""
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    comment: Optional[str] = None


class TicketResponse(BaseModel):
    """工單回應"""
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    merchant_id: Optional[str]
    created_by: str
    assigned_to: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]
    attachments: List[str]
    comments: List[Dict[str, Any]]


# 通知相關模型
class NotificationSendRequest(BaseModel):
    """發送通知請求"""
    type: str  # email, sms, push, webhook
    recipient: str
    subject: str
    content: str


class MerchantNotificationRequest(BaseModel):
    """商家通知請求"""
    merchant_id: str
    subject: str
    content: str
    type: str = "email"


class SystemAlertRequest(BaseModel):
    """系統警報請求"""
    alert_type: str
    message: str
    severity: str = "medium"


class NotificationResponse(BaseModel):
    """通知回應"""
    id: str
    type: str
    recipient: str
    subject: str
    content: str
    sent_at: str
    status: str
    retry_count: int


# 回滾相關模型
class RollbackCreateRequest(BaseModel):
    """創建回滾請求"""
    operation_type: str
    target_id: str
    description: str
    rollback_data: Dict[str, Any]


class RollbackResponse(BaseModel):
    """回滾回應"""
    id: str
    operation_type: str
    target_id: str
    description: str
    executed_by: str
    executed_at: str
    status: str
    rollback_data: Dict[str, Any]


# 依賴注入
def get_support_service(db_session = Depends(get_db_session)) -> SupportService:
    return SupportService(db_session)


def get_rbac_service(db_session = Depends(get_db_session)) -> RBACService:
    return RBACService(db_session)


def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """取得當前用戶（簡化版）"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的認證令牌")
    
    token = authorization.split(" ")[1]
    rbac_service = RBACService(None)  # 簡化版
    user = rbac_service.get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="無效的認證令牌")
    
    return {
        "id": str(user.id),
        "username": user.username,
        "role": user.role.value,
        "permissions": [p.value for p in user.permissions]
    }


# 工單管理 API
@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """創建支援工單"""
    try:
        category = TicketCategory(ticket_data.category)
        priority = TicketPriority(ticket_data.priority)
        merchant_id = UUID(ticket_data.merchant_id) if ticket_data.merchant_id else None
        
        ticket = support_service.create_ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            category=category,
            priority=priority,
            merchant_id=merchant_id,
            created_by=current_user["username"]
        )
        
        return TicketResponse(
            id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            category=ticket.category.value,
            priority=ticket.priority.value,
            status=ticket.status.value,
            merchant_id=str(ticket.merchant_id) if ticket.merchant_id else None,
            created_by=ticket.created_by,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at.isoformat(),
            updated_at=ticket.updated_at.isoformat(),
            resolved_at=ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            attachments=ticket.attachments,
            comments=ticket.comments
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建工單失敗: {str(e)}")


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    merchant_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """列出工單"""
    # 檢查權限
    if Permission.SUPPORT_TICKETS_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        # 解析枚舉
        ticket_status = TicketStatus(status) if status else None
        ticket_priority = TicketPriority(priority) if priority else None
        ticket_category = TicketCategory(category) if category else None
        merchant_uuid = UUID(merchant_id) if merchant_id else None
        
        tickets = support_service.list_tickets(
            status=ticket_status,
            priority=ticket_priority,
            category=ticket_category,
            merchant_id=merchant_uuid,
            limit=limit,
            offset=offset
        )
        
        return [
            TicketResponse(
                id=str(ticket.id),
                title=ticket.title,
                description=ticket.description,
                category=ticket.category.value,
                priority=ticket.priority.value,
                status=ticket.status.value,
                merchant_id=str(ticket.merchant_id) if ticket.merchant_id else None,
                created_by=ticket.created_by,
                assigned_to=ticket.assigned_to,
                created_at=ticket.created_at.isoformat(),
                updated_at=ticket.updated_at.isoformat(),
                resolved_at=ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                attachments=ticket.attachments,
                comments=ticket.comments
            )
            for ticket in tickets
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢工單失敗: {str(e)}")


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """取得工單詳情"""
    # 檢查權限
    if Permission.SUPPORT_TICKETS_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    ticket = support_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工單不存在")
    
    return TicketResponse(
        id=str(ticket.id),
        title=ticket.title,
        description=ticket.description,
        category=ticket.category.value,
        priority=ticket.priority.value,
        status=ticket.status.value,
        merchant_id=str(ticket.merchant_id) if ticket.merchant_id else None,
        created_by=ticket.created_by,
        assigned_to=ticket.assigned_to,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        resolved_at=ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        attachments=ticket.attachments,
        comments=ticket.comments
    )


@router.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: UUID,
    update_data: TicketUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """更新工單"""
    # 檢查權限
    if Permission.SUPPORT_TICKETS_MANAGE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        if update_data.status:
            status = TicketStatus(update_data.status)
            success = support_service.update_ticket_status(
                ticket_id=ticket_id,
                status=status,
                updated_by=current_user["username"],
                comment=update_data.comment
            )
            if not success:
                raise HTTPException(status_code=500, detail="更新工單狀態失敗")
        
        if update_data.assigned_to:
            success = support_service.assign_ticket(ticket_id, update_data.assigned_to)
            if not success:
                raise HTTPException(status_code=500, detail="指派工單失敗")
        
        return {"status": "success", "message": "工單已更新"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新工單失敗: {str(e)}")


@router.get("/tickets/statistics")
async def get_ticket_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """取得工單統計"""
    # 檢查權限
    if Permission.SUPPORT_TICKETS_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    statistics = support_service.get_ticket_statistics()
    return statistics


# 通知管理 API
@router.post("/notifications/send", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationSendRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """發送通知"""
    try:
        notification_type = NotificationType(notification_data.type)
        
        notification = support_service.send_notification(
            notification_type=notification_type,
            recipient=notification_data.recipient,
            subject=notification_data.subject,
            content=notification_data.content
        )
        
        return NotificationResponse(
            id=str(notification.id),
            type=notification.type.value,
            recipient=notification.recipient,
            subject=notification.subject,
            content=notification.content,
            sent_at=notification.sent_at.isoformat(),
            status=notification.status,
            retry_count=notification.retry_count
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送通知失敗: {str(e)}")


@router.post("/notifications/merchant")
async def send_merchant_notification(
    notification_data: MerchantNotificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """發送商家通知"""
    try:
        merchant_id = UUID(notification_data.merchant_id)
        notification_type = NotificationType(notification_data.type)
        
        notification = support_service.send_merchant_notification(
            merchant_id=merchant_id,
            subject=notification_data.subject,
            content=notification_data.content,
            notification_type=notification_type
        )
        
        return {
            "status": "success",
            "message": "商家通知已發送",
            "notification_id": str(notification.id),
            "sent_at": notification.sent_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送商家通知失敗: {str(e)}")


@router.post("/notifications/system-alert")
async def send_system_alert(
    alert_data: SystemAlertRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """發送系統警報"""
    try:
        notifications = support_service.send_system_alert(
            alert_type=alert_data.alert_type,
            message=alert_data.message,
            severity=alert_data.severity
        )
        
        return {
            "status": "success",
            "message": "系統警報已發送",
            "notifications_sent": len(notifications),
            "sent_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送系統警報失敗: {str(e)}")


@router.get("/notifications/history", response_model=List[NotificationResponse])
async def get_notification_history(
    recipient: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """取得通知歷史"""
    try:
        notification_type = NotificationType(type) if type else None
        
        notifications = support_service.get_notification_history(
            recipient=recipient,
            notification_type=notification_type,
            limit=limit,
            offset=offset
        )
        
        return [
            NotificationResponse(
                id=str(notification.id),
                type=notification.type.value,
                recipient=notification.recipient,
                subject=notification.subject,
                content=notification.content,
                sent_at=notification.sent_at.isoformat(),
                status=notification.status,
                retry_count=notification.retry_count
            )
            for notification in notifications
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢通知歷史失敗: {str(e)}")


# 回滾操作 API
@router.post("/rollback", response_model=RollbackResponse)
async def create_rollback_operation(
    rollback_data: RollbackCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """創建回滾操作"""
    try:
        target_id = UUID(rollback_data.target_id)
        
        rollback = support_service.create_rollback_operation(
            operation_type=rollback_data.operation_type,
            target_id=target_id,
            description=rollback_data.description,
            executed_by=current_user["username"],
            rollback_data=rollback_data.rollback_data
        )
        
        return RollbackResponse(
            id=str(rollback.id),
            operation_type=rollback.operation_type,
            target_id=str(rollback.target_id),
            description=rollback.description,
            executed_by=rollback.executed_by,
            executed_at=rollback.executed_at.isoformat(),
            status=rollback.status,
            rollback_data=rollback.rollback_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建回滾操作失敗: {str(e)}")


@router.post("/rollback/{rollback_id}/execute")
async def execute_rollback(
    rollback_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """執行回滾操作"""
    try:
        success = support_service.execute_rollback(rollback_id)
        
        if success:
            return {
                "status": "success",
                "message": "回滾操作已執行",
                "rollback_id": str(rollback_id),
                "executed_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="執行回滾操作失敗")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"執行回滾操作失敗: {str(e)}")


@router.get("/rollback/history", response_model=List[RollbackResponse])
async def get_rollback_history(
    operation_type: Optional[str] = None,
    target_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """取得回滾歷史"""
    try:
        target_uuid = UUID(target_id) if target_id else None
        
        rollbacks = support_service.get_rollback_history(
            operation_type=operation_type,
            target_id=target_uuid,
            limit=limit,
            offset=offset
        )
        
        return [
            RollbackResponse(
                id=str(rollback.id),
                operation_type=rollback.operation_type,
                target_id=str(rollback.target_id),
                description=rollback.description,
                executed_by=rollback.executed_by,
                executed_at=rollback.executed_at.isoformat(),
                status=rollback.status,
                rollback_data=rollback.rollback_data
            )
            for rollback in rollbacks
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢回滾歷史失敗: {str(e)}")


@router.get("/rollback/statistics")
async def get_rollback_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    support_service: SupportService = Depends(get_support_service)
):
    """取得回滾統計"""
    statistics = support_service.get_rollback_statistics()
    return statistics
