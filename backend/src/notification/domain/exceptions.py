"""
Notification Context - Domain Layer - Exceptions
Notification 領域專屬異常
"""


class TemplateNotFoundError(Exception):
    """模板不存在"""
    def __init__(self, template_key: str, merchant_id: str):
        self.template_key = template_key
        self.merchant_id = merchant_id
        super().__init__(f"模板不存在: {template_key} (商家: {merchant_id})")


class TemplateRenderError(Exception):
    """模板渲染失敗"""
    def __init__(self, template_key: str, error: str):
        self.template_key = template_key
        super().__init__(f"模板渲染失敗: {template_key}, 錯誤: {error}")


class NotificationSendError(Exception):
    """通知發送失敗"""
    def __init__(self, channel: str, recipient: str, error: str):
        self.channel = channel
        self.recipient = recipient
        super().__init__(
            f"通知發送失敗 ({channel} -> {recipient}): {error}"
        )


class LineCredentialsNotConfiguredError(Exception):
    """LINE 憑證未配置"""
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        super().__init__(f"商家 {merchant_id} 未配置 LINE 憑證")

