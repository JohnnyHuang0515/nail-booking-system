"""
平台管理員 API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.repositories.sql_appointment_repository import SQLAppointmentRepository
# from app.infrastructure.database.models import AdminUser  # 暫時註解，使用模擬資料

router = APIRouter()
security = HTTPBearer()

# JWT 設定
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "your-admin-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AdminLoginRequest(BaseModel):
    """管理員登入請求"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """管理員登入回應"""
    access_token: str
    token_type: str
    user: dict


class AdminUserResponse(BaseModel):
    """管理員用戶回應"""
    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class MerchantStatsResponse(BaseModel):
    """商家統計回應"""
    merchant_id: str
    name: str
    total_users: int
    total_appointments: int
    total_revenue: float
    is_active: bool


class SystemStatsResponse(BaseModel):
    """系統統計回應"""
    total_merchants: int
    active_merchants: int
    total_users: int
    total_appointments: int
    total_revenue: float
    system_health: dict


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """創建訪問令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """加密密碼"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), 
                     db_session = Depends(get_db_session)) -> dict:
    """取得當前管理員"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 這裡應該從資料庫查詢管理員資料
        # 暫時返回模擬資料
        return {
            "username": username,
            "role": "super_admin",
            "permissions": ["merchant_management", "system_settings", "reports"]
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, db_session = Depends(get_db_session)):
    """管理員登入"""
    try:
        # 這裡應該從資料庫查詢管理員資料
        # 暫時使用模擬驗證
        if request.username == "admin" and request.password == "admin123":
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": request.username}, expires_delta=access_token_expires
            )
            
            user_data = {
                "id": "1",
                "username": request.username,
                "email": "admin@platform.com",
                "role": "super_admin",
                "permissions": ["merchant_management", "system_settings", "reports"]
            }
            
            return AdminLoginResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶名或密碼錯誤"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登入失敗: {str(e)}"
        )


@router.get("/admin/profile", response_model=AdminUserResponse)
async def get_admin_profile(current_admin: dict = Depends(get_current_admin)):
    """取得管理員個人資料"""
    return AdminUserResponse(
        id="1",
        username=current_admin["username"],
        email="admin@platform.com",
        role=current_admin["role"],
        permissions=current_admin["permissions"],
        is_active=True,
        created_at="2024-01-01T00:00:00Z"
    )


@router.get("/admin/merchants", response_model=List[MerchantStatsResponse])
async def get_merchant_stats(
    current_admin: dict = Depends(get_current_admin),
    db_session = Depends(get_db_session)
):
    """取得所有商家統計資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        user_repo = SQLUserRepository(db_session)
        appointment_repo = SQLAppointmentRepository(db_session)
        
        merchants = merchant_repo.list_active()
        merchant_stats = []
        
        for merchant in merchants:
            # 統計用戶數
            users = user_repo.list_by_merchant(merchant.id)
            total_users = len(users)
            
            # 統計預約數（這裡需要實現相應的統計方法）
            # appointments = appointment_repo.list_by_merchant_and_date_range(...)
            total_appointments = 0  # 暫時設為 0
            
            # 統計營收（這裡需要實現相應的統計方法）
            total_revenue = 0.0  # 暫時設為 0
            
            merchant_stats.append(MerchantStatsResponse(
                merchant_id=str(merchant.id),
                name=merchant.name,
                total_users=total_users,
                total_appointments=total_appointments,
                total_revenue=total_revenue,
                is_active=merchant.is_active
            ))
        
        return merchant_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得商家統計失敗: {str(e)}"
        )


@router.get("/admin/system-stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_admin: dict = Depends(get_current_admin),
    db_session = Depends(get_db_session)
):
    """取得系統統計資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        user_repo = SQLUserRepository(db_session)
        
        # 統計商家數量
        all_merchants = merchant_repo.list_active()
        active_merchants = len([m for m in all_merchants if m.is_active])
        
        # 統計用戶數量
        total_users = 0
        for merchant in all_merchants:
            users = user_repo.list_by_merchant(merchant.id)
            total_users += len(users)
        
        # 系統健康狀態
        system_health = {
            "database": "healthy",
            "redis": "healthy",
            "line_api": "healthy",
            "load_average": "normal"
        }
        
        return SystemStatsResponse(
            total_merchants=len(all_merchants),
            active_merchants=active_merchants,
            total_users=total_users,
            total_appointments=0,  # 需要實現統計
            total_revenue=0.0,     # 需要實現統計
            system_health=system_health
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得系統統計失敗: {str(e)}"
        )


class SystemConfigRequest(BaseModel):
    """系統配置請求"""
    platform_name: Optional[str] = "美甲預約系統"
    default_timezone: Optional[str] = "Asia/Taipei"
    max_merchants: Optional[int] = 100
    webhook_timeout: Optional[int] = 30
    rate_limit_per_minute: Optional[int] = 100
    maintenance_mode: Optional[bool] = False
    email_notifications: Optional[bool] = True
    sms_notifications: Optional[bool] = False
    backup_frequency: Optional[str] = "daily"


class SystemConfigResponse(BaseModel):
    """系統配置回應"""
    platform_name: str
    default_timezone: str
    max_merchants: int
    webhook_timeout: int
    rate_limit_per_minute: int
    maintenance_mode: bool
    email_notifications: bool
    sms_notifications: bool
    backup_frequency: str
    last_updated: Optional[datetime] = None


@router.get("/admin/system-config", response_model=SystemConfigResponse)
async def get_system_config():
    """取得系統配置"""
    try:
        # 這裡應該從資料庫或配置文件讀取系統設定
        # 暫時返回預設配置
        return SystemConfigResponse(
            platform_name="美甲預約系統",
            default_timezone="Asia/Taipei",
            max_merchants=100,
            webhook_timeout=30,
            rate_limit_per_minute=100,
            maintenance_mode=False,
            email_notifications=True,
            sms_notifications=False,
            backup_frequency="daily",
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得系統配置失敗: {str(e)}"
        )


@router.put("/admin/system-config", response_model=SystemConfigResponse)
async def update_system_config(
    config: SystemConfigRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """更新系統配置"""
    try:
        # 這裡應該將配置保存到資料庫或配置文件
        # 暫時只返回更新後的配置
        return SystemConfigResponse(
            platform_name=config.platform_name,
            default_timezone=config.default_timezone,
            max_merchants=config.max_merchants,
            webhook_timeout=config.webhook_timeout,
            rate_limit_per_minute=config.rate_limit_per_minute,
            maintenance_mode=config.maintenance_mode,
            email_notifications=config.email_notifications,
            sms_notifications=config.sms_notifications,
            backup_frequency=config.backup_frequency,
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新系統配置失敗: {str(e)}"
        )


@router.post("/admin/merchants/{merchant_id}/toggle-status")
async def toggle_merchant_status(
    merchant_id: UUID,
    current_admin: dict = Depends(get_current_admin),
    db_session = Depends(get_db_session)
):
    """切換商家狀態"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_id)
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的商家"
            )
        
        # 切換狀態
        merchant.is_active = not merchant.is_active
        db_session.commit()
        
        return {
            "message": f"商家 {merchant.name} 已{'啟用' if merchant.is_active else '停用'}",
            "is_active": merchant.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切換商家狀態失敗: {str(e)}"
        )


@router.get("/admin/merchants/{merchant_id}/details")
async def get_merchant_details(
    merchant_id: UUID,
    current_admin: dict = Depends(get_current_admin),
    db_session = Depends(get_db_session)
):
    """取得商家詳細資料"""
    try:
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.get_decrypted_merchant(merchant_id)
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的商家"
            )
        
        # 移除敏感資訊
        merchant_details = {
            "id": str(merchant["id"]),
            "name": merchant["name"],
            "line_channel_id": merchant["line_channel_id"],
            "liff_id": merchant["liff_id"],
            "timezone": merchant["timezone"],
            "is_active": merchant["is_active"],
            "created_at": merchant["created_at"].isoformat()
        }
        
        return merchant_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得商家詳細資料失敗: {str(e)}"
        )
