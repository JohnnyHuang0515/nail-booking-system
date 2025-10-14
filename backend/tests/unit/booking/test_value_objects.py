"""
Booking Context - Unit Tests - Value Objects
測試 Money, Duration, TimeSlot 值物件
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from booking.domain.value_objects import Money, Duration, TimeSlot


TZ = ZoneInfo("Asia/Taipei")


class TestMoney:
    """Money 值物件測試"""
    
    def test_create_money_with_valid_amount(self):
        """✅ 測試案例：建立有效金額"""
        money = Money(amount=Decimal("800"), currency="TWD")
        
        assert money.amount == Decimal("800")
        assert money.currency == "TWD"
    
    def test_negative_amount_raises_error(self):
        """✅ 測試案例：負數金額應拋出異常"""
        with pytest.raises(ValueError, match="金額不可為負數"):
            Money(amount=Decimal("-100"), currency="TWD")
    
    def test_money_addition_same_currency(self):
        """✅ 測試案例：同幣別金額加法"""
        m1 = Money(amount=Decimal("800"), currency="TWD")
        m2 = Money(amount=Decimal("200"), currency="TWD")
        
        result = m1 + m2
        
        assert result.amount == Decimal("1000")
        assert result.currency == "TWD"
    
    def test_money_addition_different_currency_raises(self):
        """✅ 測試案例：不同幣別無法相加"""
        m1 = Money(amount=Decimal("100"), currency="TWD")
        m2 = Money(amount=Decimal("10"), currency="USD")
        
        with pytest.raises(ValueError, match="不同幣別無法相加"):
            m1 + m2
    
    def test_money_multiplication(self):
        """✅ 測試案例：金額乘法"""
        money = Money(amount=Decimal("800"), currency="TWD")
        
        result = money * 2
        
        assert result.amount == Decimal("1600")
    
    def test_money_zero_factory(self):
        """✅ 測試案例：零金額工廠方法"""
        zero = Money.zero(currency="TWD")
        
        assert zero.amount == Decimal("0")
        assert zero.currency == "TWD"


class TestDuration:
    """Duration 值物件測試"""
    
    def test_create_duration(self):
        """✅ 測試案例：建立時長"""
        duration = Duration(minutes=60)
        
        assert duration.minutes == 60
    
    def test_negative_duration_raises(self):
        """✅ 測試案例：負時長應拋出異常"""
        with pytest.raises(ValueError, match="時長不可為負數"):
            Duration(minutes=-10)
    
    def test_duration_addition(self):
        """✅ 測試案例：時長加法"""
        d1 = Duration(minutes=60)
        d2 = Duration(minutes=15)
        
        result = d1 + d2
        
        assert result.minutes == 75
    
    def test_duration_to_timedelta(self):
        """✅ 測試案例：轉換為 timedelta"""
        duration = Duration(minutes=90)
        
        td = duration.to_timedelta()
        
        assert td == timedelta(minutes=90)
    
    def test_duration_from_hours(self):
        """✅ 測試案例：從小時建立時長"""
        duration = Duration.from_hours(1.5)
        
        assert duration.minutes == 90


class TestTimeSlot:
    """TimeSlot 值物件測試"""
    
    def test_create_valid_time_slot(self):
        """✅ 測試案例：建立有效時段"""
        start = datetime(2025, 10, 16, 14, 0, tzinfo=TZ)
        end = datetime(2025, 10, 16, 15, 0, tzinfo=TZ)
        
        slot = TimeSlot(start_at=start, end_at=end)
        
        assert slot.start_at == start
        assert slot.end_at == end
    
    def test_end_before_start_raises(self):
        """✅ 測試案例：結束早於開始應拋出異常"""
        start = datetime(2025, 10, 16, 15, 0, tzinfo=TZ)
        end = datetime(2025, 10, 16, 14, 0, tzinfo=TZ)
        
        with pytest.raises(ValueError, match="結束時間必須晚於開始時間"):
            TimeSlot(start_at=start, end_at=end)
    
    def test_naive_datetime_raises(self):
        """✅ 測試案例：無時區的 datetime 應拋出異常"""
        start = datetime(2025, 10, 16, 14, 0)  # naive
        end = datetime(2025, 10, 16, 15, 0)    # naive
        
        with pytest.raises(ValueError, match="時間必須包含時區資訊"):
            TimeSlot(start_at=start, end_at=end)
    
    def test_overlaps_true(self):
        """✅ 測試案例：重疊檢測 - 有重疊"""
        slot_a = TimeSlot(
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
        )
        slot_b = TimeSlot(
            start_at=datetime(2025, 10, 16, 10, 30, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 30, tzinfo=TZ)
        )
        
        assert slot_a.overlaps(slot_b) is True
        assert slot_b.overlaps(slot_a) is True  # 對稱性
    
    def test_overlaps_false_adjacent(self):
        """✅ 測試案例：緊鄰時段不重疊"""
        slot_a = TimeSlot(
            start_at=datetime(2025, 10, 16, 10, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
        )
        slot_b = TimeSlot(
            start_at=datetime(2025, 10, 16, 11, 0, tzinfo=TZ),  # 緊鄰
            end_at=datetime(2025, 10, 16, 12, 0, tzinfo=TZ)
        )
        
        assert slot_a.overlaps(slot_b) is False
    
    def test_duration_calculation(self):
        """✅ 測試案例：計算時段長度"""
        slot = TimeSlot(
            start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 16, 15, 30, tzinfo=TZ)
        )
        
        duration = slot.duration()
        
        assert duration.minutes == 90

