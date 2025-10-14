"""
Identity Context - Domain Layer - Exceptions
Identity 領域專屬異常
"""


class UserNotFoundError(Exception):
    """用戶不存在"""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"用戶不存在: {identifier}")


class UserInactiveError(Exception):
    """用戶未啟用"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"用戶 {user_id} 未啟用")


class InvalidCredentialsError(Exception):
    """無效的登入憑證"""
    def __init__(self):
        super().__init__("email 或密碼錯誤")


class EmailAlreadyExistsError(Exception):
    """Email 已存在"""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email 已存在: {email}")


class PermissionDeniedError(Exception):
    """權限不足"""
    def __init__(self, user_id: str, permission: str):
        self.user_id = user_id
        self.permission = permission
        super().__init__(f"用戶 {user_id} 無 {permission} 權限")


class TenantBoundaryViolationError(Exception):
    """租戶邊界越權"""
    def __init__(self, user_id: str, requested_merchant_id: str):
        self.user_id = user_id
        self.requested_merchant_id = requested_merchant_id
        super().__init__(
            f"用戶 {user_id} 無權訪問商家 {requested_merchant_id}"
        )

