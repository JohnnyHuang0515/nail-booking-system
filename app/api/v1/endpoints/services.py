import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.application.service_service import ServiceService
from app.domain.booking.models import Service
from app.api.v1.dependencies import get_service_service, get_current_merchant_from_token
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

# 可選的認證依賴
def get_optional_merchant_auth():
    """可選的商家認證依賴"""
    security = HTTPBearer(auto_error=False)
    
    def _get_optional_merchant(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[dict]:
        if not credentials:
            return None
        
        try:
            # 嘗試使用現有的認證邏輯
            return get_current_merchant_from_token()(credentials)
        except:
            return None
    
    return _get_optional_merchant


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
    merchant_id: Optional[str] = None,
    current_merchant: Optional[dict] = Depends(get_optional_merchant_auth()),
    service: ServiceService = Depends(get_service_service)
):
    """Get a list of all services."""
    try:
        import uuid
        # 如果提供了 merchant_id 參數，使用它（公開訪問）
        if merchant_id:
            merchant_uuid = uuid.UUID(merchant_id)
        else:
            # 否則使用認證的商家 ID（後台管理）
            if not current_merchant:
                raise HTTPException(status_code=401, detail="需要認證或提供 merchant_id 參數")
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
    except ValueError as e:
        print(f"Create service validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"驗證錯誤: {str(e)}"
        )
    except Exception as e:
        print(f"Create service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"建立服務失敗: {str(e)}"
        )


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
