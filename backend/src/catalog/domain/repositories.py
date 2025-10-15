"""
Catalog Context - Domain Layer - Repository Interfaces
"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from .models import Service, Staff, StaffHoliday


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
    
    # ========== Staff Holiday Management ==========
    
    @abstractmethod
    def save_staff_holiday(self, holiday: StaffHoliday) -> StaffHoliday:
        """儲存美甲師休假"""
        pass
    
    @abstractmethod
    def find_staff_holidays(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        staff_id: Optional[int] = None
    ) -> list[StaffHoliday]:
        """查詢美甲師休假"""
        pass
    
    @abstractmethod
    def find_staff_holiday_by_id(self, holiday_id: int, merchant_id: str) -> Optional[StaffHoliday]:
        """根據 ID 查詢美甲師休假"""
        pass
    
    @abstractmethod
    def delete_staff_holiday(self, holiday_id: int, merchant_id: str) -> bool:
        """刪除美甲師休假"""
        pass

