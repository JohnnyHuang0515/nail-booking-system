"""
Identity Context - Unit Tests - User Aggregate
測試 User 聚合的業務邏輯
"""
import pytest
from datetime import datetime, timezone as dt_timezone

from identity.domain.models import User, Role, RoleType, Permission


class TestUserAggregate:
    """User 聚合根測試"""
    
    def test_create_user_with_email(self):
        """✅ 測試案例：使用 email 建立用戶"""
        # Act
        user = User(
            id="user-001",
            email="test@example.com",
            name="Test User",
            merchant_id="merchant-001"
        )
        
        # Assert
        assert user.id == "user-001"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.role.name == RoleType.CUSTOMER
    
    def test_create_user_with_line_user_id(self):
        """✅ 測試案例：使用 LINE User ID 建立用戶"""
        # Act
        user = User(
            id="user-002",
            line_user_id="U123456789",
            name="LINE User"
        )
        
        # Assert
        assert user.line_user_id == "U123456789"
        assert user.email is None
    
    def test_create_user_without_email_and_line_raises_error(self):
        """✅ 測試案例：沒有 email 或 line_user_id 應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="email 或 line_user_id 至少需要一個"):
            User(
                id="user-003",
                name="Invalid User"
            )
    
    def test_has_permission_for_customer_role(self):
        """✅ 測試案例：客戶角色的權限檢查"""
        # Arrange
        user = User(
            id="user-001",
            email="customer@example.com",
            role=Role(id=1, name=RoleType.CUSTOMER)
        )
        
        # Act & Assert
        assert user.has_permission(Permission.BOOKING_CREATE) is True
        assert user.has_permission(Permission.BOOKING_READ) is True
        assert user.has_permission(Permission.MERCHANT_UPDATE) is False
        assert user.has_permission(Permission.ADMIN_ALL) is False
    
    def test_has_permission_for_merchant_owner_role(self):
        """✅ 測試案例：商家擁有者的權限檢查"""
        # Arrange
        user = User(
            id="user-002",
            email="owner@example.com",
            merchant_id="merchant-001",
            role=Role(id=2, name=RoleType.MERCHANT_OWNER)
        )
        
        # Act & Assert
        assert user.has_permission(Permission.BOOKING_CREATE) is True
        assert user.has_permission(Permission.MERCHANT_UPDATE) is True
        assert user.has_permission(Permission.SERVICE_CREATE) is True
        assert user.has_permission(Permission.BILLING_READ) is True
        assert user.has_permission(Permission.ADMIN_ALL) is False
    
    def test_has_permission_for_admin_role(self):
        """✅ 測試案例：管理員角色擁有所有權限"""
        # Arrange
        user = User(
            id="user-003",
            email="admin@example.com",
            role=Role(id=0, name=RoleType.ADMIN)
        )
        
        # Act & Assert
        assert user.has_permission(Permission.BOOKING_CREATE) is True
        assert user.has_permission(Permission.MERCHANT_UPDATE) is True
        assert user.has_permission(Permission.ADMIN_ALL) is True
    
    def test_inactive_user_has_no_permissions(self):
        """✅ 測試案例：停用用戶無任何權限"""
        # Arrange
        user = User(
            id="user-004",
            email="inactive@example.com",
            role=Role(id=0, name=RoleType.ADMIN),
            is_active=False
        )
        
        # Act & Assert
        assert user.has_permission(Permission.ADMIN_ALL) is False
    
    def test_belongs_to_merchant(self):
        """✅ 測試案例：檢查用戶是否屬於商家"""
        # Arrange
        user = User(
            id="user-001",
            email="staff@example.com",
            merchant_id="merchant-001"
        )
        
        # Act & Assert
        assert user.belongs_to_merchant("merchant-001") is True
        assert user.belongs_to_merchant("merchant-002") is False
    
    def test_admin_can_access_any_merchant(self):
        """✅ 測試案例：管理員可訪問任何商家"""
        # Arrange
        user = User(
            id="user-001",
            email="admin@example.com",
            role=Role(id=0, name=RoleType.ADMIN)
        )
        
        # Act & Assert
        assert user.can_access_merchant("merchant-001") is True
        assert user.can_access_merchant("merchant-002") is True
        assert user.can_access_merchant("any-merchant") is True
    
    def test_non_admin_can_only_access_own_merchant(self):
        """✅ 測試案例：非管理員只能訪問自己的商家"""
        # Arrange
        user = User(
            id="user-001",
            email="owner@example.com",
            merchant_id="merchant-001",
            role=Role(id=2, name=RoleType.MERCHANT_OWNER)
        )
        
        # Act & Assert
        assert user.can_access_merchant("merchant-001") is True
        assert user.can_access_merchant("merchant-002") is False
    
    def test_update_last_login(self):
        """✅ 測試案例：更新最後登入時間"""
        # Arrange
        user = User(
            id="user-001",
            email="test@example.com"
        )
        
        # Act
        user.update_last_login()
        
        # Assert
        assert user.last_login_at is not None
        assert user.updated_at is not None
    
    def test_activate_user(self):
        """✅ 測試案例：啟用用戶"""
        # Arrange
        user = User(
            id="user-001",
            email="test@example.com",
            is_active=False
        )
        
        # Act
        user.activate()
        
        # Assert
        assert user.is_active is True
        assert user.updated_at is not None
    
    def test_deactivate_user(self):
        """✅ 測試案例：停用用戶"""
        # Arrange
        user = User(
            id="user-001",
            email="test@example.com",
            is_active=True
        )
        
        # Act
        user.deactivate()
        
        # Assert
        assert user.is_active is False
    
    def test_verify_email(self):
        """✅ 測試案例：驗證 email"""
        # Arrange
        user = User(
            id="user-001",
            email="test@example.com",
            is_verified=False
        )
        
        # Act
        user.verify_email()
        
        # Assert
        assert user.is_verified is True


class TestRoleModel:
    """Role 實體測試"""
    
    def test_role_default_permissions_for_customer(self):
        """✅ 測試案例：客戶角色的預設權限"""
        # Act
        role = Role(id=1, name=RoleType.CUSTOMER)
        
        # Assert
        assert Permission.BOOKING_CREATE in role.permissions
        assert Permission.BOOKING_READ in role.permissions
        assert Permission.MERCHANT_UPDATE not in role.permissions
    
    def test_role_default_permissions_for_merchant_owner(self):
        """✅ 測試案例：商家擁有者的預設權限"""
        # Act
        role = Role(id=2, name=RoleType.MERCHANT_OWNER)
        
        # Assert
        assert Permission.BOOKING_CREATE in role.permissions
        assert Permission.MERCHANT_UPDATE in role.permissions
        assert Permission.SERVICE_CREATE in role.permissions
        assert Permission.BILLING_READ in role.permissions
    
    def test_role_default_permissions_for_admin(self):
        """✅ 測試案例：管理員的預設權限"""
        # Act
        role = Role(id=0, name=RoleType.ADMIN)
        
        # Assert
        assert Permission.ADMIN_ALL in role.permissions
        assert role.has_permission(Permission.MERCHANT_UPDATE) is True
        assert role.has_permission(Permission.BOOKING_CREATE) is True
    
    def test_role_has_permission(self):
        """✅ 測試案例：檢查角色是否擁有權限"""
        # Arrange
        role = Role(
            id=1,
            name=RoleType.CUSTOMER,
            permissions=[Permission.BOOKING_READ]
        )
        
        # Act & Assert
        assert role.has_permission(Permission.BOOKING_READ) is True
        assert role.has_permission(Permission.MERCHANT_UPDATE) is False


class TestPermissionEnum:
    """Permission 枚舉測試"""
    
    def test_permission_values(self):
        """✅ 測試案例：權限枚舉值正確"""
        assert Permission.BOOKING_CREATE.value == "booking:create"
        assert Permission.MERCHANT_UPDATE.value == "merchant:update"
        assert Permission.ADMIN_ALL.value == "admin:*"

