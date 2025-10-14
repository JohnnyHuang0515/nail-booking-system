"""
Booking Context - Domain Layer - Repository Interfaces
Repository 抽象介面（ABC）- 由 Infrastructure Layer 實作
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from .models import Booking, BookingLock, BookingStatus
from .value_objects import TimeSlot


class BookingRepository(ABC):
    """
    Booking 聚合倉儲介面
    
    設計原則：
    - Domain Layer 僅定義介面
    - Infrastructure Layer 提供 SQLAlchemy 實作
    - 遵循 Repository Pattern + DIP (依賴倒置原則)
    """
    
    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        """
        儲存預約（新增或更新）
        
        Returns:
            儲存後的 Booking（含 DB 生成的欄位）
        """
        pass
    
    @abstractmethod
    def find_by_id(self, booking_id: str, merchant_id: str) -> Optional[Booking]:
        """
        根據 ID 查詢預約
        
        Args:
            booking_id: 預約 ID
            merchant_id: 商家 ID（租戶隔離）
        
        Returns:
            找到的 Booking 或 None
        """
        pass
    
    @abstractmethod
    def find_by_merchant(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[BookingStatus] = None
    ) -> list[Booking]:
        """
        查詢商家的所有預約
        
        Args:
            merchant_id: 商家 ID
            start_date: 開始日期過濾
            end_date: 結束日期過濾
            status: 狀態過濾
        
        Returns:
            預約列表
        """
        pass
    
    @abstractmethod
    def find_by_staff_and_date_range(
        self,
        merchant_id: str,
        staff_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[Booking]:
        """
        查詢員工在特定時間範圍的預約
        
        用途：檢查時段衝突
        
        Args:
            merchant_id: 商家 ID
            staff_id: 員工 ID
            start_at: 開始時間
            end_at: 結束時間
        
        Returns:
            在此範圍內的預約列表
        """
        pass
    
    @abstractmethod
    def delete(self, booking_id: str, merchant_id: str) -> bool:
        """
        刪除預約（軟刪除或硬刪除）
        
        Returns:
            是否成功刪除
        """
        pass


class BookingLockRepository(ABC):
    """
    BookingLock 倉儲介面
    
    用途：在建立 Booking 前先鎖定時段
    """
    
    @abstractmethod
    def create_lock(self, lock: BookingLock) -> BookingLock:
        """
        建立預約鎖定
        
        如果與現有鎖定重疊，PostgreSQL EXCLUDE 約束會拋出異常
        
        Raises:
            psycopg2.errors.ExclusionViolation: 時段重疊
        """
        pass
    
    @abstractmethod
    def find_overlapping_locks(
        self,
        merchant_id: str,
        staff_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[BookingLock]:
        """
        查詢重疊的鎖定
        
        用途：應用層的預檢查（雖然 DB 有約束，但提前檢查可提供更好的錯誤訊息）
        """
        pass
    
    @abstractmethod
    def link_to_booking(self, lock_id: str, booking_id: str) -> bool:
        """
        將鎖定關聯到預約
        
        Args:
            lock_id: 鎖定 ID
            booking_id: 預約 ID
        
        Returns:
            是否成功關聯
        """
        pass
    
    @abstractmethod
    def delete_lock(self, lock_id: str) -> bool:
        """
        刪除鎖定
        
        用途：取消預約時釋放鎖定
        """
        pass

