"""
RBAC 權限單元測試
測試 Role 和 Permission 邏輯
"""
import pytest
from identity.domain.models import User, Role, RoleType, Permission
from identity.domain.auth_service import PasswordService


class TestRolePermissions:
    """測試角色權限配置"""
    
    def test_customer_role_permissions(self):
        """
        測試：Customer 角色權限正確
        
        Given: Customer 角色
        When: 檢查權限
        Then: 只有 booking:create 和 booking:read
        """
        role = Role(id=4, name=RoleType.CUSTOMER)
        
        # 有權限
        assert role.has_permission(Permission.BOOKING_CREATE)
        assert role.has_permission(Permission.BOOKING_READ)
        
        # 無權限
        assert not role.has_permission(Permission.BOOKING_UPDATE)
        assert not role.has_permission(Permission.BOOKING_DELETE)
        assert not role.has_permission(Permission.MERCHANT_READ)
        assert not role.has_permission(Permission.STAFF_CREATE)
    
    def test_staff_role_permissions(self):
        """
        測試：Staff 角色權限正確
        
        Given: Staff 角色
        When: 檢查權限
        Then: 有 booking CRUD (除 delete) 和 staff/service read
        """
        role = Role(id=3, name=RoleType.MERCHANT_STAFF)
        
        # 有權限
        assert role.has_permission(Permission.BOOKING_CREATE)
        assert role.has_permission(Permission.BOOKING_READ)
        assert role.has_permission(Permission.BOOKING_UPDATE)
        assert role.has_permission(Permission.STAFF_READ)
        assert role.has_permission(Permission.SERVICE_READ)
        
        # 無權限
        assert not role.has_permission(Permission.BOOKING_DELETE)
        assert not role.has_permission(Permission.MERCHANT_UPDATE)
        assert not role.has_permission(Permission.STAFF_CREATE)
    
    def test_owner_role_permissions(self):
        """
        測試：Owner 角色權限正確
        
        Given: Owner 角色
        When: 檢查權限
        Then: 有幾乎所有權限（除 merchant:delete 和 admin:*）
        """
        role = Role(id=2, name=RoleType.MERCHANT_OWNER)
        
        # 有權限
        assert role.has_permission(Permission.BOOKING_CREATE)
        assert role.has_permission(Permission.BOOKING_READ)
        assert role.has_permission(Permission.BOOKING_UPDATE)
        assert role.has_permission(Permission.BOOKING_DELETE)
        assert role.has_permission(Permission.MERCHANT_READ)
        assert role.has_permission(Permission.MERCHANT_UPDATE)
        assert role.has_permission(Permission.STAFF_CREATE)
        assert role.has_permission(Permission.STAFF_UPDATE)
        assert role.has_permission(Permission.STAFF_DELETE)
        assert role.has_permission(Permission.SERVICE_CREATE)
        assert role.has_permission(Permission.BILLING_READ)
        
        # 無權限
        assert not role.has_permission(Permission.MERCHANT_DELETE)
        assert not role.has_permission(Permission.ADMIN_ALL)
    
    def test_admin_role_has_all_permissions(self):
        """
        測試：Admin 角色擁有所有權限
        
        Given: Admin 角色
        When: 檢查任意權限
        Then: 全部返回 True
        """
        role = Role(id=1, name=RoleType.ADMIN)
        
        # Admin 有 ADMIN_ALL 權限
        assert Permission.ADMIN_ALL in role.permissions
        
        # Admin 可以做任何事
        assert role.has_permission(Permission.BOOKING_CREATE)
        assert role.has_permission(Permission.BOOKING_DELETE)
        assert role.has_permission(Permission.MERCHANT_DELETE)
        assert role.has_permission(Permission.STAFF_DELETE)
        assert role.has_permission(Permission.BILLING_UPDATE)
        assert role.has_permission(Permission.ADMIN_ALL)


class TestUserPermissions:
    """測試用戶權限檢查"""
    
    @pytest.fixture
    def customer_user(self):
        """Customer 用戶"""
        return User(
            id="customer-001",
            email="customer@test.com",
            password_hash=PasswordService.hash_password("password"),
            name="測試客戶",
            merchant_id="merchant-001",
            role=Role(id=4, name=RoleType.CUSTOMER),
            is_active=True
        )
    
    @pytest.fixture
    def owner_user(self):
        """Owner 用戶"""
        return User(
            id="owner-001",
            email="owner@test.com",
            password_hash=PasswordService.hash_password("password"),
            name="商家老闆",
            merchant_id="merchant-001",
            role=Role(id=2, name=RoleType.MERCHANT_OWNER),
            is_active=True
        )
    
    @pytest.fixture
    def admin_user(self):
        """Admin 用戶"""
        return User(
            id="admin-001",
            email="admin@system.com",
            password_hash=PasswordService.hash_password("password"),
            name="系統管理員",
            merchant_id=None,
            role=Role(id=1, name=RoleType.ADMIN),
            is_active=True
        )
    
    def test_customer_has_limited_permissions(self, customer_user):
        """
        測試：Customer 用戶權限受限
        """
        assert customer_user.has_permission(Permission.BOOKING_CREATE)
        assert customer_user.has_permission(Permission.BOOKING_READ)
        assert not customer_user.has_permission(Permission.BOOKING_UPDATE)
        assert not customer_user.has_permission(Permission.STAFF_CREATE)
    
    def test_owner_has_management_permissions(self, owner_user):
        """
        測試：Owner 用戶有管理權限
        """
        assert owner_user.has_permission(Permission.BOOKING_DELETE)
        assert owner_user.has_permission(Permission.STAFF_CREATE)
        assert owner_user.has_permission(Permission.SERVICE_UPDATE)
        assert owner_user.has_permission(Permission.MERCHANT_UPDATE)
    
    def test_admin_has_all_permissions(self, admin_user):
        """
        測試：Admin 用戶有所有權限
        """
        assert admin_user.has_permission(Permission.ADMIN_ALL)
        assert admin_user.has_permission(Permission.MERCHANT_DELETE)
        assert admin_user.has_permission(Permission.BOOKING_DELETE)
    
    def test_inactive_user_has_no_permissions(self, customer_user):
        """
        測試：停用用戶沒有任何權限
        
        Given: 用戶被停用
        When: 檢查任意權限
        Then: 全部返回 False
        """
        customer_user.deactivate()
        
        assert not customer_user.has_permission(Permission.BOOKING_CREATE)
        assert not customer_user.has_permission(Permission.BOOKING_READ)
        assert customer_user.is_active is False


class TestTenantBoundary:
    """測試租戶邊界檢查"""
    
    @pytest.fixture
    def merchant_a_user(self):
        """商家 A 的用戶"""
        return User(
            id="user-a",
            email="user@merchant_a.com",
            password_hash=PasswordService.hash_password("password"),
            name="商家A用戶",
            merchant_id="merchant-a-id",
            role=Role(id=4, name=RoleType.CUSTOMER)
        )
    
    @pytest.fixture
    def admin_user(self):
        """Admin 用戶"""
        return User(
            id="admin",
            email="admin@system.com",
            password_hash=PasswordService.hash_password("password"),
            name="Admin",
            merchant_id=None,
            role=Role(id=1, name=RoleType.ADMIN)
        )
    
    def test_user_belongs_to_own_merchant(self, merchant_a_user):
        """
        測試：用戶屬於自己的商家
        """
        assert merchant_a_user.belongs_to_merchant("merchant-a-id")
        assert not merchant_a_user.belongs_to_merchant("merchant-b-id")
    
    def test_user_can_access_own_merchant(self, merchant_a_user):
        """
        測試：用戶可以訪問自己的商家
        """
        assert merchant_a_user.can_access_merchant("merchant-a-id")
    
    def test_user_cannot_access_other_merchant(self, merchant_a_user):
        """
        測試：用戶不能訪問其他商家 (核心安全邏輯)
        """
        assert not merchant_a_user.can_access_merchant("merchant-b-id")
        assert not merchant_a_user.can_access_merchant("merchant-c-id")
    
    def test_admin_can_access_any_merchant(self, admin_user):
        """
        測試：Admin 可以訪問任意商家
        """
        assert admin_user.can_access_merchant("merchant-a-id")
        assert admin_user.can_access_merchant("merchant-b-id")
        assert admin_user.can_access_merchant("merchant-xyz")
        assert admin_user.can_access_merchant("any-random-id")
    
    def test_admin_with_merchant_can_still_access_all(self):
        """
        測試：即使 Admin 有 merchant_id，仍可訪問所有商家
        """
        admin_with_merchant = User(
            id="admin-with-merchant",
            email="admin@merchant_a.com",
            password_hash=PasswordService.hash_password("password"),
            name="Admin (有商家)",
            merchant_id="merchant-a-id",  # 有指定商家
            role=Role(id=1, name=RoleType.ADMIN)
        )
        
        # 仍然可以訪問其他商家
        assert admin_with_merchant.can_access_merchant("merchant-a-id")
        assert admin_with_merchant.can_access_merchant("merchant-b-id")


class TestUserInvariants:
    """測試用戶不變式"""
    
    def test_user_must_have_email_or_line_id(self):
        """
        測試：用戶必須有 email 或 line_user_id
        
        Given: email 和 line_user_id 都為 None
        When: 建立用戶
        Then: 拋出 ValueError
        """
        with pytest.raises(ValueError, match="email 或 line_user_id 至少需要一個"):
            User(
                id="user-001",
                email=None,
                line_user_id=None,
                password_hash="hash",
                name="測試",
                merchant_id="merchant-001"
            )
    
    def test_user_can_have_only_email(self):
        """
        測試：用戶可以只有 email
        """
        user = User(
            id="user-001",
            email="test@example.com",
            line_user_id=None,
            password_hash="hash",
            name="測試",
            merchant_id="merchant-001"
        )
        
        assert user.email == "test@example.com"
        assert user.line_user_id is None
    
    def test_user_can_have_only_line_id(self):
        """
        測試：用戶可以只有 line_user_id
        """
        user = User(
            id="user-001",
            email=None,
            line_user_id="U123456",
            password_hash="hash",
            name="測試",
            merchant_id="merchant-001"
        )
        
        assert user.email is None
        assert user.line_user_id == "U123456"
    
    def test_user_can_have_both_email_and_line_id(self):
        """
        測試：用戶可以同時有 email 和 line_user_id
        """
        user = User(
            id="user-001",
            email="test@example.com",
            line_user_id="U123456",
            password_hash="hash",
            name="測試",
            merchant_id="merchant-001"
        )
        
        assert user.email == "test@example.com"
        assert user.line_user_id == "U123456"


class TestPasswordService:
    """測試密碼服務"""
    
    def test_password_hash_is_different_from_plain(self):
        """
        測試：密碼雜湊後與明文不同
        """
        plain = "my_secret_password"
        hashed = PasswordService.hash_password(plain)
        
        assert hashed != plain
        assert len(hashed) > len(plain)
    
    def test_same_password_generates_different_hash(self):
        """
        測試：相同密碼每次雜湊結果不同（因為 salt）
        """
        plain = "my_secret_password"
        hash1 = PasswordService.hash_password(plain)
        hash2 = PasswordService.hash_password(plain)
        
        # bcrypt 每次生成不同的 salt
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """
        測試：驗證正確密碼
        """
        plain = "my_secret_password"
        hashed = PasswordService.hash_password(plain)
        
        assert PasswordService.verify_password(plain, hashed)
    
    def test_verify_incorrect_password(self):
        """
        測試：驗證錯誤密碼
        """
        plain = "my_secret_password"
        wrong = "wrong_password"
        hashed = PasswordService.hash_password(plain)
        
        assert not PasswordService.verify_password(wrong, hashed)
    
    def test_verify_empty_password_fails(self):
        """
        測試：空密碼驗證失敗
        """
        plain = "my_secret_password"
        hashed = PasswordService.hash_password(plain)
        
        assert not PasswordService.verify_password("", hashed)

