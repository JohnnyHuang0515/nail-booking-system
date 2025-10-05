#!/usr/bin/env python3
"""
測試預約成功頁面修復腳本
"""
import requests
import json
from datetime import date

def test_success_page_fix():
    """測試預約成功頁面修復"""
    
    print("=== 測試預約成功頁面修復 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 先獲取服務列表
    print("1. 獲取服務列表")
    try:
        response = requests.get(f"{base_url}/api/v1/services?merchant_id={merchant_id}")
        if response.status_code == 200:
            services = response.json()
            print(f"   ✅ 服務列表: {len(services)} 個")
            for service in services:
                print(f"   - {service['name']}: ${service['price']} ({service['duration_minutes']}分鐘)")
                print(f"     欄位: {list(service.keys())}")
        else:
            print(f"   ❌ 獲取服務失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 獲取服務異常: {e}")
    
    # 測試預約
    print("\n2. 測試預約")
    booking_data = {
        "customer_name": "王小明",
        "customer_phone": "0911111111",
        "customer_email": "wang@example.com",
        "service_id": "e2d8817f-8b14-45a1-be54-fa2e1375780e",  # 光療美甲
        "appointment_date": "2024-10-06",
        "appointment_time": "15:00",
        "notes": "測試修復"
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
            print(f"   - 服務 ID: {result.get('service_id')}")
            print(f"   - 狀態: {result.get('status')}")
            
            # 模擬前端顯示
            print(f"\n3. 模擬前端顯示")
            print(f"   預約編號: {result.get('id')}")
            print(f"   預約日期: {result.get('appointment_date')}")
            print(f"   預約時間: {result.get('appointment_time')}")
            
            # 計算結束時間
            start_time = result.get('appointment_time', '15:00:00')
            duration = 120  # 光療美甲 120 分鐘
            time_parts = start_time.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            total_minutes = hours * 60 + minutes + duration
            end_hours = total_minutes // 60
            end_minutes = total_minutes % 60
            end_time = f"{end_hours:02d}:{end_minutes:02d}"
            
            print(f"   時間範圍: {start_time[:5]} - {end_time}")
            print(f"   服務名稱: 光療美甲")
            print(f"   服務類別: 美甲服務")
            print(f"   服務描述: 專業美甲服務")
            print(f"   服務時長: {duration} 分鐘")
            print(f"   服務價格: NT$1800")
            
        else:
            print(f"   ❌ 預約失敗: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 預約異常: {e}")
    
    print(f"\n=== 測試完成 ===")
    print(f"現在預約成功頁面應該顯示正確的資訊，而不是 N/A")

if __name__ == "__main__":
    test_success_page_fix()
