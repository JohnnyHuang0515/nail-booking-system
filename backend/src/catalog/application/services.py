"""
Catalog Context - Application Layer - Services
CatalogService: 服務與員工查詢協調者
"""
from typing import Optional
from datetime import date
import logging

from catalog.domain.models import Service, Staff, ServiceOption, StaffHoliday
from catalog.domain.holiday import Holiday
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
        staff_repo: StaffRepository,
        holiday_repo: Optional['SQLAlchemyHolidayRepository'] = None
    ):
        self.service_repo = service_repo
        self.staff_repo = staff_repo
        self.holiday_repo = holiday_repo
    
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
    
    async def create_staff(
        self,
        merchant_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        skills: Optional[list[int]] = None,
        is_active: bool = True
    ) -> Staff:
        """
        新增員工
        
        Args:
            merchant_id: 商家 ID
            name: 員工姓名
            email: Email
            phone: 電話
            skills: 技能（服務ID列表）
            is_active: 是否啟用
        
        Returns:
            新建的 Staff 實例
        """
        # 生成新的 staff_id（實際應用中可能由資料庫自動生成）
        staff = Staff(
            id=0,  # 將由資料庫生成
            merchant_id=merchant_id,
            name=name,
            email=email,
            phone=phone,
            is_active=is_active,
            skills=skills or [],
            working_hours=[]  # 可以後續設定
        )
        
        return self.staff_repo.save(staff)
    
    async def update_staff(
        self,
        staff_id: int,
        merchant_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        skills: Optional[list[int]] = None,
        is_active: Optional[bool] = None
    ) -> Staff:
        """
        更新員工資訊
        
        Args:
            staff_id: 員工 ID
            merchant_id: 商家 ID
            name: 員工姓名
            email: Email
            phone: 電話
            skills: 技能（服務ID列表）
            is_active: 是否啟用
        
        Returns:
            更新後的 Staff 實例
        
        Raises:
            StaffNotFoundError: 員工不存在
        """
        staff = await self.get_staff(staff_id, merchant_id)
        
        if name is not None:
            staff.name = name
        if email is not None:
            staff.email = email
        if phone is not None:
            staff.phone = phone
        if skills is not None:
            staff.skills = skills
        if is_active is not None:
            staff.is_active = is_active
        
        return self.staff_repo.save(staff)
    
    async def delete_staff(self, staff_id: int, merchant_id: str) -> None:
        """
        刪除員工（軟刪除：設為 is_active=False）
        
        Args:
            staff_id: 員工 ID
            merchant_id: 商家 ID
        
        Raises:
            StaffNotFoundError: 員工不存在
        """
        staff = await self.get_staff(staff_id, merchant_id)
        staff.is_active = False
        self.staff_repo.save(staff)
    
    # ========== Holiday Management ==========
    
    async def create_holiday(
        self,
        merchant_id: str,
        holiday_date: date,
        name: str,
        is_recurring: bool = False
    ) -> Holiday:
        """
        創建休假日
        
        Args:
            merchant_id: 商家 ID
            holiday_date: 休假日期
            name: 休假名稱
            is_recurring: 是否每年重複
        
        Returns:
            Holiday: 創建的休假日
        """
        if not self.holiday_repo:
            raise RuntimeError("Holiday repository not initialized")
        
        holiday = Holiday(
            id=None,
            merchant_id=merchant_id,
            holiday_date=holiday_date,
            name=name,
            is_recurring=is_recurring
        )
        
        return self.holiday_repo.save(holiday)
    
    async def list_holidays(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[Holiday]:
        """
        查詢商家的休假日
        
        Args:
            merchant_id: 商家 ID
            start_date: 開始日期（可選，用於範圍查詢）
            end_date: 結束日期（可選，用於範圍查詢）
        
        Returns:
            list[Holiday]: 休假日列表
        """
        if not self.holiday_repo:
            return []
        
        if start_date and end_date:
            return self.holiday_repo.find_by_date_range(merchant_id, start_date, end_date)
        else:
            return self.holiday_repo.find_by_merchant(merchant_id)
    
    async def get_holiday(self, holiday_id: int, merchant_id: str) -> Holiday:
        """
        取得單一休假日
        
        Args:
            holiday_id: 休假日 ID
            merchant_id: 商家 ID
        
        Returns:
            Holiday: 休假日
        
        Raises:
            ValueError: 休假日不存在
        """
        if not self.holiday_repo:
            raise RuntimeError("Holiday repository not initialized")
        
        holiday = self.holiday_repo.find_by_id(holiday_id, merchant_id)
        if not holiday:
            raise ValueError(f"Holiday not found: {holiday_id}")
        
        return holiday
    
    async def update_holiday(
        self,
        holiday_id: int,
        merchant_id: str,
        holiday_date: Optional[date] = None,
        name: Optional[str] = None,
        is_recurring: Optional[bool] = None
    ) -> Holiday:
        """
        更新休假日
        
        Args:
            holiday_id: 休假日 ID
            merchant_id: 商家 ID
            holiday_date: 休假日期（可選）
            name: 休假名稱（可選）
            is_recurring: 是否每年重複（可選）
        
        Returns:
            Holiday: 更新後的休假日
        """
        if not self.holiday_repo:
            raise RuntimeError("Holiday repository not initialized")
        
        holiday = await self.get_holiday(holiday_id, merchant_id)
        
        if holiday_date is not None:
            holiday.holiday_date = holiday_date
        if name is not None:
            holiday.name = name
        if is_recurring is not None:
            holiday.is_recurring = is_recurring
        
        return self.holiday_repo.save(holiday)
    
    async def delete_holiday(self, holiday_id: int, merchant_id: str) -> None:
        """
        刪除休假日
        
        Args:
            holiday_id: 休假日 ID
            merchant_id: 商家 ID
        """
        if not self.holiday_repo:
            raise RuntimeError("Holiday repository not initialized")
        
        success = self.holiday_repo.delete(holiday_id, merchant_id)
        if not success:
            raise ValueError(f"Holiday not found: {holiday_id}")
    
    # ========== Staff Working Hours Management ==========
    
    async def clear_staff_working_hours(self, staff_id: int, merchant_id: str) -> None:
        """
        清除員工的所有工時設定
        
        Args:
            staff_id: 員工 ID
            merchant_id: 商家 ID
        """
        staff = await self.get_staff(staff_id, merchant_id)
        if not staff:
            raise ValueError(f"Staff not found: {staff_id}")
        
        # 清除現有工時
        self.staff_repo.clear_working_hours(staff_id)
    
    async def add_staff_working_hours(
        self,
        staff_id: int,
        merchant_id: str,
        day_of_week: int,
        start_time: str,
        end_time: str
    ) -> None:
        """
        新增員工工時
        
        Args:
            staff_id: 員工 ID
            merchant_id: 商家 ID
            day_of_week: 星期幾 (0=Monday, 6=Sunday)
            start_time: 開始時間 (HH:MM)
            end_time: 結束時間 (HH:MM)
        """
        staff = await self.get_staff(staff_id, merchant_id)
        if not staff:
            raise ValueError(f"Staff not found: {staff_id}")
        
        # 新增工時
        self.staff_repo.add_working_hours(staff_id, day_of_week, start_time, end_time)
    
    # ========== Staff Holiday Management ==========
    
    async def create_staff_holiday(
        self,
        merchant_id: str,
        staff_id: int,
        holiday_date: date,
        name: str,
        is_recurring: bool = False
    ) -> 'StaffHoliday':
        """
        創建美甲師休假
        
        Args:
            merchant_id: 商家 ID
            staff_id: 美甲師 ID
            holiday_date: 休假日期
            name: 休假名稱
            is_recurring: 是否每年重複
        
        Returns:
            StaffHoliday: 創建的休假
        """
        # 驗證美甲師存在
        staff = await self.get_staff(staff_id, merchant_id)
        if not staff:
            raise ValueError(f"Staff not found: {staff_id}")
        
        # 檢查是否已有相同日期的休假
        existing_holidays = await self.list_staff_holidays(
            merchant_id=merchant_id,
            staff_id=staff_id,
            start_date=holiday_date,
            end_date=holiday_date
        )
        
        if existing_holidays:
            raise ValueError(f"美甲師 {staff.name} 在 {holiday_date} 已有休假設定")
        
        holiday = StaffHoliday(
            id=None,
            staff_id=staff_id,
            merchant_id=merchant_id,
            holiday_date=holiday_date,
            name=name,
            is_recurring=is_recurring
        )
        
        # 設定美甲師名稱（用於返回）
        holiday.staff_name = staff.name
        
        return self.staff_repo.save_staff_holiday(holiday)
    
    async def list_staff_holidays(
        self,
        merchant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        staff_id: Optional[int] = None
    ) -> list['StaffHoliday']:
        """
        查詢美甲師休假
        
        Args:
            merchant_id: 商家 ID
            start_date: 開始日期（可選）
            end_date: 結束日期（可選）
            staff_id: 美甲師 ID（可選）
        
        Returns:
            list[StaffHoliday]: 休假列表
        """
        return self.staff_repo.find_staff_holidays(
            merchant_id=merchant_id,
            start_date=start_date,
            end_date=end_date,
            staff_id=staff_id
        )
    
    async def get_staff_holiday(self, holiday_id: int, merchant_id: str) -> 'StaffHoliday':
        """
        取得單一美甲師休假
        
        Args:
            holiday_id: 休假 ID
            merchant_id: 商家 ID
        
        Returns:
            StaffHoliday: 休假
        
        Raises:
            ValueError: 休假不存在
        """
        holiday = self.staff_repo.find_staff_holiday_by_id(holiday_id, merchant_id)
        if not holiday:
            raise ValueError(f"Staff holiday not found: {holiday_id}")
        
        return holiday
    
    async def update_staff_holiday(
        self,
        holiday_id: int,
        merchant_id: str,
        holiday_date: Optional[date] = None,
        name: Optional[str] = None,
        is_recurring: Optional[bool] = None
    ) -> 'StaffHoliday':
        """
        更新美甲師休假
        
        Args:
            holiday_id: 休假 ID
            merchant_id: 商家 ID
            holiday_date: 休假日期（可選）
            name: 休假名稱（可選）
            is_recurring: 是否每年重複（可選）
        
        Returns:
            StaffHoliday: 更新後的休假
        """
        holiday = await self.get_staff_holiday(holiday_id, merchant_id)
        
        if holiday_date is not None:
            holiday.holiday_date = holiday_date
        if name is not None:
            holiday.name = name
        if is_recurring is not None:
            holiday.is_recurring = is_recurring
        
        return self.staff_repo.save_staff_holiday(holiday)
    
    async def delete_staff_holiday(self, holiday_id: int, merchant_id: str) -> None:
        """
        刪除美甲師休假
        
        Args:
            holiday_id: 休假 ID
            merchant_id: 商家 ID
        """
        success = self.staff_repo.delete_staff_holiday(holiday_id, merchant_id)
        if not success:
            raise ValueError(f"Staff holiday not found: {holiday_id}")

