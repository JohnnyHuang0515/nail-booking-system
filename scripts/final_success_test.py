#!/usr/bin/env python3
"""
最終預約成功頁面測試腳本
"""
import requests
import json
from datetime import date

def final_success_test():
    """最終預約成功頁面測試"""
    
    print("=== 最終預約成功頁面測試 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試預約
    print("1. 測試預約流程")
    booking_data = {
        "customer_name": "測試用戶",
        "customer_phone": "0912345678",
        "customer_email": "test@example.com",
        "service_id": "e2d8817f-8b14-45a1-be54-fa2e1375780e",  # 光療美甲
        "appointment_date": "2024-10-06",
        "appointment_time": "15:00",
        "notes": "最終測試"
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
            print(f"\n2. 模擬前端顯示")
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
            
            # 檢查資料完整性
            print(f"\n3. 資料完整性檢查")
            if result.get('id'):
                print("   ✅ 預約編號: 正常")
            else:
                print("   ❌ 預約編號: 缺失")
                
            if result.get('appointment_time'):
                print("   ✅ 預約時間: 正常")
            else:
                print("   ❌ 預約時間: 缺失")
                
            if result.get('customer_name'):
                print("   ✅ 客戶姓名: 正常")
            else:
                print("   ❌ 客戶姓名: 缺失")
                
            if result.get('customer_phone'):
                print("   ✅ 客戶電話: 正常")
            else:
                print("   ❌ 客戶電話: 缺失")
            
        else:
            print(f"   ❌ 預約失敗: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 預約異常: {e}")
    
    print(f"\n=== 測試完成 ===")
    print(f"現在預約成功頁面應該顯示:")
    print(f"- 正確的預約編號 (UUID)")
    print(f"- 正確的時間範圍 (15:00 - 17:00)")
    print(f"- 正確的服務名稱 (光療美甲)")
    print(f"- 正確的服務資訊 (120分鐘, NT$1800)")
    print(f"- 正確的客戶資訊")

if __name__ == "__main__":
    final_success_test()
