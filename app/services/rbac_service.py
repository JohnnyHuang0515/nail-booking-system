"""
角色基礎存取控制 (RBAC) 服務
"""
import logging
from typing import Dict, List, Optional, Set
from enum import Enum
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RoleType(Enum):
    """角色類型"""
    OWNER = "owner"           # 平台擁有者
    OPS = "ops"              # 運維人員
    READONLY = "readonly"    # 唯讀管理員


class Permission(Enum):
    """權限枚舉"""
    # 商家管理
    MERCHANT_CREATE = "merchant:create"
    MERCHANT_READ = "merchant:read"
    MERCHANT_UPDATE = "merchant:update"
    MERCHANT_DELETE = "merchant:delete"
    MERCHANT_TOGGLE_STATUS = "merchant:toggle_status"
    
    # 系統設定
    SYSTEM_SETTINGS_READ = "system:settings:read"
    SYSTEM_SETTINGS_UPDATE = "system:settings:update"
    
    # 監控
    MONITORING_READ = "monitoring:read"
    MONITORING_ALERTS_MANAGE = "monitoring:alerts:manage"
    
    # 報表
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    
    # 審計
    AUDIT_READ = "audit:read"
    
    # 支援
    SUPPORT_TICKETS_READ = "support:tickets:read"
    SUPPORT_TICKETS_MANAGE = "support:tickets:manage"


@dataclass
class AdminUser:
    """管理員用戶"""
    id: UUID
    username: str
    email: str
    role: RoleType
    permissions: Set[Permission]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class RBACService:
    """角色基礎存取控制服務"""
    
    # 角色權限映射
    ROLE_PERMISSIONS = {
        RoleType.OWNER: {
            Permission.MERCHANT_CREATE,
            Permission.MERCHANT_READ,
            Permission.MERCHANT_UPDATE,
            Permission.MERCHANT_DELETE,
            Permission.MERCHANT_TOGGLE_STATUS,
            Permission.SYSTEM_SETTINGS_READ,
            Permission.SYSTEM_SETTINGS_UPDATE,
            Permission.MONITORING_READ,
            Permission.MONITORING_ALERTS_MANAGE,
            Permission.REPORTS_READ,
            Permission.REPORTS_EXPORT,
            Permission.AUDIT_READ,
            Permission.SUPPORT_TICKETS_READ,
            Permission.SUPPORT_TICKETS_MANAGE,
        },
        RoleType.OPS: {
            Permission.MERCHANT_READ,
            Permission.MERCHANT_UPDATE,
            Permission.MERCHANT_TOGGLE_STATUS,
            Permission.SYSTEM_SETTINGS_READ,
            Permission.MONITORING_READ,
            Permission.MONITORING_ALERTS_MANAGE,
            Permission.REPORTS_READ,
            Permission.REPORTS_EXPORT,
            Permission.AUDIT_READ,
            Permission.SUPPORT_TICKETS_READ,
            Permission.SUPPORT_TICKETS_MANAGE,
        },
        RoleType.READONLY: {
            Permission.MERCHANT_READ,
            Permission.SYSTEM_SETTINGS_READ,
            Permission.MONITORING_READ,
            Permission.REPORTS_READ,
            Permission.AUDIT_READ,
            Permission.SUPPORT_TICKETS_READ,
        }
    }
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.jwt_secret = "your-secret-key"  # 應該從環境變數讀取
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = 24
    
    def get_role_permissions(self, role: RoleType) -> Set[Permission]:
        """取得角色權限"""
        return self.ROLE_PERMISSIONS.get(role, set())
    
    def check_permission(self, user: AdminUser, permission: Permission) -> bool:
        """檢查用戶權限"""
        if not user.is_active:
            return False
        
        return permission in user.permissions
    
    def check_permissions(self, user: AdminUser, permissions: List[Permission]) -> bool:
        """檢查用戶多個權限"""
        if not user.is_active:
            return False
        
        return all(permission in user.permissions for permission in permissions)
    
    def create_admin_user(self, username: str, email: str, role: RoleType) -> AdminUser:
        """創建管理員用戶"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")  # 模擬 UUID
        
        permissions = self.get_role_permissions(role)
        
        admin_user = AdminUser(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            is_active=True,
            created_at=datetime.now()
        )
        
        logger.info(f"創建管理員用戶: {username}, 角色: {role.value}")
        return admin_user
    
    def generate_jwt_token(self, user: AdminUser) -> str:
        """生成 JWT Token"""
        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expire_hours),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """驗證 JWT Token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT Token 已過期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("JWT Token 無效")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[AdminUser]:
        """從 Token 取得用戶資訊"""
        payload = self.verify_jwt_token(token)
        if not payload:
            return None
        
        # 模擬從資料庫取得用戶
        user_id = UUID(payload["user_id"])
        role = RoleType(payload["role"])
        permissions = {Permission(p) for p in payload["permissions"]}
        
        return AdminUser(
            id=user_id,
            username=payload["username"],
            email="admin@example.com",  # 模擬
            role=role,
            permissions=permissions,
            is_active=True,
            created_at=datetime.now()
        )
    
    def update_user_role(self, user_id: UUID, new_role: RoleType) -> bool:
        """更新用戶角色"""
        # 模擬更新
        logger.info(f"更新用戶 {user_id} 角色為 {new_role.value}")
        return True
    
    def deactivate_user(self, user_id: UUID) -> bool:
        """停用用戶"""
        # 模擬停用
        logger.info(f"停用用戶 {user_id}")
        return True
    
    def list_admin_users(self) -> List[AdminUser]:
        """列出所有管理員用戶"""
        # 模擬資料
        users = [
            AdminUser(
                id=UUID("12345678-1234-1234-1234-123456789012"),
                username="admin",
                email="admin@example.com",
                role=RoleType.OWNER,
                permissions=self.get_role_permissions(RoleType.OWNER),
                is_active=True,
                created_at=datetime.now()
            ),
            AdminUser(
                id=UUID("87654321-4321-4321-4321-210987654321"),
                username="ops_user",
                email="ops@example.com",
                role=RoleType.OPS,
                permissions=self.get_role_permissions(RoleType.OPS),
                is_active=True,
                created_at=datetime.now()
            )
        ]
        
        return users
