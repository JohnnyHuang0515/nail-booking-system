"""
整合測試 - CatalogService
測試服務查詢與員工技能驗證邏輯
"""
import pytest
from datetime import time
from decimal import Decimal

from catalog.application.services import CatalogService
from catalog.infrastructure.repositories.sqlalchemy_service_repository import (
    SQLAlchemyServiceRepository
)
from catalog.infrastructure.repositories.sqlalchemy_staff_repository import (
    SQLAlchemyStaffRepository
)
from catalog.domain.models import (
    Service, ServiceOption, Staff, StaffWorkingHours, 
    ServiceCategory, DayOfWeek
)
from catalog.domain.exceptions import (
    ServiceNotFoundError, StaffNotFoundError, StaffSkillMismatchError
)
from booking.domain.value_objects import Money, Duration


class TestCatalogServiceIntegration:
    """CatalogService 整合測試"""
    
    @pytest.fixture
    def catalog_service(self, db_session_commit):
        """建立 CatalogService 實例"""
        service_repo = SQLAlchemyServiceRepository(db_session_commit)
        staff_repo = SQLAlchemyStaffRepository(db_session_commit)
        return CatalogService(service_repo, staff_repo)
    
    @pytest.fixture
    def sample_service(self, db_session_commit, test_merchant_id):
        """建立測試服務"""
        from catalog.infrastructure.orm.models import ServiceORM, ServiceOptionORM
        
        # 建立服務
        service = ServiceORM(
            id=1,
            merchant_id=test_merchant_id,
            name="Gel Basic",
            category="基礎服務",
            base_price_amount=Decimal("800"),
            base_price_currency="TWD",
            base_duration_minutes=60,
            is_active=True
        )
        db_session_commit.add(service)
        
        # 建立選項
        option = ServiceOptionORM(
            id=1,
            service_id=1,
            name="法式造型",
            add_price_amount=Decimal("200"),
            add_price_currency="TWD",
            add_duration_minutes=15,
            is_active=True,
            display_order=1
        )
        db_session_commit.add(option)
        db_session_commit.commit()
        
        return 1  # service_id
    
    @pytest.fixture
    def sample_staff(self, db_session_commit, test_merchant_id):
        """建立測試員工"""
        from catalog.infrastructure.orm.models import StaffORM, StaffWorkingHoursORM
        
        # 建立員工（有技能 1）
        staff = StaffORM(
            id=1,
            merchant_id=test_merchant_id,
            name="Amy",
            email="amy@test.com",
            phone="0912345678",
            skills=[1],  # 可執行服務 1
            is_active=True
        )
        db_session_commit.add(staff)
        
        # 建立工時（週一 10:00-18:00）
        wh = StaffWorkingHoursORM(
            staff_id=1,
            day_of_week=DayOfWeek.MONDAY.value,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db_session_commit.add(wh)
        db_session_commit.commit()
        
        return 1  # staff_id
    
    def test_get_service_success(
        self, 
        catalog_service, 
        sample_service, 
        test_merchant_id
    ):
        """✅ 測試案例：成功取得服務"""
        # Act
        service = catalog_service.get_service(
            service_id=sample_service,
            merchant_id=test_merchant_id
        )
        
        # Assert
        assert service is not None
        assert service.id == sample_service
        assert service.name == "Gel Basic"
        assert service.base_price.amount == Decimal("800")
        assert service.base_duration.minutes == 60
        assert len(service.options) == 1
    
    def test_get_service_not_found(self, catalog_service, test_merchant_id):
        """✅ 測試案例：服務不存在應拋出異常"""
        # Act & Assert
        with pytest.raises(ServiceNotFoundError):
            catalog_service.get_service(
                service_id=999,
                merchant_id=test_merchant_id
            )
    
    def test_get_staff_success(
        self, 
        catalog_service, 
        sample_staff, 
        test_merchant_id
    ):
        """✅ 測試案例：成功取得員工"""
        # Act
        staff = catalog_service.get_staff(
            staff_id=sample_staff,
            merchant_id=test_merchant_id
        )
        
        # Assert
        assert staff is not None
        assert staff.id == sample_staff
        assert staff.name == "Amy"
        assert 1 in staff.skills
        assert len(staff.working_hours) == 1
    
    def test_get_staff_not_found(self, catalog_service, test_merchant_id):
        """✅ 測試案例：員工不存在應拋出異常"""
        # Act & Assert
        with pytest.raises(StaffNotFoundError):
            catalog_service.get_staff(
                staff_id=999,
                merchant_id=test_merchant_id
            )
    
    def test_build_booking_item_without_options(
        self,
        catalog_service,
        sample_service,
        test_merchant_id
    ):
        """✅ 測試案例：建立預約項目（無選項）"""
        # Act
        item = catalog_service.build_booking_item(
            service_id=sample_service,
            option_ids=[],
            merchant_id=test_merchant_id
        )
        
        # Assert
        assert item.service_id == sample_service
        assert item.service_name == "Gel Basic"
        assert item.price.amount == Decimal("800")
        assert item.duration.minutes == 60
        assert len(item.options) == 0
    
    def test_build_booking_item_with_options(
        self,
        catalog_service,
        sample_service,
        test_merchant_id
    ):
        """✅ 測試案例：建立預約項目（含選項）"""
        # Act
        item = catalog_service.build_booking_item(
            service_id=sample_service,
            option_ids=[1],  # 選擇「法式造型」
            merchant_id=test_merchant_id
        )
        
        # Assert
        assert item.service_id == sample_service
        assert item.price.amount == Decimal("1000")  # 800 + 200
        assert item.duration.minutes == 75  # 60 + 15
        assert len(item.options) == 1
        assert item.options[0]["name"] == "法式造型"
    
    def test_validate_staff_can_perform_service_success(
        self,
        catalog_service,
        sample_service,
        sample_staff,
        test_merchant_id
    ):
        """✅ 測試案例：驗證員工可執行服務（成功）"""
        # Act & Assert - 不應拋出異常
        catalog_service.validate_staff_can_perform_service(
            staff_id=sample_staff,
            service_id=sample_service,
            merchant_id=test_merchant_id
        )
    
    def test_validate_staff_can_perform_service_skill_mismatch(
        self,
        catalog_service,
        sample_service,
        sample_staff,
        test_merchant_id,
        db_session_commit
    ):
        """✅ 測試案例：驗證員工技能不匹配應拋出異常"""
        # Arrange - 建立另一個服務（service_id=2），但員工只有技能 1
        from catalog.infrastructure.orm.models import ServiceORM
        
        service2 = ServiceORM(
            id=2,
            merchant_id=test_merchant_id,
            name="Advanced Nail Art",
            category="進階服務",
            base_price_amount=Decimal("1200"),
            base_price_currency="TWD",
            base_duration_minutes=90,
            is_active=True
        )
        db_session_commit.add(service2)
        db_session_commit.commit()
        
        # Act & Assert
        with pytest.raises(StaffSkillMismatchError):
            catalog_service.validate_staff_can_perform_service(
                staff_id=sample_staff,  # 只有技能 1
                service_id=2,  # 需要技能 2
                merchant_id=test_merchant_id
            )
    
    def test_get_staff_working_hours_for_day(
        self,
        catalog_service,
        sample_staff,
        test_merchant_id
    ):
        """✅ 測試案例：取得員工特定日期工時"""
        # Act
        staff = catalog_service.get_staff(
            staff_id=sample_staff,
            merchant_id=test_merchant_id
        )
        
        monday_wh = staff.get_working_hours_for_day(DayOfWeek.MONDAY)
        tuesday_wh = staff.get_working_hours_for_day(DayOfWeek.TUESDAY)
        
        # Assert
        assert monday_wh is not None
        assert monday_wh.start_time == time(10, 0)
        assert monday_wh.end_time == time(18, 0)
        assert tuesday_wh is None  # 週二無工時
    
    def test_inactive_service_not_returned(
        self,
        catalog_service,
        test_merchant_id,
        db_session_commit
    ):
        """✅ 測試案例：停用的服務不應被取得"""
        # Arrange - 建立停用服務
        from catalog.infrastructure.orm.models import ServiceORM
        
        service = ServiceORM(
            id=99,
            merchant_id=test_merchant_id,
            name="Inactive Service",
            category="基礎服務",
            base_price_amount=Decimal("500"),
            base_price_currency="TWD",
            base_duration_minutes=30,
            is_active=False  # 停用
        )
        db_session_commit.add(service)
        db_session_commit.commit()
        
        # Act & Assert
        with pytest.raises(ServiceNotFoundError):
            catalog_service.get_service(
                service_id=99,
                merchant_id=test_merchant_id
            )

