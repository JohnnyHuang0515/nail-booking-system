"""
Holiday - 休假日領域模型
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Holiday:
    """
    休假日領域模型
    
    商家可設定特定日期為休假日，該日期將不接受預約
    """
    id: Optional[int]
    merchant_id: str
    holiday_date: date
    name: str  # 休假名稱，例如：元旦、農曆新年、店休日
    is_recurring: bool = False  # 是否每年重複（例如：固定的國定假日）
    
    def __post_init__(self):
        """驗證規則"""
        if not self.name or not self.name.strip():
            raise ValueError("休假名稱不能為空")
        
        if not self.merchant_id:
            raise ValueError("merchant_id 不能為空")
    
    def is_on_date(self, check_date: date) -> bool:
        """
        檢查指定日期是否為此休假日
        
        如果是重複休假日，只比對月和日
        如果不是重複休假日，完全比對年月日
        """
        if self.is_recurring:
            return (
                self.holiday_date.month == check_date.month and
                self.holiday_date.day == check_date.day
            )
        else:
            return self.holiday_date == check_date

