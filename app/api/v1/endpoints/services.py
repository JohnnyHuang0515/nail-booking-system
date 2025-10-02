import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.application.service_service import ServiceService
from app.domain.booking.models import Service
from app.api.v1.dependencies import get_service_service, get_current_merchant_from_token

router = APIRouter()


class ServiceCreate(BaseModel):
    name: str
    price: float
    duration_minutes: int
    merchant_id: str
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None


@router.get("/services")
def list_services(
    current_merchant: dict = Depends(get_current_merchant_from_token()),
    service: ServiceService = Depends(get_service_service)
):
    """Get a list of all services."""
    try:
        import uuid
        merchant_uuid = uuid.UUID(current_merchant["id"])
        services = service.get_all_services(merchant_uuid)
        return services
    except Exception as e:
        print(f"Services error: {e}")
        return []


@router.post("/services", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    service: ServiceService = Depends(get_service_service)
):
    """Create a new service."""
    try:
        merchant_uuid = uuid.UUID(service_data.merchant_id)
        return service.create_service(
            name=service_data.name,
            price=service_data.price,
            duration_minutes=service_data.duration_minutes,
            merchant_id=merchant_uuid,
            is_active=service_data.is_active,
        )
    except Exception as e:
        print(f"Create service error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create service: {str(e)}")


@router.put("/services/{service_id}", response_model=Service)
def update_service(
    service_id: uuid.UUID,
    service_data: ServiceUpdate,
    service: ServiceService = Depends(get_service_service)
):
    """Update an existing service."""
    updated_service = service.update_service(
        service_id, **service_data.model_dump(exclude_unset=True)
    )
    if not updated_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated_service


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: uuid.UUID,
    service: ServiceService = Depends(get_service_service)
):
    """Delete a service."""
    if not service.delete_service(service_id):
        raise HTTPException(status_code=404, detail="Service not found")
    return None
