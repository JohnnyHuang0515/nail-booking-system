"""
Shared Kernel - Event Bus
領域事件發布/訂閱機制（簡易版，未來可替換為 RabbitMQ/Kafka）
"""
from typing import Callable, Any
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """領域事件基礎類別"""
    event_id: str
    occurred_at: datetime
    aggregate_id: str
    aggregate_type: str
    event_type: str
    payload: dict[str, Any]


class EventBus:
    """
    簡易的記憶體事件總線
    
    注意：此為 MVP 實作，生產環境應替換為：
    - Celery + Redis
    - RabbitMQ
    - AWS EventBridge
    """
    
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]):
        """
        訂閱事件
        
        用法：
            event_bus.subscribe("BookingConfirmed", send_line_notification)
        """
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to {event_type}")
    
    def publish(self, event: DomainEvent):
        """
        發布事件
        
        用法：
            event = BookingConfirmedEvent(...)
            event_bus.publish(event)
        """
        event_type = event.event_type
        handlers = self._handlers.get(event_type, [])
        
        logger.info(f"Publishing event: {event_type} (aggregate_id={event.aggregate_id})")
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Event handler failed: {handler.__name__} for {event_type}",
                    exc_info=e
                )
                # 不中斷其他 handler
    
    def clear_handlers(self):
        """清除所有 handler（用於測試）"""
        self._handlers.clear()


# 全局 EventBus 實例
event_bus = EventBus()

