#!/usr/bin/env python3
"""
測試預約功能腳本
"""
import requests
import json
from datetime import date

def test_booking():
    """測試預約功能"""
    
    print("=== 測試預約功能 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試預約資料
    booking_data = {
        "customer_name": "測試用戶",
        "customer_phone": "0912345678",
        "customer_email": "test@example.com",
        "service_id": "e2d8817f-8b14-45a1-be54-fa2e1375780e",  # 光療美甲
        "appointment_date": "2024-10-06",
        "appointment_time": "12:00",
        "notes": "測試預約"
    }
    
    print(f"預約資料: {json.dumps(booking_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 提交預約
        url = f"{base_url}/api/v1/bookings?merchant_id={merchant_id}"
        response = requests.post(url, json=booking_data)
        
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 預約成功!")
            print(f"預約 ID: {result.get('id')}")
            print(f"預約日期: {result.get('appointment_date')}")
            print(f"預約時間: {result.get('appointment_time')}")
            print(f"客戶姓名: {result.get('customer_name')}")
            print(f"服務 ID: {result.get('service_id')}")
            print(f"狀態: {result.get('status')}")
            print(f"完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 預約失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 預約異常: {e}")

if __name__ == "__main__":
    test_booking()
