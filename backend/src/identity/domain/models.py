"""
Identity Context - Domain Layer - Aggregates
User, Role, Permission 聚合
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
from enum import Enum
from typing import Optional


class RoleType(str, Enum):
    """角色類型"""
    ADMIN = "admin"  # 系統管理員
    MERCHANT_OWNER = "merchant_owner"  # 商家擁有者
    MERCHANT_STAFF = "merchant_staff"  # 商家員工
    CUSTOMER = "customer"  # 客戶


class Permission(str, Enum):
    """權限枚舉"""
    # Booking 權限
    BOOKING_CREATE = "booking:create"
    BOOKING_READ = "booking:read"
    BOOKING_UPDATE = "booking:update"
    BOOKING_DELETE = "booking:delete"
    
    # Merchant 權限
    MERCHANT_READ = "merchant:read"
    MERCHANT_UPDATE = "merchant:update"
    MERCHANT_DELETE = "merchant:delete"
    
    # Staff 權限
    STAFF_CREATE = "staff:create"
    STAFF_READ = "staff:read"
    STAFF_UPDATE = "staff:update"
    STAFF_DELETE = "staff:delete"
    
    # Service 權限
    SERVICE_CREATE = "service:create"
    SERVICE_READ = "service:read"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    
    # Billing 權限
    BILLING_READ = "billing:read"
    BILLING_UPDATE = "billing:update"
    
    # Admin 權限
    ADMIN_ALL = "admin:*"


@dataclass
class Role:
    """
    Role 實體
    
    不變式：
    1. 每個角色有固定的權限集合
    2. admin 角色擁有所有權限
    """
    id: int
    name: RoleType
    permissions: list[Permission] = field(default_factory=list)
    description: Optional[str] = None
    
    def __post_init__(self):
        if not self.permissions:
            self.permissions = self._default_permissions_for_role(self.name)
    
    def _default_permissions_for_role(self, role_type: RoleType) -> list[Permission]:
        """根據角色類型返回預設權限"""
        if role_type == RoleType.ADMIN:
            return [Permission.ADMIN_ALL]
        
        elif role_type == RoleType.MERCHANT_OWNER:
            return [
                Permission.BOOKING_CREATE,
                Permission.BOOKING_READ,
                Permission.BOOKING_UPDATE,
                Permission.BOOKING_DELETE,
                Permission.MERCHANT_READ,
                Permission.MERCHANT_UPDATE,
                Permission.STAFF_CREATE,
                Permission.STAFF_READ,
                Permission.STAFF_UPDATE,
                Permission.STAFF_DELETE,
                Permission.SERVICE_CREATE,
                Permission.SERVICE_READ,
                Permission.SERVICE_UPDATE,
                Permission.SERVICE_DELETE,
                Permission.BILLING_READ,
                Permission.BILLING_UPDATE,
            ]
        
        elif role_type == RoleType.MERCHANT_STAFF:
            return [
                Permission.BOOKING_CREATE,
                Permission.BOOKING_READ,
                Permission.BOOKING_UPDATE,
                Permission.STAFF_READ,
                Permission.SERVICE_READ,
            ]
        
        else:  # CUSTOMER
            return [
                Permission.BOOKING_CREATE,
                Permission.BOOKING_READ,
            ]
    
    def has_permission(self, permission: Permission) -> bool:
        """檢查是否擁有特定權限"""
        # ADMIN 擁有所有權限
        if Permission.ADMIN_ALL in self.permissions:
            return True
        
        return permission in self.permissions


class User:
    """
    User 聚合根
    
    不變式：
    1. email 或 line_user_id 至少一個不為空
    2. password_hash 不可為明文（Infrastructure 層處理）
    3. is_active 為 False 時無法登入
    4. 每個 User 必須關聯到 merchant_id（多租戶隔離）
    """
    
    def __init__(
        self,
        id: str,  # UUID
        email: Optional[str] = None,
        line_user_id: Optional[str] = None,
        name: Optional[str] = None,
        password_hash: Optional[str] = None,
        merchant_id: Optional[str] = None,  # 租戶邊界
        role: Optional[Role] = None,
        is_active: bool = True,
        is_verified: bool = False,
        last_login_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.line_user_id = line_user_id
        self.name = name
        self.password_hash = password_hash
        self.merchant_id = merchant_id
        self.role = role or Role(id=4, name=RoleType.CUSTOMER)
        self.is_active = is_active
        self.is_verified = is_verified
        self.last_login_at = last_login_at
        self.created_at = created_at or datetime.now(dt_timezone.utc)
        self.updated_at = updated_at
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if not self.email and not self.line_user_id:
            raise ValueError("email 或 line_user_id 至少需要一個")
    
    def has_permission(self, permission: Permission) -> bool:
        """檢查用戶是否擁有權限"""
        if not self.is_active:
            return False
        
        return self.role.has_permission(permission)
    
    def belongs_to_merchant(self, merchant_id: str) -> bool:
        """檢查用戶是否屬於特定商家（租戶隔離）"""
        return self.merchant_id == merchant_id
    
    def can_access_merchant(self, merchant_id: str) -> bool:
        """
        檢查用戶是否可訪問商家資源
        
        規則：
        - ADMIN 可訪問所有商家
        - 其他角色只能訪問自己的商家
        """
        if self.role.name == RoleType.ADMIN:
            return True
        
        return self.belongs_to_merchant(merchant_id)
    
    def update_last_login(self):
        """更新最後登入時間"""
        self.last_login_at = datetime.now(dt_timezone.utc)
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def activate(self):
        """啟用用戶"""
        self.is_active = True
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def deactivate(self):
        """停用用戶"""
        self.is_active = False
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def verify_email(self):
        """驗證 email"""
        self.is_verified = True
        self.updated_at = datetime.now(dt_timezone.utc)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.name.value})>"

