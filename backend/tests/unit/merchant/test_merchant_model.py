"""
Merchant Context - Unit Tests - Merchant Aggregate
測試 Merchant 聚合的業務邏輯
"""
import pytest
from datetime import datetime

from merchant.domain.models import Merchant, MerchantStatus, LineCredentials


class TestMerchantAggregate:
    """Merchant 聚合根測試"""
    
    def test_create_merchant_with_basic_info(self):
        """✅ 測試案例：建立基礎商家"""
        # Act
        merchant = Merchant(
            id="test-merchant-001",
            slug="nail-abc",
            name="美甲沙龍 ABC",
            status=MerchantStatus.ACTIVE,
            timezone="Asia/Taipei"
        )
        
        # Assert
        assert merchant.id == "test-merchant-001"
        assert merchant.slug == "nail-abc"
        assert merchant.name == "美甲沙龍 ABC"
        assert merchant.status == MerchantStatus.ACTIVE
        assert merchant.timezone == "Asia/Taipei"
        assert merchant.is_active() is True
    
    def test_empty_slug_raises_error(self):
        """✅ 測試案例：空 slug 應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="商家 slug 不可為空"):
            Merchant(
                id="test",
                slug="",
                name="Test"
            )
    
    def test_empty_name_raises_error(self):
        """✅ 測試案例：空名稱應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="商家名稱不可為空"):
            Merchant(
                id="test",
                slug="test",
                name=""
            )
    
    def test_invalid_slug_format_raises_error(self):
        """✅ 測試案例：無效 slug 格式應拋出異常"""
        # Act & Assert - 包含大寫字母
        with pytest.raises(ValueError, match="slug 只能包含小寫字母"):
            Merchant(
                id="test",
                slug="Nail-ABC",  # 大寫
                name="Test"
            )
        
        # 包含特殊符號
        with pytest.raises(ValueError, match="slug 只能包含小寫字母"):
            Merchant(
                id="test",
                slug="nail_abc",  # 底線（應使用連字符）
                name="Test"
            )
    
    def test_invalid_timezone_raises_error(self):
        """✅ 測試案例：無效時區應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="無效的時區"):
            Merchant(
                id="test",
                slug="test",
                name="Test",
                timezone="Invalid/Timezone"
            )
    
    def test_is_active_returns_true_for_active_merchant(self):
        """✅ 測試案例：啟用商家的 is_active() 返回 True"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            status=MerchantStatus.ACTIVE
        )
        
        # Act & Assert
        assert merchant.is_active() is True
        assert merchant.can_accept_booking() is True
    
    def test_is_active_returns_false_for_suspended_merchant(self):
        """✅ 測試案例：暫停商家的 is_active() 返回 False"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            status=MerchantStatus.SUSPENDED
        )
        
        # Act & Assert
        assert merchant.is_active() is False
        assert merchant.can_accept_booking() is False
    
    def test_activate_merchant(self):
        """✅ 測試案例：啟用商家"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            status=MerchantStatus.SUSPENDED
        )
        
        # Act
        merchant.activate()
        
        # Assert
        assert merchant.status == MerchantStatus.ACTIVE
        assert merchant.updated_at is not None
    
    def test_suspend_merchant(self):
        """✅ 測試案例：暫停商家"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            status=MerchantStatus.ACTIVE
        )
        
        # Act
        merchant.suspend()
        
        # Assert
        assert merchant.status == MerchantStatus.SUSPENDED
        assert merchant.updated_at is not None
    
    def test_cancel_merchant(self):
        """✅ 測試案例：取消商家（終態）"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            status=MerchantStatus.ACTIVE
        )
        
        # Act
        merchant.cancel()
        
        # Assert
        assert merchant.status == MerchantStatus.CANCELLED
        assert merchant.can_accept_booking() is False
    
    def test_update_merchant_info(self):
        """✅ 測試案例：更新商家資訊"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Original Name",
            address="Original Address",
            phone="0900000000"
        )
        
        # Act
        merchant.update_info(
            name="New Name",
            address="New Address",
            phone="0911111111"
        )
        
        # Assert
        assert merchant.name == "New Name"
        assert merchant.address == "New Address"
        assert merchant.phone == "0911111111"
        assert merchant.updated_at is not None
    
    def test_update_merchant_timezone(self):
        """✅ 測試案例：更新時區"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test",
            timezone="Asia/Taipei"
        )
        
        # Act
        merchant.update_info(timezone="Asia/Tokyo")
        
        # Assert
        assert merchant.timezone == "Asia/Tokyo"
    
    def test_update_invalid_timezone_raises_error(self):
        """✅ 測試案例：更新無效時區應拋出異常"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="無效的時區"):
            merchant.update_info(timezone="Invalid/Timezone")


class TestLineCredentials:
    """LineCredentials 值物件測試"""
    
    def test_create_empty_credentials(self):
        """✅ 測試案例：建立空憑證"""
        # Act
        creds = LineCredentials()
        
        # Assert
        assert creds.channel_id is None
        assert creds.is_configured() is False
    
    def test_create_full_credentials(self):
        """✅ 測試案例：建立完整憑證"""
        # Act
        creds = LineCredentials(
            channel_id="123456",
            channel_secret="secret123",
            channel_access_token="token123",
            bot_basic_id="@bot123"
        )
        
        # Assert
        assert creds.channel_id == "123456"
        assert creds.channel_secret == "secret123"
        assert creds.channel_access_token == "token123"
        assert creds.bot_basic_id == "@bot123"
        assert creds.is_configured() is True
    
    def test_is_configured_requires_all_essential_fields(self):
        """✅ 測試案例：is_configured 需要所有必要欄位"""
        # Arrange - 缺少 channel_secret
        creds = LineCredentials(
            channel_id="123456",
            channel_access_token="token123"
        )
        
        # Act & Assert
        assert creds.is_configured() is False
    
    def test_update_line_credentials(self):
        """✅ 測試案例：更新 LINE 憑證"""
        # Arrange
        merchant = Merchant(
            id="test",
            slug="test",
            name="Test"
        )
        
        # Act
        merchant.update_line_credentials(
            channel_id="new-channel-id",
            channel_secret="new-secret",
            channel_access_token="new-token",
            bot_basic_id="@new-bot"
        )
        
        # Assert
        assert merchant.line_credentials.channel_id == "new-channel-id"
        assert merchant.line_credentials.is_configured() is True
        assert merchant.updated_at is not None


class TestMerchantStatus:
    """MerchantStatus 枚舉測試"""
    
    def test_status_values(self):
        """✅ 測試案例：狀態枚舉值正確"""
        assert MerchantStatus.ACTIVE.value == "active"
        assert MerchantStatus.SUSPENDED.value == "suspended"
        assert MerchantStatus.CANCELLED.value == "cancelled"
    
    def test_create_from_string(self):
        """✅ 測試案例：從字串建立枚舉"""
        # Act
        active = MerchantStatus("active")
        suspended = MerchantStatus("suspended")
        
        # Assert
        assert active == MerchantStatus.ACTIVE
        assert suspended == MerchantStatus.SUSPENDED

