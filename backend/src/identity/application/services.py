"""
Identity Context - Application Layer - Services
IdentityService 協調認證與授權邏輯
"""
from typing import Optional
from uuid import uuid4

from identity.domain.models import User, Role, RoleType, Permission
from identity.domain.repositories import UserRepository
from identity.domain.auth_service import PasswordService, TokenService
from identity.domain.exceptions import (
    UserNotFoundError,
    UserInactiveError,
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    PermissionDeniedError,
    TenantBoundaryViolationError
)


class IdentityService:
    """
    IdentityService 應用服務
    
    職責：
    1. 用戶註冊與登入
    2. JWT Token 生成與驗證
    3. 權限檢查
    4. 租戶邊界檢查
    """
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register_user(
        self,
        email: str,
        password: str,
        name: Optional[str] = None,
        merchant_id: Optional[str] = None,
        role_type: RoleType = RoleType.CUSTOMER
    ) -> User:
        """
        註冊新用戶
        
        Args:
            email: Email
            password: 明文密碼
            name: 姓名
            merchant_id: 商家 ID
            role_type: 角色類型
        
        Returns:
            新建立的用戶
        
        Raises:
            EmailAlreadyExistsError: Email 已存在
        """
        # 檢查 email 是否已存在
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsError(email)
        
        # 雜湊密碼
        password_hash = PasswordService.hash_password(password)
        
        # 建立角色
        role = Role(
            id=role_type.value,  # 簡化：使用枚舉值作為 ID
            name=role_type
        )
        
        # 建立用戶
        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=password_hash,
            name=name,
            merchant_id=merchant_id,
            role=role,
            is_active=True,
            is_verified=False
        )
        
        self.user_repo.save(user)
        
        return user
    
    def login(self, email: str, password: str) -> tuple[User, str]:
        """
        用戶登入
        
        Args:
            email: Email
            password: 密碼
        
        Returns:
            (User, access_token)
        
        Raises:
            InvalidCredentialsError: 登入失敗
            UserInactiveError: 用戶未啟用
        """
        # 查詢用戶
        user = self.user_repo.find_by_email(email)
        
        if user is None:
            raise InvalidCredentialsError()
        
        # 驗證密碼
        if not PasswordService.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        # 檢查用戶狀態
        if not user.is_active:
            raise UserInactiveError(user.id)
        
        # 更新最後登入時間
        user.update_last_login()
        self.user_repo.save(user)
        
        # 生成 Access Token
        access_token = TokenService.create_access_token(
            user_id=user.id,
            merchant_id=user.merchant_id,
            role=user.role.name.value
        )
        
        return user, access_token
    
    def get_user_from_token(self, token: str) -> User:
        """
        從 Token 取得用戶
        
        Args:
            token: JWT token
        
        Returns:
            User 聚合
        
        Raises:
            UserNotFoundError: 用戶不存在
            JWTError: Token 無效
        """
        user_id = TokenService.get_user_id_from_token(token)
        
        if user_id is None:
            raise UserNotFoundError("Invalid token")
        
        user = self.user_repo.find_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        return user
    
    def validate_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> User:
        """
        驗證用戶權限
        
        Args:
            user_id: 用戶 ID
            permission: 所需權限
        
        Returns:
            User 聚合
        
        Raises:
            UserNotFoundError: 用戶不存在
            PermissionDeniedError: 權限不足
        """
        user = self.user_repo.find_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        if not user.has_permission(permission):
            raise PermissionDeniedError(user_id, permission.value)
        
        return user
    
    def validate_tenant_access(
        self,
        user_id: str,
        merchant_id: str
    ) -> User:
        """
        驗證租戶訪問權限
        
        Args:
            user_id: 用戶 ID
            merchant_id: 請求訪問的商家 ID
        
        Returns:
            User 聚合
        
        Raises:
            UserNotFoundError: 用戶不存在
            TenantBoundaryViolationError: 租戶邊界越權
        """
        user = self.user_repo.find_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        if not user.can_access_merchant(merchant_id):
            raise TenantBoundaryViolationError(user_id, merchant_id)
        
        return user
    
    def get_user(self, user_id: str) -> User:
        """取得用戶"""
        user = self.user_repo.find_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        return user
    
    def list_merchant_users(self, merchant_id: str) -> list[User]:
        """列出商家的所有用戶"""
        return self.user_repo.find_by_merchant(merchant_id)

