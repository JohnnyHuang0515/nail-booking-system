"""
Catalog Context - Infrastructure Layer - Service Repository
"""
from typing import Optional
from decimal import Decimal
import logging

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_

from catalog.domain.models import Service, ServiceOption, ServiceCategory
from catalog.domain.repositories import ServiceRepository
from catalog.infrastructure.orm.models import ServiceORM, ServiceOptionORM
from booking.domain.value_objects import Money, Duration

logger = logging.getLogger(__name__)


class SQLAlchemyServiceRepository(ServiceRepository):
    """SQLAlchemy 實作的 Service Repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, service: Service) -> Service:
        """儲存服務"""
        existing = self.session.get(ServiceORM, service.id)
        
        if existing:
            self._update_orm_from_domain(existing, service)
            logger.info(f"Updated service: {service.id}")
        else:
            orm_service = self._domain_to_orm(service)
            self.session.add(orm_service)
            logger.info(f"Created service: {service.id}")
        
        self.session.flush()
        return self.find_by_id(service.id, service.merchant_id)
    
    def find_by_id(self, service_id: int, merchant_id: str) -> Optional[Service]:
        """根據 ID 查詢服務（含租戶隔離）"""
        stmt = select(ServiceORM).options(
            joinedload(ServiceORM.options)
        ).where(
            and_(
                ServiceORM.id == service_id,
                ServiceORM.merchant_id == merchant_id
            )
        )
        
        orm_service = self.session.scalar(stmt)
        
        if not orm_service:
            return None
        
        return self._orm_to_domain(orm_service)
    
    def find_by_merchant(self, merchant_id: str, is_active_only: bool = True) -> list[Service]:
        """查詢商家的所有服務"""
        stmt = select(ServiceORM).options(
            joinedload(ServiceORM.options)
        ).where(
            ServiceORM.merchant_id == merchant_id
        )
        
        if is_active_only:
            stmt = stmt.where(ServiceORM.is_active == True)
        
        stmt = stmt.order_by(ServiceORM.id)
        
        orm_services = self.session.scalars(stmt).unique().all()
        return [self._orm_to_domain(orm) for orm in orm_services]
    
    def find_by_ids(self, service_ids: list[int], merchant_id: str) -> list[Service]:
        """批量查詢服務"""
        stmt = select(ServiceORM).options(
            joinedload(ServiceORM.options)
        ).where(
            and_(
                ServiceORM.id.in_(service_ids),
                ServiceORM.merchant_id == merchant_id,
                ServiceORM.is_active == True
            )
        )
        
        orm_services = self.session.scalars(stmt).unique().all()
        return [self._orm_to_domain(orm) for orm in orm_services]
    
    def delete(self, service_id: int, merchant_id: str) -> bool:
        """刪除服務"""
        stmt = select(ServiceORM).where(
            and_(
                ServiceORM.id == service_id,
                ServiceORM.merchant_id == merchant_id
            )
        )
        
        orm_service = self.session.scalar(stmt)
        
        if not orm_service:
            return False
        
        self.session.delete(orm_service)
        self.session.flush()
        return True
    
    # === ORM ↔ Domain 轉換 ===
    
    def _orm_to_domain(self, orm: ServiceORM) -> Service:
        """ORM → Domain"""
        options = []
        for orm_opt in orm.options:
            option = ServiceOption(
                id=orm_opt.id,
                service_id=orm_opt.service_id,
                name=orm_opt.name,
                add_price=Money(
                    amount=Decimal(str(orm_opt.add_price_amount)),
                    currency=orm_opt.add_price_currency
                ),
                add_duration=Duration(minutes=orm_opt.add_duration_minutes),
                is_active=orm_opt.is_active,
                display_order=orm_opt.display_order
            )
            options.append(option)
        
        return Service(
            id=orm.id,
            merchant_id=orm.merchant_id,
            name=orm.name,
            base_price=Money(
                amount=Decimal(str(orm.base_price_amount)),
                currency=orm.base_price_currency
            ),
            base_duration=Duration(minutes=orm.base_duration_minutes),
            category=ServiceCategory(orm.category),
            description=orm.description,
            is_active=orm.is_active,
            allow_stack=orm.allow_stack,
            options=options
        )
    
    def _domain_to_orm(self, domain: Service) -> ServiceORM:
        """Domain → ORM"""
        orm = ServiceORM(
            id=domain.id,
            merchant_id=domain.merchant_id,
            name=domain.name,
            category=domain.category.value,
            description=domain.description,
            base_price_amount=domain.base_price.amount,
            base_price_currency=domain.base_price.currency,
            base_duration_minutes=domain.base_duration.minutes,
            is_active=domain.is_active,
            allow_stack=domain.allow_stack
        )
        
        # 轉換 options
        for opt in domain.options:
            orm_opt = ServiceOptionORM(
                id=opt.id,
                service_id=opt.service_id,
                name=opt.name,
                add_price_amount=opt.add_price.amount,
                add_price_currency=opt.add_price.currency,
                add_duration_minutes=opt.add_duration.minutes,
                is_active=opt.is_active,
                display_order=opt.display_order
            )
            orm.options.append(orm_opt)
        
        return orm
    
    def _update_orm_from_domain(self, orm: ServiceORM, domain: Service):
        """更新 ORM（用於 UPDATE）"""
        orm.name = domain.name
        orm.category = domain.category.value
        orm.description = domain.description
        orm.base_price_amount = domain.base_price.amount
        orm.base_duration_minutes = domain.base_duration.minutes
        orm.is_active = domain.is_active
        orm.allow_stack = domain.allow_stack

