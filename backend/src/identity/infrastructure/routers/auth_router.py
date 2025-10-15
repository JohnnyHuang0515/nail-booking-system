"""
Identity Context - Infrastructure Layer - Auth Router
認證相關的 FastAPI 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from identity.application.dtos import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse
)
from identity.application.services import IdentityService
from identity.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)
from identity.infrastructure.dependencies import get_current_user, get_identity_service
from identity.domain.models import User, RoleType
from identity.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError
)
from shared.database import get_db
from shared.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    identity_service: IdentityService = Depends(get_identity_service)
):
    """
    註冊新用戶
    
    - **email**: Email 地址（唯一）
    - **password**: 密碼（至少 6 字元）
    - **name**: 姓名（可選）
    - **merchant_id**: 所屬商家 ID（可選，CUSTOMER 角色不需要）
    """
    try:
        user = identity_service.register_user(
            email=request.email,
            password=request.password,
            name=request.name,
            merchant_id=request.merchant_id,
            role_type=RoleType.CUSTOMER
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            line_user_id=user.line_user_id,
            name=user.name,
            merchant_id=user.merchant_id,
            role=user.role.name.value,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email 已存在: {e.email}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    identity_service: IdentityService = Depends(get_identity_service)
):
    """
    用戶登入
    
    - **email**: Email 地址
    - **password**: 密碼
    
    成功後返回 JWT Access Token
    """
    try:
        user, access_token = identity_service.login(
            email=request.email,
            password=request.password
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                line_user_id=user.line_user_id,
                name=user.name,
                merchant_id=user.merchant_id,
                role=user.role.name.value,
                is_active=user.is_active,
                is_verified=user.is_verified
            )
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email 或密碼錯誤"
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用戶已停用"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    取得當前登入用戶資訊
    
    需要在 Header 提供 JWT Token:
    Authorization: Bearer <token>
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        line_user_id=current_user.line_user_id,
        name=current_user.name,
        merchant_id=current_user.merchant_id,
        role=current_user.role.name.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified
    )


