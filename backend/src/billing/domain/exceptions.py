"""
Billing Context - Domain Layer - Exceptions
Billing 領域專屬異常
"""


class SubscriptionNotFoundError(Exception):
    """訂閱不存在"""
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        super().__init__(f"訂閱不存在: {subscription_id}")


class NoActiveSubscriptionError(Exception):
    """商家無啟用訂閱"""
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        super().__init__(f"商家 {merchant_id} 無啟用訂閱")


class SubscriptionPastDueError(Exception):
    """訂閱逾期（功能降級）"""
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        super().__init__(f"商家 {merchant_id} 訂閱逾期，無法建立新預約")


class PlanNotFoundError(Exception):
    """方案不存在"""
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        super().__init__(f"方案不存在: {plan_id}")


class QuotaExceededError(Exception):
    """超過方案額度"""
    def __init__(self, resource: str, limit: int, current: int):
        self.resource = resource
        self.limit = limit
        self.current = current
        super().__init__(
            f"超過 {resource} 額度：當前 {current}，上限 {limit}"
        )

