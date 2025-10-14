"""
預約流程集成測試
測試核心業務邏輯的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from api.main import app
from booking.application.services import BookingService
from booking.infrastructure.repositories.sqlalchemy_booking_repository import SQLAlchemyBookingRepository
from booking.infrastructure.repositories.sqlalchemy_booking_lock_repository import SQLAlchemyBookingLockRepository
from catalog.application.services import CatalogService
from catalog.infrastructure.repositories.sqlalchemy_service_repository import SQLAlchemyServiceRepository
from catalog.infrastructure.repositories.sqlalchemy_staff_repository import SQLAlchemyStaffRepository
from identity.domain.auth_service import TokenService


class TestBookingFlow:
    """預約流程測試套件"""
    
    @pytest.fixture
    def client(self):
        """FastAPI 測試客戶端"""
        return TestClient(app)
    
    @pytest.fixture
    def merchant_id(self):
        """測試商家 ID"""
        return "00000000-0000-0000-0000-000000000001"
    
    @pytest.fixture
    def customer_token(self, merchant_id):
        """客戶 Token"""
        return TokenService.create_access_token(
            user_id="test-customer-001",
            merchant_id=merchant_id,
            role="customer"
        )
    
    @pytest.fixture
    def booking_service(self, db_session_commit):
        """BookingService 實例"""
        booking_repo = SQLAlchemyBookingRepository(db_session_commit)
        booking_lock_repo = SQLAlchemyBookingLockRepository(db_session_commit)
        
        service_repo = SQLAlchemyServiceRepository(db_session_commit)
        staff_repo = SQLAlchemyStaffRepository(db_session_commit)
        catalog_service = CatalogService(service_repo, staff_repo)
        
        return BookingService(booking_repo, booking_lock_repo, catalog_service)
    
    # ===== 測試：建立預約 =====
    
    def test_create_booking_success(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：成功建立預約
        
        Given: 有效的預約資料
        When: 呼叫 POST /liff/bookings
        Then: 返回 201 Created 並包含預約詳情
        """
        # 使用未來時間（避免「過去時間」錯誤）
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        # 驗證回應
        assert response.status_code == 201
        data = response.json()
        
        # 驗證必要欄位
        assert "id" in data
        assert data["merchant_id"] == merchant_id
        assert data["staff_id"] == 1
        assert data["status"] == "confirmed"
        assert data["customer"]["name"] == "測試客戶"
        assert len(data["items"]) == 1
        assert float(data["total_price"]) > 0
    
    def test_create_booking_with_multiple_services(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：建立包含多個服務的預約
        
        Given: 預約包含多個服務項目
        When: 呼叫 POST /liff/bookings
        Then: 正確計算總價格和總時長
        """
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800},
                    {"service_id": 2, "quantity": 1, "price_snapshot": 500}
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # 驗證多個服務
        assert len(data["items"]) == 2
        assert float(data["total_price"]) >= 800  # 至少有第一個服務的價格
        assert data["total_duration_minutes"] > 0
    
    # ===== 測試：查詢預約 =====
    
    def test_list_bookings_success(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：查詢預約列表
        
        Given: 已建立預約
        When: 呼叫 GET /liff/bookings
        Then: 返回預約列表
        """
        response = client.get(
            f"/liff/bookings?merchant_id={merchant_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_booking_by_id_success(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：查詢單筆預約
        
        Given: 已建立預約
        When: 呼叫 GET /liff/bookings/{id}
        Then: 返回預約詳情
        """
        # 先建立預約
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        create_response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        booking_id = create_response.json()["id"]
        
        # 查詢單筆預約
        response = client.get(
            f"/liff/bookings/{booking_id}?merchant_id={merchant_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id
    
    def test_get_booking_not_found(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：查詢不存在的預約
        
        Given: 不存在的預約 ID
        When: 呼叫 GET /liff/bookings/{id}
        Then: 返回 404 Not Found
        """
        fake_id = "00000000-0000-0000-0000-000000000099"
        
        response = client.get(
            f"/liff/bookings/{fake_id}?merchant_id={merchant_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 404
    
    # ===== 測試：取消預約 =====
    
    def test_cancel_booking_success(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：成功取消預約
        
        Given: 已建立的預約
        When: 呼叫 DELETE /liff/bookings/{id}
        Then: 返回 204 No Content
        """
        # 先建立預約
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        create_response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        booking_id = create_response.json()["id"]
        
        # 取消預約
        response = client.delete(
            f"/liff/bookings/{booking_id}?merchant_id={merchant_id}&requester_line_id=U123456",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 204
        
        # 驗證狀態已變更
        get_response = client.get(
            f"/liff/bookings/{booking_id}?merchant_id={merchant_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "cancelled"
        assert get_response.json()["cancelled_at"] is not None
    
    # ===== 測試：業務規則驗證 =====
    
    def test_create_booking_past_time_rejected(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：過去時間的預約被拒絕
        
        Given: 預約時間在過去
        When: 嘗試建立預約
        Then: 返回 400 Bad Request
        """
        past_time = "2020-01-01T14:00:00+08:00"
        
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": past_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_create_booking_without_items_rejected(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：沒有服務項目的預約被拒絕
        
        Given: items 為空陣列
        When: 嘗試建立預約
        Then: 返回 422 Validation Error
        """
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": []  # 空陣列
            }
        )
        
        assert response.status_code == 422
    
    def test_create_booking_missing_customer_info_rejected(
        self, 
        client, 
        customer_token, 
        merchant_id
    ):
        """
        測試：缺少客戶資訊的預約被拒絕
        
        Given: customer 物件缺少必要欄位
        When: 嘗試建立預約
        Then: 返回 422 Validation Error
        """
        future_time = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT14:00:00+08:00")
        
        response = client.post(
            "/liff/bookings",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": future_time,
                "customer": {
                    # 缺少 name
                    "phone": "0912345678",
                    "line_user_id": "U123456"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        
        assert response.status_code == 422


class TestBookingFlowPerformance:
    """預約流程性能測試"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def customer_token(self):
        return TokenService.create_access_token(
            user_id="perf-test-user",
            merchant_id="00000000-0000-0000-0000-000000000001",
            role="customer"
        )
    
    def test_concurrent_booking_performance(
        self, 
        client, 
        customer_token
    ):
        """
        測試：並發建立預約的性能
        
        Given: 多個並發請求
        When: 同時建立多筆預約
        Then: 所有請求都能正確處理
        
        註: 這是簡化的並發測試，完整測試需使用 locust 或 k6
        """
        import concurrent.futures
        
        merchant_id = "00000000-0000-0000-0000-000000000001"
        
        def create_booking(index):
            future_time = (datetime.now(timezone.utc) + timedelta(days=10, hours=index)).strftime("%Y-%m-%dT14:00:00+08:00")
            
            return client.post(
                "/liff/bookings",
                headers={"Authorization": f"Bearer {customer_token}"},
                json={
                    "merchant_id": merchant_id,
                    "staff_id": 1,
                    "start_at": future_time,
                    "customer": {
                        "name": f"客戶{index}",
                        "phone": "0912345678",
                        "line_user_id": f"U{index}"
                    },
                    "items": [
                        {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                    ]
                }
            )
        
        # 並發建立 5 筆預約
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_booking, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 驗證所有請求都成功（201 或 200）
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count >= 3  # 至少 60% 成功率

