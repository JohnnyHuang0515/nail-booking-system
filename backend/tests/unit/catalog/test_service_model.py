"""
Catalog Context - Unit Tests - Service Aggregate
測試 Service 聚合的業務邏輯
"""
import pytest
from decimal import Decimal

from catalog.domain.models import Service, ServiceOption
from booking.domain.value_objects import Money, Duration


class TestServiceAggregate:
    """Service 聚合根測試"""
    
    def test_create_service_with_basic_info(self):
        """✅ 測試案例：建立基礎服務"""
        # Arrange & Act
        service = Service(
            id=1,
            merchant_id="test-merchant",
            name="Gel Basic",
            base_price=Money(Decimal("800"), "TWD"),
            base_duration=Duration(60),
            category="基礎服務",
            description="基礎凝膠指甲"
        )
        
        # Assert
        assert service.id == 1
        assert service.name == "Gel Basic"
        assert service.base_price.amount == Decimal("800")
        assert service.base_duration.minutes == 60
        assert service.is_active is True
    
    def test_negative_price_raises_error(self):
        """✅ 測試案例：負數價格應拋出異常（由 Money 值物件保護）"""
        # Act & Assert
        with pytest.raises(ValueError, match="金額不可為負數"):
            Service(
                id=1,
                merchant_id="test",
                name="Test",
                base_price=Money(Decimal("-100")),
                base_duration=Duration(60)
            )
    
    def test_zero_duration_raises_error(self):
        """✅ 測試案例：零時長應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="服務時長必須大於 0"):
            Service(
                id=1,
                merchant_id="test",
                name="Test",
                base_price=Money(Decimal("800")),
                base_duration=Duration(0)
            )
    
    def test_add_option_to_service(self):
        """✅ 測試案例：新增加購選項"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel Basic",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60)
        )
        
        option = ServiceOption(
            id=1,
            service_id=1,
            name="法式造型",
            add_price=Money(Decimal("200")),
            add_duration=Duration(15)
        )
        
        # Act
        service.add_option(option)
        
        # Assert
        assert len(service.options) == 1
        assert service.options[0].name == "法式造型"
    
    def test_add_option_wrong_service_raises(self):
        """✅ 測試案例：選項不屬於此服務應拋出異常"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel Basic",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60)
        )
        
        wrong_option = ServiceOption(
            id=1,
            service_id=99,  # 不同的 service_id
            name="Wrong",
            add_price=Money(Decimal("100")),
            add_duration=Duration(10)
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="選項 1 不屬於服務 1"):
            service.add_option(wrong_option)
    
    def test_get_active_options(self):
        """✅ 測試案例：只取得啟用的選項"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60),
            options=[
                ServiceOption(
                    id=1, service_id=1, name="Active",
                    add_price=Money(Decimal("100")), add_duration=Duration(10),
                    is_active=True
                ),
                ServiceOption(
                    id=2, service_id=1, name="Inactive",
                    add_price=Money(Decimal("100")), add_duration=Duration(10),
                    is_active=False
                )
            ]
        )
        
        # Act
        active_options = service.get_active_options()
        
        # Assert
        assert len(active_options) == 1
        assert active_options[0].name == "Active"
    
    def test_calculate_total_price_without_options(self):
        """✅ 測試案例：無選項的總價計算"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60)
        )
        
        # Act
        total = service.calculate_total_price(option_ids=[])
        
        # Assert
        assert total.amount == Decimal("800")
    
    def test_calculate_total_price_with_options(self):
        """✅ 測試案例：含選項的總價計算（核心邏輯）"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60),
            options=[
                ServiceOption(
                    id=1, service_id=1, name="French",
                    add_price=Money(Decimal("200")), add_duration=Duration(15),
                    is_active=True
                ),
                ServiceOption(
                    id=2, service_id=1, name="Art",
                    add_price=Money(Decimal("300")), add_duration=Duration(20),
                    is_active=True
                )
            ]
        )
        
        # Act
        total = service.calculate_total_price(option_ids=[1, 2])
        
        # Assert
        assert total.amount == Decimal("1300")  # 800 + 200 + 300
    
    def test_calculate_total_price_ignores_inactive_options(self):
        """✅ 測試案例：停用選項不計入總價"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60),
            options=[
                ServiceOption(
                    id=1, service_id=1, name="Active",
                    add_price=Money(Decimal("200")), add_duration=Duration(15),
                    is_active=True
                ),
                ServiceOption(
                    id=2, service_id=1, name="Inactive",
                    add_price=Money(Decimal("300")), add_duration=Duration(20),
                    is_active=False
                )
            ]
        )
        
        # Act
        total = service.calculate_total_price(option_ids=[1, 2])
        
        # Assert
        assert total.amount == Decimal("1000")  # 800 + 200（選項2停用）
    
    def test_calculate_total_duration_with_options(self):
        """✅ 測試案例：含選項的總時長計算（核心邏輯）"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60),
            options=[
                ServiceOption(
                    id=1, service_id=1, name="French",
                    add_price=Money(Decimal("200")), add_duration=Duration(15),
                    is_active=True
                ),
                ServiceOption(
                    id=2, service_id=1, name="Art",
                    add_price=Money(Decimal("300")), add_duration=Duration(20),
                    is_active=True
                )
            ]
        )
        
        # Act
        total = service.calculate_total_duration(option_ids=[1, 2])
        
        # Assert
        assert total.minutes == 95  # 60 + 15 + 20
    
    def test_calculate_with_nonexistent_option_id(self):
        """✅ 測試案例：不存在的選項 ID 應被忽略（不拋錯，更實用）"""
        # Arrange
        service = Service(
            id=1,
            merchant_id="test",
            name="Gel",
            base_price=Money(Decimal("800")),
            base_duration=Duration(60),
            options=[
                ServiceOption(
                    id=1, service_id=1, name="French",
                    add_price=Money(Decimal("200")), add_duration=Duration(15),
                    is_active=True
                )
            ]
        )
        
        # Act
        total = service.calculate_total_price(option_ids=[1, 999])  # 999 不存在
        
        # Assert
        assert total.amount == Decimal("1000")  # 800 + 200（忽略 999）


class TestServiceOption:
    """ServiceOption 實體測試"""
    
    def test_create_service_option(self):
        """✅ 測試案例：建立服務選項"""
        # Act
        option = ServiceOption(
            id=1,
            service_id=1,
            name="法式造型",
            add_price=Money(Decimal("200")),
            add_duration=Duration(15),
            is_active=True,
            display_order=1
        )
        
        # Assert
        assert option.id == 1
        assert option.service_id == 1
        assert option.add_price.amount == Decimal("200")
        assert option.add_duration.minutes == 15

