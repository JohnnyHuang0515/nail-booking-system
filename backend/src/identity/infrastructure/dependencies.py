"""
Identity Context - Infrastructure Layer - FastAPI Dependencies
JWT 認證與授權的 FastAPI dependency
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from identity.application.services import IdentityService
from identity.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)
from identity.domain.models import User, Permission
from identity.domain.exceptions import (
    UserNotFoundError,
    UserInactiveError,
    PermissionDeniedError,
    TenantBoundaryViolationError
)
from shared.database import get_db
from jose import JWTError


security = HTTPBearer(auto_error=False)


def get_identity_service(db: Session = Depends(get_db)) -> IdentityService:
    """Dependency: 建立 IdentityService 實例"""
    user_repo = SQLAlchemyUserRepository(db)
    return IdentityService(user_repo)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    identity_service: IdentityService = Depends(get_identity_service)
) -> User:
    """
    Dependency: 取得當前登入用戶
    
    從 Authorization header 解析 JWT token 並返回用戶
    
    Raises:
        HTTPException 401: Token 無效或用戶不存在
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供認證 token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        user = identity_service.get_user_from_token(token)
    except (JWTError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證 token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用戶已停用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency: 取得當前啟用用戶
    
    檢查用戶是否為啟用狀態
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用戶已停用"
        )
    
    return current_user


def require_permission(permission: Permission):
    """
    Dependency Factory: 要求特定權限
    
    用法:
    @router.post("/admin/merchants")
    async def create_merchant(
        user: User = Depends(require_permission(Permission.MERCHANT_CREATE))
    ):
        ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"權限不足：需要 {permission.value}"
            )
        return current_user
    
    return permission_checker


def require_merchant_access(merchant_id: str):
    """
    Dependency Factory: 要求商家訪問權限
    
    用法:
    @router.get("/merchants/{merchant_id}/bookings")
    async def get_bookings(
        merchant_id: str,
        user: User = Depends(require_merchant_access(merchant_id))
    ):
        ...
    """
    async def merchant_access_checker(
        current_user: User = Depends(get_current_active_user),
        identity_service: IdentityService = Depends(get_identity_service)
    ) -> User:
        try:
            identity_service.validate_tenant_access(current_user.id, merchant_id)
        except TenantBoundaryViolationError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"無權訪問商家 {merchant_id}"
            )
        
        return current_user
    
    return merchant_access_checker

