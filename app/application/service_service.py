from typing import List
import uuid
from app.domain.booking.models import Service
from app.domain.booking.service_repository import AbstractServiceRepository


class ServiceService:
    def __init__(self, service_repo: AbstractServiceRepository):
        self.service_repo = service_repo

    def get_all_services(self, merchant_id: uuid.UUID = None) -> List[Service]:
        if merchant_id:
            return self.service_repo.list_by_merchant(merchant_id)
        return self.service_repo.list()

    def create_service(self, name: str, price: float, duration_minutes: int, merchant_id: uuid.UUID, is_active: bool = True) -> Service:
        service = Service(name=name, price=price, duration_minutes=duration_minutes, merchant_id=merchant_id, is_active=is_active)
        self.service_repo.add(service)
        return service

    def update_service(self, service_id: uuid.UUID, **kwargs) -> Service | None:
        service = self.service_repo.get_by_id(service_id)
        if service:
            updated_service = service.model_copy(update=kwargs)
            self.service_repo.update(updated_service)
            return updated_service
        return None

    def delete_service(self, service_id: uuid.UUID) -> bool:
        service = self.service_repo.get_by_id(service_id)
        if service:
            self.service_repo.delete(service_id)
            return True
        return False
