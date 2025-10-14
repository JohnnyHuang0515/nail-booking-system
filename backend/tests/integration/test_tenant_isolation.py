"""
租戶隔離集成測試 - 最關鍵的安全測試
驗證修復的 SEC-001 漏洞不會再發生
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from identity.domain.models import User, Role, RoleType
from identity.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from identity.domain.auth_service import PasswordService, TokenService


class TestTenantIsolation:
    """
    租戶隔離測試套件
    
    測試目標:
    - ✅ 用戶只能訪問自己所屬商家的資料
    - ✅ 跨租戶訪問被正確拒絕 (403 Forbidden)
    - ✅ Admin 角色可以跨租戶訪問
    """
    
    @pytest.fixture
    def client(self):
        """FastAPI 測試客戶端"""
        return TestClient(app)
    
    @pytest.fixture
    def merchant_a_id(self):
        """商家 A 的 ID"""
        return "00000000-0000-0000-0000-000000000001"
    
    @pytest.fixture
    def merchant_b_id(self):
        """商家 B 的 ID"""
        return "11111111-1111-1111-1111-111111111111"
    
    @pytest.fixture
    def user_merchant_a(self, db_session_commit, merchant_a_id):
        """商家 A 的用戶"""
        from uuid import uuid4
        user_repo = SQLAlchemyUserRepository(db_session_commit)
        
        user = User(
            id=str(uuid4()),
            email="user_a@merchant_a.com",
            password_hash=PasswordService.hash_password("password123"),
            name="商家A用戶",
            merchant_id=merchant_a_id,
            role=Role(id=4, name=RoleType.CUSTOMER)
        )
        
        user_repo.save(user)
        db_session_commit.commit()
        
        return user
    
    @pytest.fixture
    def user_merchant_b(self, db_session_commit, merchant_b_id):
        """商家 B 的用戶"""
        from uuid import uuid4
        user_repo = SQLAlchemyUserRepository(db_session_commit)
        
        user = User(
            id=str(uuid4()),
            email="user_b@merchant_b.com",
            password_hash=PasswordService.hash_password("password123"),
            name="商家B用戶",
            merchant_id=merchant_b_id,
            role=Role(id=4, name=RoleType.CUSTOMER)
        )
        
        user_repo.save(user)
        db_session_commit.commit()
        
        return user
    
    @pytest.fixture
    def token_merchant_a(self, user_merchant_a):
        """商家 A 用戶的 JWT Token"""
        return TokenService.create_access_token(
            user_id=user_merchant_a.id,
            merchant_id=user_merchant_a.merchant_id,
            role=user_merchant_a.role.name.value
        )
    
    @pytest.fixture
    def token_merchant_b(self, user_merchant_b):
        """商家 B 用戶的 JWT Token"""
        return TokenService.create_access_token(
            user_id=user_merchant_b.id,
            merchant_id=user_merchant_b.merchant_id,
            role=user_merchant_b.role.name.value
        )
    
    # ===== 測試：同租戶訪問 =====
    
    def test_same_tenant_access_allowed(
        self, 
        client, 
        token_merchant_a, 
        merchant_a_id
    ):
        """
        測試：用戶可以訪問自己所屬商家的資料
        
        Given: 商家 A 的用戶持有有效 Token
        When: 訪問商家 A 的預約列表
        Then: 返回 200 OK
        """
        response = client.get(
            f"/liff/bookings?merchant_id={merchant_a_id}",
            headers={"Authorization": f"Bearer {token_merchant_a}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # ===== 測試：跨租戶訪問拒絕 =====
    
    def test_cross_tenant_access_denied(
        self, 
        client, 
        token_merchant_a, 
        merchant_b_id
    ):
        """
        測試：用戶不能訪問其他商家的資料 (SEC-001 修復驗證)
        
        Given: 商家 A 的用戶持有有效 Token
        When: 嘗試訪問商家 B 的預約列表
        Then: 返回 403 Forbidden
        """
        response = client.get(
            f"/liff/bookings?merchant_id={merchant_b_id}",
            headers={"Authorization": f"Bearer {token_merchant_a}"}
        )
        
        # 🔒 關鍵斷言：必須返回 403
        assert response.status_code == 403
        assert "無權訪問商家" in response.json()["detail"]
    
    def test_cross_tenant_create_booking_denied(
        self, 
        client, 
        token_merchant_a, 
        merchant_b_id
    ):
        """
        測試：用戶不能為其他商家建立預約
        
        Given: 商家 A 的用戶持有有效 Token
        When: 嘗試為商家 B 建立預約
        Then: 返回 403 Forbidden
        """
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {token_merchant_a}"},
            json={
                "merchant_id": merchant_b_id,
                "staff_id": 1,
                "start_at": "2025-10-25T14:00:00+08:00",
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U999"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        # 🔒 關鍵斷言：必須返回 403
        assert response.status_code == 403
        assert "無權訪問商家" in response.json()["detail"]
    
    def test_cross_tenant_get_booking_denied(
        self, 
        client, 
        token_merchant_a, 
        merchant_b_id
    ):
        """
        測試：用戶不能查詢其他商家的預約詳情
        
        Given: 商家 A 的用戶持有有效 Token
        When: 嘗試查詢商家 B 的預約
        Then: 返回 403 Forbidden
        """
        fake_booking_id = "00000000-0000-0000-0000-000000000099"
        
        response = client.get(
            f"/liff/bookings/{fake_booking_id}?merchant_id={merchant_b_id}",
            headers={"Authorization": f"Bearer {token_merchant_a}"}
        )
        
        # 🔒 關鍵斷言：必須返回 403（在查詢資料庫前就應該被拒絕）
        assert response.status_code == 403
        assert "無權訪問商家" in response.json()["detail"]
    
    def test_cross_tenant_cancel_booking_denied(
        self, 
        client, 
        token_merchant_a, 
        merchant_b_id
    ):
        """
        測試：用戶不能取消其他商家的預約
        
        Given: 商家 A 的用戶持有有效 Token
        When: 嘗試取消商家 B 的預約
        Then: 返回 403 Forbidden
        """
        fake_booking_id = "00000000-0000-0000-0000-000000000099"
        
        response = client.delete(
            f"/liff/bookings/{fake_booking_id}?merchant_id={merchant_b_id}&requester_line_id=U999",
            headers={"Authorization": f"Bearer {token_merchant_a}"}
        )
        
        # 🔒 關鍵斷言：必須返回 403
        assert response.status_code == 403
        assert "無權訪問商家" in response.json()["detail"]
    
    # ===== 測試：無 Token 訪問拒絕 =====
    
    def test_no_token_access_denied(self, client, merchant_a_id):
        """
        測試：未提供 Token 時訪問被拒絕
        
        Given: 未提供 Authorization Header
        When: 訪問受保護的端點
        Then: 返回 401 Unauthorized
        """
        response = client.get(
            f"/liff/bookings?merchant_id={merchant_a_id}"
        )
        
        assert response.status_code == 401
        assert "未提供認證" in response.json()["detail"]
    
    def test_invalid_token_access_denied(self, client, merchant_a_id):
        """
        測試：無效 Token 訪問被拒絕
        
        Given: 提供無效的 JWT Token
        When: 訪問受保護的端點
        Then: 返回 401 Unauthorized
        """
        response = client.get(
            f"/liff/bookings?merchant_id={merchant_a_id}",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
        assert "無效的認證" in response.json()["detail"]
    
    # ===== 測試：User.can_access_merchant() 邏輯 =====
    
    def test_user_can_access_own_merchant(self, user_merchant_a, merchant_a_id):
        """
        測試：User.can_access_merchant() 允許訪問自己的商家
        """
        assert user_merchant_a.can_access_merchant(merchant_a_id) is True
    
    def test_user_cannot_access_other_merchant(
        self, 
        user_merchant_a, 
        merchant_b_id
    ):
        """
        測試：User.can_access_merchant() 拒絕訪問其他商家
        """
        assert user_merchant_a.can_access_merchant(merchant_b_id) is False
    
    def test_admin_can_access_any_merchant(self, db_session_commit):
        """
        測試：Admin 角色可以訪問任意商家
        
        Given: Admin 角色的用戶
        When: 檢查訪問任意商家的權限
        Then: 返回 True
        """
        admin = User(
            id="admin-001",
            email="admin@system.com",
            password_hash=PasswordService.hash_password("admin123"),
            name="系統管理員",
            merchant_id=None,  # Admin 不屬於特定商家
            role=Role(id=1, name=RoleType.ADMIN)
        )
        
        # Admin 可以訪問任意商家
        assert admin.can_access_merchant("00000000-0000-0000-0000-000000000001") is True
        assert admin.can_access_merchant("11111111-1111-1111-1111-111111111111") is True
        assert admin.can_access_merchant("ANY-MERCHANT-ID") is True


class TestTenantIsolationEdgeCases:
    """租戶隔離邊界測試"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_empty_merchant_id_rejected(self, client):
        """
        測試：空 merchant_id 被拒絕
        
        Given: 請求中 merchant_id 為空字串
        When: 訪問端點
        Then: 返回 422 Validation Error
        """
        # 創建臨時用戶並獲取 token
        token = TokenService.create_access_token(
            user_id="temp-user",
            merchant_id="00000000-0000-0000-0000-000000000001",
            role="customer"
        )
        
        response = client.get(
            "/liff/bookings?merchant_id=",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 應該返回驗證錯誤
        assert response.status_code in [422, 400]
    
    def test_malformed_merchant_id_rejected(self, client):
        """
        測試：格式錯誤的 merchant_id 被處理
        
        Given: merchant_id 格式不是 UUID
        When: 訪問端點
        Then: 返回 403 (因為不匹配用戶的 merchant_id)
        """
        token = TokenService.create_access_token(
            user_id="temp-user",
            merchant_id="00000000-0000-0000-0000-000000000001",
            role="customer"
        )
        
        response = client.get(
            "/liff/bookings?merchant_id=not-a-uuid",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 應該返回 403（不匹配用戶的 merchant_id）
        assert response.status_code == 403

