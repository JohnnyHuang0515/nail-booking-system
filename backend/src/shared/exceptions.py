"""
Shared Kernel - Exception Hierarchy
所有自定義異常的基礎類別
"""
from typing import Optional, Any


class DomainException(Exception):
    """領域異常基礎類別"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict[str, Any]:
        """轉換為 API 錯誤響應格式"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ApplicationException(Exception):
    """應用層異常基礎類別"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class InfrastructureException(Exception):
    """基礎設施層異常基礎類別"""
    pass


# === 通用領域異常 ===

class EntityNotFoundError(DomainException):
    """實體不存在異常"""
    def __init__(self, entity_type: str, entity_id: Any):
        super().__init__(
            message=f"{entity_type} with id {entity_id} not found",
            error_code="entity_not_found",
            details={"entity_type": entity_type, "entity_id": str(entity_id)}
        )


class InvalidStatusTransitionError(DomainException):
    """無效狀態轉移異常"""
    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            message=f"無法從 {from_status} 轉移至 {to_status}",
            error_code="invalid_status_transition",
            details={"from_status": from_status, "to_status": to_status}
        )


class ValidationError(DomainException):
    """驗證錯誤異常"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"驗證失敗: {field} - {message}",
            error_code="validation_error",
            details={"field": field}
        )


# === 多租戶相關異常 ===

class TenantIsolationViolationError(DomainException):
    """租戶隔離違反異常"""
    def __init__(self, message: str = "租戶資料存取違規"):
        super().__init__(
            message=message,
            error_code="tenant_isolation_violation"
        )


class MerchantInactiveError(ApplicationException):
    """商家停用異常"""
    def __init__(self, merchant_id: str):
        super().__init__(
            message=f"商家 {merchant_id} 已停用，無法執行操作",
            status_code=403,
            error_code="merchant_inactive"
        )


class SubscriptionPastDueError(ApplicationException):
    """訂閱逾期異常"""
    def __init__(self, merchant_id: str):
        super().__init__(
            message=f"商家 {merchant_id} 訂閱已逾期，無法建立新預約",
            status_code=403,
            error_code="subscription_past_due"
        )


# === 認證授權異常 ===

class AuthenticationError(ApplicationException):
    """認證失敗異常"""
    def __init__(self, message: str = "認證失敗"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="authentication_failed"
        )


class PermissionDeniedError(ApplicationException):
    """權限不足異常"""
    def __init__(self, message: str = "權限不足"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="permission_denied"
        )

