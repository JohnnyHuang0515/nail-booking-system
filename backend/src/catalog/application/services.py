"""
Catalog Context - Application Layer - Services
CatalogService: 服務與員工查詢協調者
"""
from typing import Optional
import logging

from catalog.domain.models import Service, Staff, ServiceOption
from catalog.domain.repositories import ServiceRepository, StaffRepository
from catalog.domain.exceptions import (
    ServiceNotFoundError,
    StaffNotFoundError,
    StaffCannotPerformServiceError
)
from booking.domain.value_objects import Money, Duration
from booking.domain.models import BookingItem

logger = logging.getLogger(__name__)


class CatalogService:
    """
    Catalog 應用服務
    
    職責：
    1. 提供服務查詢
    2. 提供員工查詢
    3. 驗證員工技能與服務匹配
    4. 為 BookingService 建構 BookingItem
    """
    
    def __init__(
        self,
        service_repo: ServiceRepository,
        staff_repo: StaffRepository
    ):
        self.service_repo = service_repo
        self.staff_repo = staff_repo
    
    async def get_service(self, service_id: int, merchant_id: str) -> Service:
        """
        取得服務
        
        Raises:
            ServiceNotFoundError: 服務不存在
        """
        service = self.service_repo.find_by_id(service_id, merchant_id)
        
        if not service:
            raise ServiceNotFoundError(service_id)
        
        return service
    
    async def get_staff(self, staff_id: int, merchant_id: str) -> Staff:
        """
        取得員工
        
        Raises:
            StaffNotFoundError: 員工不存在
        """
        staff = self.staff_repo.find_by_id(staff_id, merchant_id)
        
        if not staff:
            raise StaffNotFoundError(staff_id)
        
        return staff
    
    async def validate_staff_can_perform_service(
        self,
        staff_id: int,
        service_id: int,
        merchant_id: str
    ):
        """
        驗證員工可執行服務
        
        Raises:
            StaffNotFoundError: 員工不存在
            ServiceNotFoundError: 服務不存在
            StaffCannotPerformServiceError: 員工技能不符
        """
        staff = await self.get_staff(staff_id, merchant_id)
        service = await self.get_service(service_id, merchant_id)
        
        if not staff.is_active:
            from booking.domain.exceptions import StaffInactiveError
            raise StaffInactiveError(staff_id)
        
        if not service.is_active:
            from booking.domain.exceptions import ServiceInactiveError
            raise ServiceInactiveError(service_id)
        
        if not staff.can_perform_service(service_id):
            raise StaffCannotPerformServiceError(staff_id, service_id)
    
    async def build_booking_item(
        self,
        service_id: int,
        option_ids: list[int],
        merchant_id: str
    ) -> BookingItem:
        """
        為 BookingService 建構 BookingItem
        
        此方法替換 BookingService._build_booking_items_mock
        
        Args:
            service_id: 服務 ID
            option_ids: 選項 ID 列表
            merchant_id: 商家 ID
        
        Returns:
            BookingItem 實例
        
        Raises:
            ServiceNotFoundError: 服務不存在
        """
        service = await self.get_service(service_id, merchant_id)
        
        # 過濾有效的選項
        selected_options = []
        for option_id in option_ids:
            option = next(
                (opt for opt in service.options if opt.id == option_id and opt.is_active),
                None
            )
            if option:
                selected_options.append(option)
        
        return BookingItem(
            service_id=service.id,
            service_name=service.name,
            service_price=service.base_price,
            service_duration=service.base_duration,
            option_ids=[opt.id for opt in selected_options],
            option_names=[opt.name for opt in selected_options],
            option_prices=[opt.add_price for opt in selected_options],
            option_durations=[opt.add_duration for opt in selected_options]
        )
    
    async def list_services(self, merchant_id: str, is_active_only: bool = True) -> list[Service]:
        """列出商家的服務"""
        return self.service_repo.find_by_merchant(merchant_id, is_active_only)
    
    async def list_staff(self, merchant_id: str, is_active_only: bool = True) -> list[Staff]:
        """列出商家的員工"""
        return self.staff_repo.find_by_merchant(merchant_id, is_active_only)
    
    async def get_staff_for_service(
        self,
        service_id: int,
        merchant_id: str
    ) -> list[Staff]:
        """取得可執行特定服務的員工列表"""
        return self.staff_repo.find_by_service(service_id, merchant_id)

