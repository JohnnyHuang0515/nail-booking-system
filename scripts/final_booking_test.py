#!/usr/bin/env python3
"""
最終預約流程測試腳本
"""
import requests
import json
from datetime import date

def final_booking_test():
    """最終預約流程測試"""
    
    print("=== 最終預約流程測試 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試完整的預約流程
    print("1. 測試獲取可用時段")
    try:
        response = requests.get(f"{base_url}/api/v1/slots/2024-10-06?merchant_id={merchant_id}")
        if response.status_code == 200:
            slots = response.json()
            print(f"   ✅ 可用時段: {len(slots)} 個")
            for slot in slots:
                print(f"   - {slot['time']}: {'可用' if slot['available'] else '不可用'}")
        else:
            print(f"   ❌ 獲取時段失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 獲取時段異常: {e}")
    
    print("\n2. 測試獲取服務列表")
    try:
        response = requests.get(f"{base_url}/api/v1/services?merchant_id={merchant_id}")
        if response.status_code == 200:
            services = response.json()
            print(f"   ✅ 服務列表: {len(services)} 個")
            for service in services:
                print(f"   - {service['name']}: ${service['price']} ({service['duration_minutes']}分鐘)")
        else:
            print(f"   ❌ 獲取服務失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 獲取服務異常: {e}")
    
    print("\n3. 測試提交預約")
    booking_data = {
        "customer_name": "李四",
        "customer_phone": "0987654321",
        "customer_email": "li@example.com",
        "service_id": "b4da790e-948d-4f59-8a13-895ed1dfed6d",  # 基礎美甲
        "appointment_date": "2024-10-06",
        "appointment_time": "18:00",
        "notes": "最終測試預約"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/bookings?merchant_id={merchant_id}", json=booking_data)
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ 預約成功!")
            print(f"   - 預約 ID: {result.get('id')}")
            print(f"   - 預約日期: {result.get('appointment_date')}")
            print(f"   - 預約時間: {result.get('appointment_time')}")
            print(f"   - 客戶姓名: {result.get('customer_name')}")
            print(f"   - 客戶電話: {result.get('customer_phone')}")
            print(f"   - 狀態: {result.get('status')}")
            
            # 驗證資料完整性
            if result.get('id') and result.get('customer_name') and result.get('appointment_time'):
                print("   ✅ 預約資料完整")
            else:
                print("   ❌ 預約資料不完整")
        else:
            print(f"   ❌ 預約失敗: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 預約異常: {e}")
    
    print("\n4. 測試前端頁面")
    try:
        response = requests.get("http://localhost:3001")
        if response.status_code == 200:
            print("   ✅ 前端頁面正常載入")
        else:
            print(f"   ❌ 前端頁面載入失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 前端頁面異常: {e}")
    
    print(f"\n=== 測試完成 ===")
    print(f"現在您可以訪問 http://localhost:3001 來測試預約功能")
    print(f"預約成功後應該可以看到正確的訂單編號和時間")

if __name__ == "__main__":
    final_booking_test()
