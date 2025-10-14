"""
Notification Context - Application Layer - Event Handlers
訂閱並處理領域事件
"""
import logging
from typing import TYPE_CHECKING

from booking.domain.events import BookingConfirmedEvent, BookingCancelledEvent
from notification.application.services import NotificationService

if TYPE_CHECKING:
    from merchant.domain.models import Merchant


logger = logging.getLogger(__name__)


class BookingEventHandler:
    """
    預約事件處理器
    
    訂閱 Booking Context 的領域事件並發送通知
    """
    
    def __init__(
        self,
        notification_service: NotificationService
    ):
        self.notification_service = notification_service
    
    def handle_booking_confirmed(
        self,
        event: BookingConfirmedEvent,
        merchant: "Merchant"
    ):
        """
        處理預約確認事件
        
        Args:
            event: BookingConfirmedEvent
            merchant: Merchant 聚合（需從外部注入）
        """
        logger.info(f"處理預約確認事件: {event.booking_id}")
        
        try:
            self.notification_service.send_booking_confirmed_notification(
                merchant=merchant,
                customer_line_user_id=event.customer_line_user_id,
                customer_name=event.customer_name,
                booking_id=event.booking_id,
                start_at=event.start_at.strftime("%Y-%m-%d %H:%M"),
                service_name=event.service_names[0] if event.service_names else "服務"
            )
        except Exception as e:
            logger.error(f"發送預約確認通知失敗: {e}")
    
    def handle_booking_cancelled(
        self,
        event: BookingCancelledEvent,
        merchant: "Merchant"
    ):
        """
        處理預約取消事件
        
        Args:
            event: BookingCancelledEvent
            merchant: Merchant 聚合（需從外部注入）
        """
        logger.info(f"處理預約取消事件: {event.booking_id}")
        
        try:
            self.notification_service.send_booking_cancelled_notification(
                merchant=merchant,
                customer_line_user_id=event.customer_line_user_id,
                customer_name=event.customer_name,
                booking_id=event.booking_id,
                start_at=event.start_at.strftime("%Y-%m-%d %H:%M"),
                service_name="您的服務"  # 簡化：BookingCancelledEvent 未包含 service_names
            )
        except Exception as e:
            logger.error(f"發送預約取消通知失敗: {e}")

