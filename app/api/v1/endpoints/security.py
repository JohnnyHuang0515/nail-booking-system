"""
安全與治理 API
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.infrastructure.database.session import get_db_session
from app.services.rbac_service import RBACService, RoleType, Permission
from app.services.audit_service import AuditService, AuditAction
from app.services.secret_manager_service import SecretManagerService

router = APIRouter()


# RBAC 相關模型
class AdminUserCreate(BaseModel):
    """創建管理員用戶請求"""
    username: str
    email: str
    role: str  # owner, ops, readonly


class AdminUserResponse(BaseModel):
    """管理員用戶回應"""
    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    is_active: bool
    created_at: str


class RoleUpdateRequest(BaseModel):
    """角色更新請求"""
    role: str


# 審計相關模型
class AuditLogResponse(BaseModel):
    """審計日誌回應"""
    id: str
    user_id: str
    username: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: str
    success: bool
    error_message: Optional[str]


class AuditQueryRequest(BaseModel):
    """審計查詢請求"""
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 100
    offset: int = 0


# 秘密管理相關模型
class SecretStoreRequest(BaseModel):
    """儲存秘密請求"""
    key: str
    value: str


class CredentialRotateRequest(BaseModel):
    """憑證輪替請求"""
    new_secret: Optional[str] = None
    new_token: Optional[str] = None


# 依賴注入
def get_rbac_service(db_session = Depends(get_db_session)) -> RBACService:
    return RBACService(db_session)


def get_audit_service(db_session = Depends(get_db_session)) -> AuditService:
    return AuditService(db_session)


def get_secret_manager_service(db_session = Depends(get_db_session)) -> SecretManagerService:
    return SecretManagerService(db_session)


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


# RBAC API
@router.post("/admin/users", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """創建管理員用戶"""
    # 檢查權限
    if Permission.USER_MANAGE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        role = RoleType(user_data.role)
        admin_user = rbac_service.create_admin_user(
            username=user_data.username,
            email=user_data.email,
            role=role
        )
        
        return AdminUserResponse(
            id=str(admin_user.id),
            username=admin_user.username,
            email=admin_user.email,
            role=admin_user.role.value,
            permissions=[p.value for p in admin_user.permissions],
            is_active=admin_user.is_active,
            created_at=admin_user.created_at.isoformat()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的角色類型")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建用戶失敗: {str(e)}")


@router.get("/admin/users", response_model=List[AdminUserResponse])
async def list_admin_users(
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """列出管理員用戶"""
    # 檢查權限
    if Permission.USER_MANAGE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    users = rbac_service.list_admin_users()
    
    return [
        AdminUserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role.value,
            permissions=[p.value for p in user.permissions],
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_data: RoleUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """更新用戶角色"""
    # 檢查權限
    if Permission.USER_MANAGE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        new_role = RoleType(role_data.role)
        success = rbac_service.update_user_role(user_id, new_role)
        
        if success:
            return {"status": "success", "message": "用戶角色已更新"}
        else:
            raise HTTPException(status_code=500, detail="更新用戶角色失敗")
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的角色類型")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用戶角色失敗: {str(e)}")


# 審計 API
@router.get("/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """查詢審計日誌"""
    # 檢查權限
    if Permission.AUDIT_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        # 解析日期
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # 解析動作
        audit_action = AuditAction(action) if action else None
        
        logs = audit_service.get_audit_logs(
            user_id=UUID(user_id) if user_id else None,
            action=audit_action,
            resource_type=resource_type,
            resource_id=resource_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        return [
            AuditLogResponse(
                id=str(log.id),
                user_id=str(log.user_id),
                username=log.username,
                action=log.action.value,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                timestamp=log.timestamp.isoformat(),
                success=log.success,
                error_message=log.error_message
            )
            for log in logs
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無效的參數: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢審計日誌失敗: {str(e)}")


@router.get("/audit/summary")
async def get_audit_summary(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """取得審計摘要"""
    # 檢查權限
    if Permission.AUDIT_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    summary = audit_service.get_audit_summary(days)
    return summary


@router.get("/audit/export")
async def export_audit_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    current_user: Dict[str, Any] = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """匯出審計日誌"""
    # 檢查權限
    if Permission.AUDIT_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        # 解析日期
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        exported_data = audit_service.export_audit_logs(
            start_date=start_dt,
            end_date=end_dt,
            format=format
        )
        
        return {
            "status": "success",
            "format": format,
            "data": exported_data,
            "exported_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出審計日誌失敗: {str(e)}")


# 秘密管理 API
@router.post("/secrets/system")
async def store_system_secret(
    secret_data: SecretStoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """儲存系統秘密"""
    # 檢查權限
    if Permission.SYSTEM_SETTINGS_UPDATE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        encrypted_value = secret_manager.store_system_secret(
            key=secret_data.key,
            value=secret_data.value
        )
        
        return {
            "status": "success",
            "message": "系統秘密已加密儲存",
            "key": secret_data.key,
            "encrypted_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存系統秘密失敗: {str(e)}")


@router.get("/secrets/system/{key}")
async def get_system_secret(
    key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """取得系統秘密"""
    # 檢查權限
    if Permission.SYSTEM_SETTINGS_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        decrypted_value = secret_manager.retrieve_system_secret(key)
        
        return {
            "key": key,
            "value": decrypted_value,
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得系統秘密失敗: {str(e)}")


@router.post("/secrets/merchants/{merchant_id}/rotate")
async def rotate_merchant_credentials(
    merchant_id: UUID,
    credential_data: CredentialRotateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """輪替商家憑證"""
    # 檢查權限
    if Permission.MERCHANT_UPDATE not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        updated_credentials = secret_manager.rotate_merchant_credentials(
            merchant_id=merchant_id,
            new_secret=credential_data.new_secret,
            new_token=credential_data.new_token
        )
        
        return {
            "status": "success",
            "message": "商家憑證已輪替",
            "merchant_id": str(merchant_id),
            "rotated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"輪替商家憑證失敗: {str(e)}")


@router.get("/secrets/merchants/{merchant_id}")
async def get_merchant_credentials(
    merchant_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """取得商家憑證"""
    # 檢查權限
    if Permission.MERCHANT_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    try:
        credentials = secret_manager.retrieve_merchant_credentials(merchant_id)
        
        return {
            "merchant_id": str(merchant_id),
            "credentials": credentials,
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得商家憑證失敗: {str(e)}")


@router.get("/secrets/health")
async def secret_manager_health_check(
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """秘密管理健康檢查"""
    health_status = secret_manager.health_check()
    return health_status


@router.get("/secrets/list")
async def list_encrypted_secrets(
    current_user: Dict[str, Any] = Depends(get_current_user),
    secret_manager: SecretManagerService = Depends(get_secret_manager_service)
):
    """列出所有加密秘密"""
    # 檢查權限
    if Permission.SYSTEM_SETTINGS_READ not in [Permission(p) for p in current_user["permissions"]]:
        raise HTTPException(status_code=403, detail="權限不足")
    
    secrets = secret_manager.list_encrypted_secrets()
    return secrets
