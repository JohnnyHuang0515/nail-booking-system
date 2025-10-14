"""
RBAC 權限測試腳本
測試所有角色的權限與租戶隔離
"""
import requests
import json
from typing import Optional


BASE_URL = "http://localhost:8000"
MERCHANT_ID_1 = "00000000-0000-0000-0000-000000000001"
MERCHANT_ID_2 = "11111111-1111-1111-1111-111111111111"


class RBACTester:
    """RBAC 測試器"""
    
    def __init__(self):
        self.results = []
        self.tokens = {}
    
    def test(self, name: str, expected: bool, func):
        """執行單個測試"""
        try:
            func()
            actual = True
            status = "✅" if actual == expected else "❌"
        except requests.HTTPError as e:
            actual = False
            status = "✅" if actual == expected else "❌"
            if not expected:
                # 預期失敗，檢查狀態碼
                if e.response.status_code in [401, 403]:
                    status = "✅"
        except Exception as e:
            actual = False
            status = "❌"
        
        self.results.append({
            "name": name,
            "expected": "通過" if expected else "拒絕",
            "actual": "通過" if actual else "拒絕",
            "status": status
        })
        
        print(f"{status} {name} - 預期{self.results[-1]['expected']}")
    
    def register_user(self, email: str, password: str, name: str, role: str = "customer") -> dict:
        """註冊用戶"""
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "name": name,
            "merchant_id": MERCHANT_ID_1
        })
        resp.raise_for_status()
        return resp.json()
    
    def login(self, email: str, password: str) -> str:
        """登入並返回 token"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        resp.raise_for_status()
        data = resp.json()
        return data["access_token"]
    
    def get_me(self, token: str) -> dict:
        """取得當前用戶資訊"""
        resp = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        return resp.json()
    
    def create_booking(self, token: str, merchant_id: str = MERCHANT_ID_1):
        """建立預約"""
        resp = requests.post(
            f"{BASE_URL}/liff/bookings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "merchant_id": merchant_id,
                "staff_id": 1,
                "start_at": "2025-10-25T14:00:00+08:00",
                "customer": {
                    "name": "測試客戶",
                    "phone": "0912345678",
                    "line_user_id": "Utest123"
                },
                "items": [
                    {"service_id": 1, "quantity": 1, "price_snapshot": 800}
                ]
            }
        )
        resp.raise_for_status()
        return resp.json()
    
    def list_bookings(self, token: str, merchant_id: str = MERCHANT_ID_1):
        """查詢預約列表"""
        resp = requests.get(
            f"{BASE_URL}/liff/bookings",
            headers={"Authorization": f"Bearer {token}"},
            params={"merchant_id": merchant_id}
        )
        resp.raise_for_status()
        return resp.json()
    
    def cancel_booking(self, token: str, booking_id: str, merchant_id: str = MERCHANT_ID_1):
        """取消預約"""
        resp = requests.delete(
            f"{BASE_URL}/liff/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "merchant_id": merchant_id,
                "requester_line_id": "Utest123"
            }
        )
        resp.raise_for_status()
    
    def print_summary(self):
        """打印測試摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "✅")
        
        print("\n" + "="*60)
        print(f"📊 測試摘要: {passed}/{total} 通過 ({passed/total*100:.1f}%)")
        print("="*60)
        
        if passed < total:
            print("\n❌ 失敗的測試:")
            for r in self.results:
                if r["status"] == "❌":
                    print(f"  - {r['name']}")


def main():
    """主測試流程"""
    tester = RBACTester()
    
    print("🚀 開始 RBAC 權限測試\n")
    
    # ===== 1. Customer 角色測試 =====
    print("=" * 60)
    print("📋 測試 Customer 角色權限")
    print("=" * 60)
    
    # 註冊 Customer
    import time
    timestamp = int(time.time())
    customer_email = f"customer{timestamp}@test.com"
    
    customer = tester.register_user(
        customer_email,
        "customer123",
        "測試顧客",
        "customer"
    )
    customer_token = tester.login(customer_email, "customer123")
    
    # 取得當前用戶資訊
    tester.test(
        "Customer - 取得自己的資訊 (/auth/me)",
        expected=True,
        func=lambda: tester.get_me(customer_token)
    )
    
    # 建立預約 (有權限)
    tester.test(
        "Customer - 建立預約 (BOOKING_CREATE)",
        expected=True,
        func=lambda: tester.create_booking(customer_token)
    )
    
    # 查詢預約列表 (有權限)
    tester.test(
        "Customer - 查詢預約列表 (BOOKING_READ)",
        expected=True,
        func=lambda: tester.list_bookings(customer_token)
    )
    
    # 跨租戶訪問 (無權限)
    tester.test(
        "Customer - 跨租戶查詢預約 (應拒絕)",
        expected=False,
        func=lambda: tester.list_bookings(customer_token, MERCHANT_ID_2)
    )
    
    print("\n✅ Customer 角色測試完成\n")
    
    # ===== 2. 無 Token 測試 =====
    print("=" * 60)
    print("📋 測試未認證訪問")
    print("=" * 60)
    
    tester.test(
        "無 Token - 訪問受保護端點 (應拒絕)",
        expected=False,
        func=lambda: tester.get_me("")
    )
    
    print("\n✅ 未認證測試完成\n")
    
    # ===== 3. Token 驗證測試 =====
    print("=" * 60)
    print("📋 測試 JWT Token 內容")
    print("=" * 60)
    
    me = tester.get_me(customer_token)
    print(f"✅ Token 解析成功:")
    print(f"  User ID: {me['id']}")
    print(f"  Email: {me['email']}")
    print(f"  Role: {me['role']}")
    print(f"  Merchant ID: {me['merchant_id']}")
    
    # 打印測試摘要
    tester.print_summary()
    
    # 生成 JSON 報告
    with open("/tmp/rbac_test_results.json", "w") as f:
        json.dump({
            "total": len(tester.results),
            "passed": sum(1 for r in tester.results if r["status"] == "✅"),
            "failed": sum(1 for r in tester.results if r["status"] == "❌"),
            "results": tester.results
        }, f, indent=2, ensure_ascii=False)
    
    print("\n📄 詳細報告已保存: /tmp/rbac_test_results.json")


if __name__ == "__main__":
    main()

