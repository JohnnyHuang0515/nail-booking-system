"""
Catalog Context - Domain Layer - Repository Interfaces
"""
from abc import ABC, abstractmethod
from typing import Optional

from .models import Service, Staff


class ServiceRepository(ABC):
    """服務倉儲介面"""
    
    @abstractmethod
    def save(self, service: Service) -> Service:
        """儲存服務"""
        pass
    
    @abstractmethod
    def find_by_id(self, service_id: int, merchant_id: str) -> Optional[Service]:
        """根據 ID 查詢服務（含租戶隔離）"""
        pass
    
    @abstractmethod
    def find_by_merchant(self, merchant_id: str, is_active_only: bool = True) -> list[Service]:
        """查詢商家的所有服務"""
        pass
    
    @abstractmethod
    def find_by_ids(self, service_ids: list[int], merchant_id: str) -> list[Service]:
        """批量查詢服務"""
        pass
    
    @abstractmethod
    def delete(self, service_id: int, merchant_id: str) -> bool:
        """刪除服務"""
        pass


class StaffRepository(ABC):
    """員工倉儲介面"""
    
    @abstractmethod
    def save(self, staff: Staff) -> Staff:
        """儲存員工"""
        pass
    
    @abstractmethod
    def find_by_id(self, staff_id: int, merchant_id: str) -> Optional[Staff]:
        """根據 ID 查詢員工（含租戶隔離）"""
        pass
    
    @abstractmethod
    def find_by_merchant(self, merchant_id: str, is_active_only: bool = True) -> list[Staff]:
        """查詢商家的所有員工"""
        pass
    
    @abstractmethod
    def find_by_service(self, service_id: int, merchant_id: str) -> list[Staff]:
        """查詢可執行特定服務的員工"""
        pass
    
    @abstractmethod
    def delete(self, staff_id: int, merchant_id: str) -> bool:
        """刪除員工"""
        pass

