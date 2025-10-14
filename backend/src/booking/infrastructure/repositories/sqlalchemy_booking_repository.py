"""
Booking Context - Infrastructure Layer - Repository Implementation
SQLAlchemy Repository 實作（依賴倒置：實作 Domain 定義的介面）
"""
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from booking.domain.models import Booking, BookingItem, BookingStatus, Customer
from booking.domain.repositories import BookingRepository
from booking.domain.value_objects import Money, Duration
from booking.infrastructure.orm.models import BookingORM

logger = logging.getLogger(__name__)


class SQLAlchemyBookingRepository(BookingRepository):
    """
    SQLAlchemy 實作的 Booking Repository
    
    職責：
    1. Domain Model ↔ ORM Model 轉換
    2. 資料庫 CRUD 操作
    3. 租戶隔離（merchant_id 過濾）
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, booking: Booking) -> Booking:
        """儲存預約"""
        # 檢查是否已存在
        existing = self.session.get(BookingORM, booking.id)
        
        if existing:
            # 更新
            self._update_orm_from_domain(existing, booking)
            logger.info(f"Updated booking: {booking.id}")
        else:
            # 新增
            orm_booking = self._domain_to_orm(booking)
            self.session.add(orm_booking)
            logger.info(f"Created booking: {booking.id}")
        
        self.session.flush()  # 刷新以取得 DB 生成欄位
        
        # 重新查詢以確保取得最新狀態
        return self.find_by_id(booking.id, booking.merchant_id)
    
    def find_by_id(self, booking_id: str, merchant_id: str) -> Optional[Booking]:
        """根據 ID 查詢（含租戶隔離）"""
        stmt = select(BookingORM).where(
            and_(
                BookingORM.id == booking_id,
                BookingORM.merchant_id == merchant_id  # 租戶隔離
            )
        )
        
        orm_booking = self.session.scalar(stmt)
        
        if not orm_booking:
            return None
        
        return self._orm_to_domain(orm_booking)
    
    def find_by_merchant(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[BookingStatus] = None
    ) -> list[Booking]:
        """查詢商家的預約"""
        stmt = select(BookingORM).where(
            BookingORM.merchant_id == merchant_id
        )
        
        if start_date:
            stmt = stmt.where(BookingORM.start_at >= datetime.combine(start_date, datetime.min.time()))
        
        if end_date:
            stmt = stmt.where(BookingORM.end_at <= datetime.combine(end_date, datetime.max.time()))
        
        if status:
            stmt = stmt.where(BookingORM.status == status.value)
        
        stmt = stmt.order_by(BookingORM.start_at.desc())
        
        orm_bookings = self.session.scalars(stmt).all()
        return [self._orm_to_domain(orm) for orm in orm_bookings]
    
    def find_by_staff_and_date_range(
        self,
        merchant_id: str,
        staff_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[Booking]:
        """查詢員工在時間範圍內的預約"""
        stmt = select(BookingORM).where(
            and_(
                BookingORM.merchant_id == merchant_id,
                BookingORM.staff_id == staff_id,
                BookingORM.start_at < end_at,
                BookingORM.end_at > start_at,
                BookingORM.status.in_(["confirmed", "pending"])  # 排除已取消/完成
            )
        )
        
        orm_bookings = self.session.scalars(stmt).all()
        return [self._orm_to_domain(orm) for orm in orm_bookings]
    
    def delete(self, booking_id: str, merchant_id: str) -> bool:
        """刪除預約（硬刪除）"""
        stmt = select(BookingORM).where(
            and_(
                BookingORM.id == booking_id,
                BookingORM.merchant_id == merchant_id
            )
        )
        
        orm_booking = self.session.scalar(stmt)
        
        if not orm_booking:
            return False
        
        self.session.delete(orm_booking)
        self.session.flush()
        return True
    
    # === ORM ↔ Domain 轉換 ===
    
    def _orm_to_domain(self, orm: BookingORM) -> Booking:
        """ORM Model → Domain Model"""
        # 轉換 items JSON 為 BookingItem 物件
        items = []
        for item_data in orm.items:
            item = BookingItem(
                service_id=item_data["service_id"],
                service_name=item_data["service_name"],
                service_price=Money(
                    amount=Decimal(str(item_data["service_price"])),
                    currency=item_data.get("currency", "TWD")
                ),
                service_duration=Duration(minutes=item_data["service_duration_minutes"]),
                option_ids=item_data.get("option_ids", []),
                option_names=item_data.get("option_names", []),
                option_prices=[
                    Money(amount=Decimal(str(p))) 
                    for p in item_data.get("option_prices", [])
                ],
                option_durations=[
                    Duration(minutes=d) 
                    for d in item_data.get("option_durations_minutes", [])
                ]
            )
            items.append(item)
        
        # 轉換 customer JSON 為 Customer 物件
        customer = Customer(
            line_user_id=orm.customer.get("line_user_id"),
            name=orm.customer.get("name"),
            phone=orm.customer.get("phone"),
            email=orm.customer.get("email")
        )
        
        return Booking(
            id=orm.id,
            merchant_id=orm.merchant_id,
            customer=customer,
            staff_id=orm.staff_id,
            start_at=orm.start_at,
            items=items,
            status=BookingStatus(orm.status),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            cancelled_at=orm.cancelled_at,
            completed_at=orm.completed_at,
            notes=orm.notes
        )
    
    def _domain_to_orm(self, domain: Booking) -> BookingORM:
        """Domain Model → ORM Model"""
        # 序列化 items
        items_json = []
        for item in domain.items:
            items_json.append({
                "service_id": item.service_id,
                "service_name": item.service_name,
                "service_price": float(item.service_price.amount),
                "currency": item.service_price.currency,
                "service_duration_minutes": item.service_duration.minutes,
                "option_ids": item.option_ids,
                "option_names": item.option_names,
                "option_prices": [float(p.amount) for p in item.option_prices],
                "option_durations_minutes": [d.minutes for d in item.option_durations]
            })
        
        # 序列化 customer
        customer_json = {
            "line_user_id": domain.customer.line_user_id,
            "name": domain.customer.name,
            "phone": domain.customer.phone,
            "email": domain.customer.email
        }
        
        return BookingORM(
            id=domain.id,
            merchant_id=domain.merchant_id,
            staff_id=domain.staff_id,
            status=domain.status.value,
            start_at=domain.start_at,
            end_at=domain.end_at,  # 計算欄位
            customer=customer_json,
            items=items_json,
            total_price_amount=domain.total_price().amount,
            total_price_currency=domain.total_price().currency,
            total_duration_minutes=domain.total_duration().minutes,
            notes=domain.notes,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            cancelled_at=domain.cancelled_at,
            completed_at=domain.completed_at
        )
    
    def _update_orm_from_domain(self, orm: BookingORM, domain: Booking):
        """更新 ORM 欄位（用於 UPDATE）"""
        orm.status = domain.status.value
        orm.updated_at = domain.updated_at
        orm.cancelled_at = domain.cancelled_at
        orm.completed_at = domain.completed_at
        orm.notes = domain.notes

