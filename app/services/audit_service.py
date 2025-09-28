"""
審計軌跡服務
"""
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from uuid import UUID
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """審計動作類型"""
    # 憑證變更
    CREDENTIALS_ROTATE = "credentials:rotate"
    CREDENTIALS_UPDATE = "credentials:update"
    
    # 商家狀態變更
    MERCHANT_ACTIVATE = "merchant:activate"
    MERCHANT_DEACTIVATE = "merchant:deactivate"
    MERCHANT_CREATE = "merchant:create"
    MERCHANT_UPDATE = "merchant:update"
    
    # Rich Menu 操作
    RICH_MENU_PUBLISH = "rich_menu:publish"
    RICH_MENU_ROLLBACK = "rich_menu:rollback"
    RICH_MENU_UPDATE = "rich_menu:update"
    
    # 系統設定
    SYSTEM_SETTINGS_UPDATE = "system:settings:update"
    
    # 用戶管理
    USER_LOGIN = "user:login"
    USER_LOGOUT = "user:logout"
    USER_ROLE_CHANGE = "user:role:change"
    USER_DEACTIVATE = "user:deactivate"
    
    # 支援操作
    TICKET_CREATE = "ticket:create"
    TICKET_UPDATE = "ticket:update"
    TICKET_CLOSE = "ticket:close"
    
    # 回滾操作
    ROLLBACK_EXECUTE = "rollback:execute"


@dataclass
class AuditLog:
    """審計日誌"""
    id: UUID
    user_id: UUID
    username: str
    action: AuditAction
    resource_type: str  # merchant, system, user, etc.
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class AuditService:
    """審計軌跡服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def log_action(
        self,
        user_id: UUID,
        username: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """記錄審計動作"""
        
        audit_log = AuditLog(
            id=UUID("12345678-1234-1234-1234-123456789012"),  # 模擬 UUID
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )
        
        # 在實際環境中，這裡會將審計日誌保存到資料庫
        logger.info(f"審計日誌: {username} 執行了 {action.value} 操作")
        
        return audit_log
    
    def log_credential_change(
        self,
        user_id: UUID,
        username: str,
        merchant_id: UUID,
        action: AuditAction,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> AuditLog:
        """記錄憑證變更"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            resource_type="merchant",
            resource_id=str(merchant_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    
    def log_merchant_status_change(
        self,
        user_id: UUID,
        username: str,
        merchant_id: UUID,
        action: AuditAction,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> AuditLog:
        """記錄商家狀態變更"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            resource_type="merchant",
            resource_id=str(merchant_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    
    def log_rich_menu_operation(
        self,
        user_id: UUID,
        username: str,
        merchant_id: UUID,
        action: AuditAction,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> AuditLog:
        """記錄 Rich Menu 操作"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            resource_type="rich_menu",
            resource_id=str(merchant_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    
    def log_user_operation(
        self,
        user_id: UUID,
        username: str,
        action: AuditAction,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> AuditLog:
        """記錄用戶操作"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            resource_type="user",
            resource_id=str(user_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    
    def get_audit_logs(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """查詢審計日誌"""
        
        # 模擬查詢結果
        logs = [
            AuditLog(
                id=UUID("12345678-1234-1234-1234-123456789012"),
                user_id=UUID("87654321-4321-4321-4321-210987654321"),
                username="admin",
                action=AuditAction.MERCHANT_CREATE,
                resource_type="merchant",
                resource_id="1",
                details={"merchant_name": "台北時尚美甲"},
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0...",
                timestamp=datetime.now(),
                success=True
            ),
            AuditLog(
                id=UUID("11111111-2222-3333-4444-555555555555"),
                user_id=UUID("87654321-4321-4321-4321-210987654321"),
                username="admin",
                action=AuditAction.CREDENTIALS_ROTATE,
                resource_type="merchant",
                resource_id="1",
                details={"channel_id": "taipei_fashion_channel_1234567890abcdef"},
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0...",
                timestamp=datetime.now(),
                success=True
            )
        ]
        
        # 簡單過濾
        filtered_logs = logs
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log.resource_type == resource_type]
        if resource_id:
            filtered_logs = [log for log in filtered_logs if log.resource_id == resource_id]
        
        return filtered_logs[offset:offset + limit]
    
    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """取得審計摘要"""
        # 模擬摘要資料
        return {
            "total_actions": 150,
            "successful_actions": 145,
            "failed_actions": 5,
            "top_actions": [
                {"action": "merchant:create", "count": 25},
                {"action": "credentials:rotate", "count": 20},
                {"action": "rich_menu:publish", "count": 15}
            ],
            "top_users": [
                {"username": "admin", "count": 80},
                {"username": "ops_user", "count": 70}
            ],
            "recent_activities": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "username": "admin",
                    "action": "merchant:create",
                    "resource": "台北時尚美甲"
                }
            ]
        }
    
    def export_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """匯出審計日誌"""
        logs = self.get_audit_logs(start_date=start_date, end_date=end_date, limit=1000)
        
        if format == "json":
            return json.dumps([asdict(log) for log in logs], default=str, ensure_ascii=False, indent=2)
        elif format == "csv":
            # 簡化版 CSV 匯出
            csv_lines = ["id,user_id,username,action,resource_type,resource_id,timestamp,success"]
            for log in logs:
                csv_lines.append(f"{log.id},{log.user_id},{log.username},{log.action.value},{log.resource_type},{log.resource_id},{log.timestamp},{log.success}")
            return "\n".join(csv_lines)
        
        return ""
