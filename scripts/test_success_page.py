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
    
    # 測試預約資料
    booking_data = {
        "customer_name": "張三",
        "customer_phone": "0912345678",
        "customer_email": "zhang@example.com",
        "service_id": "e2d8817f-8b14-45a1-be54-fa2e1375780e",  # 光療美甲
        "appointment_date": "2024-10-06",
        "appointment_time": "15:00",
        "notes": "測試預約成功頁面"
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
            print(f"客戶電話: {result.get('customer_phone')}")
            print(f"服務 ID: {result.get('service_id')}")
            print(f"狀態: {result.get('status')}")
            
            # 檢查時間格式
            appointment_time = result.get('appointment_time')
            if appointment_time:
                print(f"時間格式檢查: {appointment_time}")
                if ':' in appointment_time:
                    time_parts = appointment_time.split(':')
                    print(f"時間部分: {time_parts}")
                    if len(time_parts) >= 2:
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        print(f"小時: {hours}, 分鐘: {minutes}")
                        if not (isNaN(hours) or isNaN(minutes)):
                            print("✅ 時間格式正確")
                        else:
                            print("❌ 時間格式錯誤")
                    else:
                        print("❌ 時間格式不完整")
                else:
                    print("❌ 時間格式無效")
            
            print(f"\n完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 預約失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 預約異常: {e}")

def isNaN(value):
    """檢查是否為 NaN"""
    try:
        return float(value) != float(value)
    except (ValueError, TypeError):
        return True

if __name__ == "__main__":
    test_success_page_fix()
