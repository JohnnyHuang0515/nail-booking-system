"""
Catalog Context - Domain Layer - Aggregates
Service 與 Staff 聚合
"""
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional
from decimal import Decimal

from booking.domain.value_objects import Money, Duration


# 服務分類現在改為自由文字，商家可自訂
# 常見分類範例：基礎服務、進階服務、豪華服務、保養護理等


@dataclass
class ServiceOption:
    """
    服務加購選項（實體，屬於 Service 聚合）
    
    範例：法式、彩繪、光療等
    """
    id: int
    service_id: int  # 所屬服務
    name: str
    add_price: Money
    add_duration: Duration
    is_active: bool = True
    display_order: int = 0


class Service:
    """
    服務聚合根
    
    不變式：
    1. base_price >= 0
    2. base_duration > 0
    3. 只有 is_active 的服務可被預約
    4. ServiceOption 屬於此服務
    """
    
    def __init__(
        self,
        id: int,
        merchant_id: str,
        name: str,
        base_price: Money,
        base_duration: Duration,
        category: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True,
        allow_stack: bool = True,  # 是否允許與其他服務堆疊
        options: Optional[list[ServiceOption]] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.name = name
        self.base_price = base_price
        self.base_duration = base_duration
        self.category = category
        self.description = description
        self.is_active = is_active
        self.allow_stack = allow_stack
        self.options = options or []
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        if self.base_price.amount < 0:
            raise ValueError("服務價格不可為負數")
        
        if self.base_duration.minutes <= 0:
            raise ValueError("服務時長必須大於 0")
    
    def add_option(self, option: ServiceOption):
        """新增加購選項"""
        if option.service_id != self.id:
            raise ValueError(f"選項 {option.id} 不屬於服務 {self.id}")
        
        self.options.append(option)
    
    def get_active_options(self) -> list[ServiceOption]:
        """取得有效的加購選項"""
        return [opt for opt in self.options if opt.is_active]
    
    def calculate_total_price(self, option_ids: list[int]) -> Money:
        """
        計算含選項的總價
        
        Args:
            option_ids: 選擇的選項 ID 列表
        
        Returns:
            總價格
        """
        total = self.base_price
        
        for option_id in option_ids:
            option = next((opt for opt in self.options if opt.id == option_id), None)
            if option and option.is_active:
                total = total + option.add_price
        
        return total
    
    def calculate_total_duration(self, option_ids: list[int]) -> Duration:
        """
        計算含選項的總時長
        
        Args:
            option_ids: 選擇的選項 ID 列表
        
        Returns:
            總時長
        """
        total = self.base_duration
        
        for option_id in option_ids:
            option = next((opt for opt in self.options if opt.id == option_id), None)
            if option and option.is_active:
                total = total + option.add_duration
        
        return total
    
    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name={self.name}, active={self.is_active})>"


class DayOfWeek(int, Enum):
    """星期枚舉（0=Monday, 6=Sunday）"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class StaffWorkingHours:
    """
    員工工時（值物件）
    
    不變式：
    - start_time < end_time
    - day_of_week in [0-6]
    """
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    
    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("開始時間必須早於結束時間")
    
    def is_working(self, check_time: time) -> bool:
        """檢查特定時間是否在工作時間內"""
        return self.start_time <= check_time < self.end_time
    
    def duration_minutes(self) -> int:
        """計算工作時長（分鐘）"""
        from datetime import datetime, date
        today = date.today()
        start_dt = datetime.combine(today, self.start_time)
        end_dt = datetime.combine(today, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)


class Staff:
    """
    員工聚合根
    
    不變式：
    1. 只有 is_active 的員工可被預約
    2. skills 必須對應有效的 service_id
    3. 工時不可重疊（同一天）
    """
    
    def __init__(
        self,
        id: int,
        merchant_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        skills: Optional[list[int]] = None,  # service_id 列表
        is_active: bool = True,
        working_hours: Optional[list[StaffWorkingHours]] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.name = name
        self.email = email
        self.phone = phone
        self.skills = skills or []
        self.is_active = is_active
        self.working_hours = working_hours or []
        
        self._validate_invariants()
    
    def _validate_invariants(self):
        """驗證不變式"""
        # 檢查同一天工時不重疊
        working_hours_by_day = {}
        for wh in self.working_hours:
            day = wh.day_of_week
            if day not in working_hours_by_day:
                working_hours_by_day[day] = []
            working_hours_by_day[day].append(wh)
        
        for day, hours_list in working_hours_by_day.items():
            if len(hours_list) > 1:
                # 簡化：目前不支援同一天多個工時段
                raise ValueError(f"同一天不可有多個工時段：{day}")
    
    def can_perform_service(self, service_id: int) -> bool:
        """檢查員工是否可執行此服務"""
        return service_id in self.skills
    
    def get_working_hours_for_day(self, day_of_week: DayOfWeek) -> Optional[StaffWorkingHours]:
        """取得特定日期的工時"""
        for wh in self.working_hours:
            if wh.day_of_week == day_of_week:
                return wh
        return None
    
    def is_working_at(self, check_time: time, day_of_week: DayOfWeek) -> bool:
        """檢查是否在工作"""
        wh = self.get_working_hours_for_day(day_of_week)
        if not wh:
            return False
        return wh.is_working(check_time)
    
    def add_skill(self, service_id: int):
        """新增技能"""
        if service_id not in self.skills:
            self.skills.append(service_id)
    
    def remove_skill(self, service_id: int):
        """移除技能"""
        if service_id in self.skills:
            self.skills.remove(service_id)
    
    def set_working_hours(self, day: DayOfWeek, start: time, end: time):
        """設定特定日期的工時"""
        # 移除舊的工時
        self.working_hours = [
            wh for wh in self.working_hours 
            if wh.day_of_week != day
        ]
        
        # 新增新工時
        new_wh = StaffWorkingHours(
            day_of_week=day,
            start_time=start,
            end_time=end
        )
        self.working_hours.append(new_wh)
    
    def __repr__(self) -> str:
        return f"<Staff(id={self.id}, name={self.name}, active={self.is_active}, skills={len(self.skills)})>"

