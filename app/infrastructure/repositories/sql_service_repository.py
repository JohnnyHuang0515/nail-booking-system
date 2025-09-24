import uuid
from sqlalchemy.orm import Session

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
        orm_service = self.session.query(OrmService).filter(OrmService.id == service_id).first()
        if orm_service:
            return DomainService.model_validate(orm_service)
        return None

    def list(self) -> list[DomainService]:
        orm_services = self.session.query(OrmService).all()
        return [DomainService.model_validate(s) for s in orm_services]

    def update(self, service: DomainService) -> None:
        orm_service = self.session.query(OrmService).filter(OrmService.id == service.id).first()
        if orm_service:
            update_data = service.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(orm_service, key, value)
            self.session.add(orm_service)
            self.session.commit()

    def delete(self, service_id: uuid.UUID) -> None:
        orm_service = self.session.query(OrmService).filter(OrmService.id == service_id).first()
        if orm_service:
            self.session.delete(orm_service)
            self.session.commit()
