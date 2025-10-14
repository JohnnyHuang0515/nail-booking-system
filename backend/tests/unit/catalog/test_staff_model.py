"""
Catalog Context - Unit Tests - Staff Aggregate
測試 Staff 聚合與 StaffWorkingHours 邏輯
"""
import pytest
from datetime import time

from catalog.domain.models import Staff, StaffWorkingHours, DayOfWeek


class TestStaffAggregate:
    """Staff 聚合根測試"""
    
    def test_create_staff_with_basic_info(self):
        """✅ 測試案例：建立基礎員工"""
        # Act
        staff = Staff(
            id=1,
            merchant_id="test-merchant",
            name="Amy",
            email="amy@test.com",
            phone="0912345678",
            is_active=True
        )
        
        # Assert
        assert staff.id == 1
        assert staff.name == "Amy"
        assert staff.is_active is True
        assert len(staff.skills) == 0
        assert len(staff.working_hours) == 0
    
    def test_add_skill(self):
        """✅ 測試案例：新增技能"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            skills=[]
        )
        
        # Act
        staff.add_skill(service_id=1)
        staff.add_skill(service_id=2)
        
        # Assert
        assert staff.skills == [1, 2]
    
    def test_add_duplicate_skill_ignored(self):
        """✅ 測試案例：重複技能不會被加入兩次"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            skills=[1]
        )
        
        # Act
        staff.add_skill(service_id=1)  # 重複
        
        # Assert
        assert staff.skills == [1]  # 只有一個
    
    def test_remove_skill(self):
        """✅ 測試案例：移除技能"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            skills=[1, 2, 3]
        )
        
        # Act
        staff.remove_skill(service_id=2)
        
        # Assert
        assert staff.skills == [1, 3]
    
    def test_can_perform_service_true(self):
        """✅ 測試案例：員工可執行服務（核心邏輯）"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            skills=[1, 2, 3]
        )
        
        # Act & Assert
        assert staff.can_perform_service(service_id=1) is True
        assert staff.can_perform_service(service_id=2) is True
        assert staff.can_perform_service(service_id=3) is True
    
    def test_can_perform_service_false(self):
        """✅ 測試案例：員工無法執行服務"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            skills=[1, 2]
        )
        
        # Act & Assert
        assert staff.can_perform_service(service_id=99) is False
    
    def test_set_working_hours(self):
        """✅ 測試案例：設定工作時間"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy"
        )
        
        # Act
        staff.set_working_hours(
            day=DayOfWeek.MONDAY,
            start=time(10, 0),
            end=time(18, 0)
        )
        
        # Assert
        assert len(staff.working_hours) == 1
        wh = staff.working_hours[0]
        assert wh.day_of_week == DayOfWeek.MONDAY
        assert wh.start_time == time(10, 0)
        assert wh.end_time == time(18, 0)
    
    def test_set_working_hours_replaces_existing(self):
        """✅ 測試案例：設定工時會覆蓋該天的舊工時"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            working_hours=[
                StaffWorkingHours(DayOfWeek.MONDAY, time(9, 0), time(17, 0))
            ]
        )
        
        # Act
        staff.set_working_hours(
            day=DayOfWeek.MONDAY,
            start=time(10, 0),
            end=time(18, 0)
        )
        
        # Assert
        assert len(staff.working_hours) == 1  # 只有一個
        wh = staff.working_hours[0]
        assert wh.start_time == time(10, 0)  # 已更新
    
    def test_get_working_hours_for_day(self):
        """✅ 測試案例：取得特定日期的工時"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            working_hours=[
                StaffWorkingHours(DayOfWeek.MONDAY, time(10, 0), time(18, 0)),
                StaffWorkingHours(DayOfWeek.TUESDAY, time(11, 0), time(19, 0))
            ]
        )
        
        # Act
        monday_wh = staff.get_working_hours_for_day(DayOfWeek.MONDAY)
        wednesday_wh = staff.get_working_hours_for_day(DayOfWeek.WEDNESDAY)
        
        # Assert
        assert monday_wh is not None
        assert monday_wh.start_time == time(10, 0)
        assert wednesday_wh is None  # 週三無工時
    
    def test_is_working_at_true(self):
        """✅ 測試案例：檢查是否在工作時間內"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            working_hours=[
                StaffWorkingHours(DayOfWeek.MONDAY, time(10, 0), time(18, 0))
            ]
        )
        
        # Act & Assert
        assert staff.is_working_at(time(14, 0), DayOfWeek.MONDAY) is True
        assert staff.is_working_at(time(10, 0), DayOfWeek.MONDAY) is True  # 邊界
        assert staff.is_working_at(time(17, 59), DayOfWeek.MONDAY) is True
    
    def test_is_working_at_false(self):
        """✅ 測試案例：不在工作時間"""
        # Arrange
        staff = Staff(
            id=1,
            merchant_id="test",
            name="Amy",
            working_hours=[
                StaffWorkingHours(DayOfWeek.MONDAY, time(10, 0), time(18, 0))
            ]
        )
        
        # Act & Assert
        assert staff.is_working_at(time(9, 59), DayOfWeek.MONDAY) is False
        assert staff.is_working_at(time(18, 0), DayOfWeek.MONDAY) is False  # 邊界（不包含）
        assert staff.is_working_at(time(14, 0), DayOfWeek.TUESDAY) is False  # 該天無工時


class TestStaffWorkingHours:
    """StaffWorkingHours 值物件測試"""
    
    def test_create_valid_working_hours(self):
        """✅ 測試案例：建立有效工時"""
        # Act
        wh = StaffWorkingHours(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Assert
        assert wh.day_of_week == DayOfWeek.MONDAY
        assert wh.start_time == time(10, 0)
        assert wh.end_time == time(18, 0)
    
    def test_end_before_start_raises(self):
        """✅ 測試案例：結束時間早於開始時間應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="開始時間必須早於結束時間"):
            StaffWorkingHours(
                day_of_week=DayOfWeek.MONDAY,
                start_time=time(18, 0),
                end_time=time(10, 0)
            )
    
    def test_is_working_within_hours(self):
        """✅ 測試案例：時間在工時內"""
        # Arrange
        wh = StaffWorkingHours(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Act & Assert
        assert wh.is_working(time(10, 0)) is True   # 開始時間（包含）
        assert wh.is_working(time(14, 0)) is True   # 中間時間
        assert wh.is_working(time(17, 59)) is True  # 接近結束
    
    def test_is_working_outside_hours(self):
        """✅ 測試案例：時間在工時外"""
        # Arrange
        wh = StaffWorkingHours(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Act & Assert
        assert wh.is_working(time(9, 59)) is False   # 開始前
        assert wh.is_working(time(18, 0)) is False   # 結束時間（不包含）
        assert wh.is_working(time(18, 1)) is False   # 結束後
    
    def test_duration_minutes_calculation(self):
        """✅ 測試案例：計算工時長度"""
        # Arrange
        wh = StaffWorkingHours(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Act
        duration = wh.duration_minutes()
        
        # Assert
        assert duration == 480  # 8 小時 = 480 分鐘
    
    def test_duration_minutes_with_partial_hours(self):
        """✅ 測試案例：非整點工時長度計算"""
        # Arrange
        wh = StaffWorkingHours(
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 30),
            end_time=time(18, 15)
        )
        
        # Act
        duration = wh.duration_minutes()
        
        # Assert
        assert duration == 465  # 7小時45分鐘 = 465分鐘


class TestDayOfWeekEnum:
    """DayOfWeek 枚舉測試"""
    
    def test_day_of_week_values(self):
        """✅ 測試案例：星期枚舉值正確"""
        assert DayOfWeek.MONDAY.value == 0
        assert DayOfWeek.TUESDAY.value == 1
        assert DayOfWeek.WEDNESDAY.value == 2
        assert DayOfWeek.THURSDAY.value == 3
        assert DayOfWeek.FRIDAY.value == 4
        assert DayOfWeek.SATURDAY.value == 5
        assert DayOfWeek.SUNDAY.value == 6
    
    def test_create_from_int(self):
        """✅ 測試案例：從整數建立枚舉"""
        # Act
        monday = DayOfWeek(0)
        sunday = DayOfWeek(6)
        
        # Assert
        assert monday == DayOfWeek.MONDAY
        assert sunday == DayOfWeek.SUNDAY

