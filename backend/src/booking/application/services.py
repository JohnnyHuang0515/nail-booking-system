"""
Booking Context - Application Layer - Services
BookingService: 預約業務邏輯協調者
"""
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Optional
import logging

from booking.domain.models import Booking, BookingItem, BookingLock, BookingStatus, Customer
from booking.domain.repositories import BookingRepository, BookingLockRepository
from booking.domain.value_objects import Money, Duration, TimeSlot
from booking.domain.events import (
    BookingConfirmedEvent,
    BookingCancelledEvent,
    BookingCompletedEvent
)
from booking.domain.exceptions import (
    BookingOverlapError,
    StaffInactiveError,
    ServiceInactiveError,
    OutsideWorkingHoursError,
    InvalidTimeSlotError
)
from shared.exceptions import (
    EntityNotFoundError,
    MerchantInactiveError,
    SubscriptionPastDueError,
    PermissionDeniedError
)
from shared.event_bus import event_bus

logger = logging.getLogger(__name__)


class BookingService:
    """
    預約應用服務
    
    職責：
    1. 協調多個聚合（Booking, Catalog, Merchant, Billing）
    2. 執行業務規則驗證
    3. 發布領域事件
    4. 管理交易邊界
    """
    
    def __init__(
        self,
        booking_repo: BookingRepository,
        booking_lock_repo: BookingLockRepository,
        catalog_service: Optional["CatalogService"] = None,  # Catalog Context
        merchant_service: Optional["MerchantService"] = None,  # Merchant Context
        billing_service: Optional["BillingService"] = None  # Billing Context
    ):
        self.booking_repo = booking_repo
        self.booking_lock_repo = booking_lock_repo
        self.catalog_service = catalog_service
        self.merchant_service = merchant_service
        self.billing_service = billing_service
    
    async def create_booking(
        self,
        merchant_id: str,
        customer: Customer,
        staff_id: int,
        start_at: datetime,
        items_data: list[dict],  # [{"service_id": 1, "option_ids": [1,2]}]
        notes: Optional[str] = None
    ) -> Booking:
        """
        建立預約
        
        交易流程（強一致性）：
        1. 驗證商家狀態與訂閱
        2. 驗證員工與服務
        3. 計算總價與總時長
        4. 檢查時段可用性
        5. 建立 BookingLock（EXCLUDE 約束保證無重疊）
        6. 建立 Booking
        7. 關聯 Lock 到 Booking
        8. 發布 BookingConfirmed 事件
        9. 提交交易
        
        失敗時完全回滾，確保無殘留 lock
        
        Raises:
            MerchantInactiveError: 商家停用
            SubscriptionPastDueError: 訂閱逾期
            StaffInactiveError: 員工停用
            ServiceInactiveError: 服務停用
            BookingOverlapError: 時段重疊
            OutsideWorkingHoursError: 超出工作時間
        """
        
        # === STEP 1: 驗證商家狀態 ===
        if self.merchant_service:
            # 使用真實的 MerchantService 驗證商家狀態
            self.merchant_service.validate_merchant_active(merchant_id)
        else:
            # Fallback: 跳過商家驗證（向後相容）
            pass
        
        # === STEP 2: 驗證訂閱狀態 ===
        if self.billing_service:
            # 使用真實的 BillingService 驗證訂閱狀態
            self.billing_service.validate_can_create_booking(merchant_id)
        else:
            # Fallback: 跳過訂閱驗證（向後相容）
            pass
        
        # === STEP 3: 驗證員工與服務，計算價格時長 ===
        booking_items = []
        
        if self.catalog_service:
            # 使用真實的 CatalogService
            for item_data in items_data:
                # 驗證員工可執行此服務
                await self.catalog_service.validate_staff_can_perform_service(
                    staff_id=staff_id,
                    service_id=item_data["service_id"],
                    merchant_id=merchant_id
                )
                
                # 建構 BookingItem
                booking_item = await self.catalog_service.build_booking_item(
                    service_id=item_data["service_id"],
                    option_ids=item_data.get("option_ids", []),
                    merchant_id=merchant_id
                )
                booking_items.append(booking_item)
        else:
            # Fallback: 使用模擬資料（向後相容）
            booking_items = self._build_booking_items_mock(items_data)
        
        # === STEP 4: 計算總時長，確定 end_at ===
        total_duration = Duration.zero()
        for item in booking_items:
            total_duration = total_duration + item.total_duration()
        
        end_at = start_at + total_duration.to_timedelta()
        
        # === STEP 5: 檢查時段衝突（應用層預檢查）===
        overlapping_locks = self.booking_lock_repo.find_overlapping_locks(
            merchant_id=merchant_id,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at
        )
        
        if overlapping_locks:
            raise BookingOverlapError(
                staff_id=staff_id,
                start_at=start_at,
                end_at=end_at,
                conflicting_booking_id=overlapping_locks[0].booking_id
            )
        
        # === STEP 6: 建立 BookingLock（DB 層保證）===
        lock = BookingLock.create_for_booking(
            merchant_id=merchant_id,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at
        )
        
        try:
            created_lock = self.booking_lock_repo.create_lock(lock)
        except Exception as e:
            # PostgreSQL EXCLUDE 約束違反
            if "exclusion" in str(e).lower():
                raise BookingOverlapError(
                    staff_id=staff_id,
                    start_at=start_at,
                    end_at=end_at
                )
            raise
        
        # === STEP 7: 建立 Booking 聚合 ===
        booking = Booking.create_new(
            merchant_id=merchant_id,
            customer=customer,
            staff_id=staff_id,
            start_at=start_at,
            items=booking_items,
            notes=notes
        )
        
        saved_booking = self.booking_repo.save(booking)
        
        # === STEP 8: 關聯 Lock 到 Booking ===
        self.booking_lock_repo.link_to_booking(
            lock_id=created_lock.id,
            booking_id=saved_booking.id
        )
        
        # === STEP 9: 發布領域事件 ===
        event = BookingConfirmedEvent.create(
            booking_id=saved_booking.id,
            merchant_id=merchant_id,
            payload={
                "customer": {
                    "line_user_id": customer.line_user_id,
                    "name": customer.name
                },
                "staff_id": staff_id,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "total_price": float(saved_booking.total_price().amount)
            }
        )
        event_bus.publish(event)
        
        # === STEP 10: 觸發通知（LINE 推播）===
        # 簡化版：直接調用 NotificationService（實際環境應由 EventBus 非同步處理）
        if self.merchant_service:
            try:
                from notification.application.services import NotificationService
                
                merchant = self.merchant_service.get_merchant(merchant_id)
                notification_service = NotificationService()
                
                # 提取服務名稱
                service_names = [item.service_name for item in saved_booking.items]
                service_name = service_names[0] if service_names else "預約服務"
                
                notification_service.send_booking_confirmed_notification(
                    merchant=merchant,
                    customer_line_user_id=customer.line_user_id,
                    customer_name=customer.name or "客戶",
                    booking_id=saved_booking.id,
                    start_at=start_at.strftime("%Y-%m-%d %H:%M"),
                    service_name=service_name
                )
                
                logger.info(f"✅ LINE 通知已發送: {saved_booking.id}")
            except Exception as e:
                # 通知失敗不影響預約建立
                logger.warning(f"⚠️  LINE 通知發送失敗（不影響預約）: {e}")
        
        logger.info(f"Booking created: {saved_booking.id}")
        return saved_booking
    
    def _build_booking_items_mock(self, items_data: list[dict]) -> list[BookingItem]:
        """
        建立 BookingItem（暫時模擬，待 Catalog Context 實作）
        
        TODO: 替換為實際的 CatalogService 查詢
        """
        booking_items = []
        
        for item_data in items_data:
            service_id = item_data["service_id"]
            option_ids = item_data.get("option_ids", [])
            
            # 模擬資料
            booking_item = BookingItem(
                service_id=service_id,
                service_name=f"測試服務 {service_id}",
                service_price=Money(amount=Decimal("800"), currency="TWD"),
                service_duration=Duration(minutes=60),
                option_ids=option_ids,
                option_names=[f"選項 {oid}" for oid in option_ids],
                option_prices=[Money(amount=Decimal("200")) for _ in option_ids],
                option_durations=[Duration(minutes=15) for _ in option_ids]
            )
            booking_items.append(booking_item)
        
        return booking_items
    
    async def cancel_booking(
        self,
        booking_id: str,
        merchant_id: str,
        requester_line_id: str,
        reason: str = ""
    ) -> Booking:
        """
        取消預約
        
        驗證：
        1. 預約存在
        2. 屬於正確的商家（租戶隔離）
        3. 請求者是預約擁有者
        4. 狀態允許取消
        
        Raises:
            EntityNotFoundError: 預約不存在
            PermissionDeniedError: 無權取消
            BookingAlreadyCompletedError: 已完成無法取消
        """
        booking = self.booking_repo.find_by_id(booking_id, merchant_id)
        
        if not booking:
            raise EntityNotFoundError("Booking", booking_id)
        
        # 驗證權限：商家或預約擁有者可取消
        is_merchant = requester_line_id == "merchant"
        is_owner = booking.customer.line_user_id == requester_line_id
        
        if not (is_merchant or is_owner):
            raise PermissionDeniedError("只有預約擁有者或商家可以取消預約")
        
        # 執行取消（狀態檢查在 Domain 內）
        booking.cancel(cancelled_by=requester_line_id, reason=reason)
        
        # 儲存
        updated_booking = self.booking_repo.save(booking)
        
        # 發布事件
        event = BookingCancelledEvent.create(
            booking_id=booking_id,
            merchant_id=merchant_id,
            cancelled_by=requester_line_id,
            reason=reason
        )
        event_bus.publish(event)
        
        logger.info(f"Booking cancelled: {booking_id}")
        return updated_booking
    
    async def get_booking(
        self,
        booking_id: str,
        merchant_id: str
    ) -> Optional[Booking]:
        """查詢預約（租戶隔離）"""
        return self.booking_repo.find_by_id(booking_id, merchant_id)
    
    async def list_bookings(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[BookingStatus] = None
    ) -> list[Booking]:
        """列出商家的預約"""
        return self.booking_repo.find_by_merchant(
            merchant_id=merchant_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
    
    async def calculate_available_slots(
        self,
        merchant_id: str,
        staff_id: int,
        target_date: date,
        service_duration_min: int = 60,
        interval_min: int = 30
    ) -> list[dict]:
        """
        計算可訂時段
        
        演算法：
        1. 取得員工工作時間
        2. 取得已預約時段
        3. 計算空閒時段
        4. 切片為 interval_min 間隔
        5. 過濾出 >= service_duration_min 的時段
        
        Returns:
            [{"start_time": "14:00", "end_time": "15:00", "available": True}, ...]
        """
        # 設定時區（台北時間 UTC+8）
        from datetime import timezone, timedelta
        tz = timezone(timedelta(hours=8))  # Asia/Taipei
        
        # 檢查是否為休假日
        if self.catalog_service:
            holidays = await self.catalog_service.list_holidays(
                merchant_id=merchant_id,
                start_date=target_date,
                end_date=target_date
            )
            
            # 檢查目標日期是否為休假日（包含重複休假日）
            for holiday in holidays:
                if holiday.is_on_date(target_date):
                    # 休假日，無可用時段
                    return []
        
        # 取得員工工時
        if self.catalog_service:
            staff = await self.catalog_service.get_staff(staff_id, merchant_id)
            
            # 取得當天工時
            day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
            from catalog.domain.models import DayOfWeek
            working_hours = staff.get_working_hours_for_day(DayOfWeek(day_of_week))
            
            if not working_hours:
                # 該天無工作時間
                return []
            
            working_start = datetime.combine(target_date, working_hours.start_time, tzinfo=tz)
            working_end = datetime.combine(target_date, working_hours.end_time, tzinfo=tz)
        else:
            # Fallback: 固定工時 10:00-18:00
            working_start = datetime.combine(target_date, time(10, 0), tzinfo=tz)
            working_end = datetime.combine(target_date, time(18, 0), tzinfo=tz)
        
        # 取得當天所有預約
        day_start = datetime.combine(target_date, time(0, 0), tzinfo=tz)
        day_end = datetime.combine(target_date, time(23, 59, 59), tzinfo=tz)
        
        bookings = self.booking_repo.find_by_staff_and_date_range(
            merchant_id=merchant_id,
            staff_id=staff_id,
            start_at=day_start,
            end_at=day_end
        )
        
        # 建立已預約時段列表
        booked_slots = [booking.time_slot() for booking in bookings]
        
        # 生成所有可能的時段（間隔為 interval_min）
        slots = []
        current = working_start
        
        while current + timedelta(minutes=service_duration_min) <= working_end:
            slot_end = current + timedelta(minutes=service_duration_min)
            candidate_slot = TimeSlot(start_at=current, end_at=slot_end)
            
            # 檢查是否與已預約時段重疊
            is_available = not any(
                candidate_slot.overlaps(booked_slot)
                for booked_slot in booked_slots
            )
            
            slots.append({
                "start_time": current.strftime("%H:%M"),
                "end_time": slot_end.strftime("%H:%M"),
                "available": is_available,
                "duration_minutes": service_duration_min
            })
            
            current += timedelta(minutes=interval_min)
        
        return slots

