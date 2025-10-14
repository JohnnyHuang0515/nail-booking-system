"""
Booking Context - Domain Layer - Value Objects
值物件：不可變、無身份標識、可替換
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Self


@dataclass(frozen=True)
class Money:
    """
    金額值物件
    
    不變式：
    - amount >= 0
    - currency 必須為 ISO 4217 代碼
    """
    amount: Decimal
    currency: str = "TWD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"金額不可為負數: {self.amount}")
        
        if self.currency not in ["TWD", "USD", "JPY"]:
            raise ValueError(f"不支援的幣別: {self.currency}")
    
    def __add__(self, other: Self) -> Self:
        """金額加法（必須同幣別）"""
        if self.currency != other.currency:
            raise ValueError(
                f"不同幣別無法相加: {self.currency} vs {other.currency}"
            )
        return Money(
            amount=self.amount + other.amount,
            currency=self.currency
        )
    
    def __mul__(self, multiplier: int | Decimal) -> Self:
        """金額乘法"""
        return Money(
            amount=self.amount * Decimal(str(multiplier)),
            currency=self.currency
        )
    
    def __str__(self) -> str:
        return f"{self.currency} ${self.amount:,.2f}"
    
    @classmethod
    def zero(cls, currency: str = "TWD") -> Self:
        """建立零金額"""
        return cls(amount=Decimal("0"), currency=currency)


@dataclass(frozen=True)
class Duration:
    """
    時長值物件
    
    不變式：
    - minutes >= 0
    """
    minutes: int
    
    def __post_init__(self):
        if self.minutes < 0:
            raise ValueError(f"時長不可為負數: {self.minutes}")
    
    def __add__(self, other: Self) -> Self:
        """時長加法"""
        return Duration(minutes=self.minutes + other.minutes)
    
    def __mul__(self, multiplier: int) -> Self:
        """時長乘法"""
        return Duration(minutes=self.minutes * multiplier)
    
    def to_timedelta(self):
        """轉換為 Python timedelta"""
        from datetime import timedelta
        return timedelta(minutes=self.minutes)
    
    def __str__(self) -> str:
        hours = self.minutes // 60
        mins = self.minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours}小時{mins}分鐘"
        elif hours > 0:
            return f"{hours}小時"
        else:
            return f"{mins}分鐘"
    
    @classmethod
    def zero(cls) -> Self:
        """建立零時長"""
        return cls(minutes=0)
    
    @classmethod
    def from_hours(cls, hours: int | Decimal) -> Self:
        """從小時建立時長"""
        return cls(minutes=int(Decimal(str(hours)) * 60))


@dataclass(frozen=True)
class TimeSlot:
    """
    時段值物件
    
    不變式：
    - start_at < end_at
    """
    start_at: datetime
    end_at: datetime
    
    def __post_init__(self):
        if self.start_at >= self.end_at:
            raise ValueError(
                f"結束時間必須晚於開始時間: {self.start_at} >= {self.end_at}"
            )
        
        # 確保時區感知
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("時間必須包含時區資訊（timezone-aware）")
    
    def overlaps(self, other: Self) -> bool:
        """
        檢查時段是否重疊
        
        演算法：兩個區間不重疊的條件是
        a.end <= b.start OR b.end <= a.start
        因此重疊的條件是上述的否定
        """
        return not (self.end_at <= other.start_at or other.end_at <= self.start_at)
    
    def duration(self) -> Duration:
        """計算時段長度"""
        delta = self.end_at - self.start_at
        return Duration(minutes=int(delta.total_seconds() / 60))
    
    def __str__(self) -> str:
        return f"{self.start_at.strftime('%Y-%m-%d %H:%M')} - {self.end_at.strftime('%H:%M')}"

