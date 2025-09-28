import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.booking.models import Service as DomainService
from app.domain.booking.service_repository import AbstractServiceRepository
from app.infrastructure.database.models import Service as OrmService


class SqlServiceRepository(AbstractServiceRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, service: DomainService) -> None:
        orm_service = OrmService(**service.model_dump())
        self.session.add(orm_service)
        self.session.commit()
        self.session.refresh(orm_service)

    def get_by_id(self, service_id: uuid.UUID) -> DomainService | None:
        stmt = select(OrmService).where(OrmService.id == service_id)
        orm_service = self.session.execute(stmt).scalar_one_or_none()
        if orm_service:
            return DomainService.model_validate(orm_service)
        return None

    def list(self) -> List[DomainService]:
        stmt = select(OrmService).where(OrmService.is_active == True)
        orm_services = self.session.execute(stmt).scalars().all()
        return [DomainService.model_validate(s) for s in orm_services]

    def list_by_merchant(self, merchant_id: uuid.UUID) -> List[DomainService]:
        """列出指定商家的所有服務"""
        stmt = select(OrmService).where(
            OrmService.merchant_id == merchant_id,
            OrmService.is_active == True
        )
        orm_services = self.session.execute(stmt).scalars().all()
        return [DomainService.model_validate(s) for s in orm_services]

    def find_by_id(self, service_id: uuid.UUID) -> OrmService | None:
        """根據ID查找服務（返回ORM對象）"""
        stmt = select(OrmService).where(
            OrmService.id == service_id,
            OrmService.is_active == True
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def update(self, service: DomainService) -> None:
        stmt = select(OrmService).where(OrmService.id == service.id)
        orm_service = self.session.execute(stmt).scalar_one_or_none()
        if orm_service:
            update_data = service.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(orm_service, key, value)
            self.session.add(orm_service)
            self.session.commit()

    def delete(self, service_id: uuid.UUID) -> None:
        stmt = select(OrmService).where(OrmService.id == service_id)
        orm_service = self.session.execute(stmt).scalar_one_or_none()
        if orm_service:
            self.session.delete(orm_service)
            self.session.commit()
