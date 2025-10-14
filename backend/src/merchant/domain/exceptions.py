"""
Merchant Context - Domain Layer - Exceptions
Merchant 領域專屬異常
"""


class MerchantNotFoundError(Exception):
    """商家不存在"""
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        super().__init__(f"商家不存在: {merchant_id}")


class MerchantInactiveError(Exception):
    """商家未啟用（不可接受預約）"""
    def __init__(self, merchant_id: str, status: str):
        self.merchant_id = merchant_id
        self.status = status
        super().__init__(f"商家 {merchant_id} 狀態為 {status}，無法接受預約")


class MerchantSlugDuplicateError(Exception):
    """商家 slug 重複"""
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"商家 slug 已存在: {slug}")


class InvalidTimezoneError(Exception):
    """無效時區"""
    def __init__(self, timezone: str):
        self.timezone = timezone
        super().__init__(f"無效的時區: {timezone}")

