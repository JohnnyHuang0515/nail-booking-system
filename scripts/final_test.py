#!/usr/bin/env python3
"""
最終測試腳本 - 確認所有功能正常
"""
import requests
import json
from datetime import date

def final_test():
    """最終測試所有功能"""
    
    print("=== 最終測試 - 確認所有功能正常 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    test_date = "2024-10-06"
    
    print(f"商家 ID: {merchant_id}")
    print(f"測試日期: {test_date}")
    
    # 測試 1: 商家上下文 API
    print(f"\n1. 測試商家上下文 API")
    try:
        response = requests.get(f"{base_url}/api/v1/merchant-context/{merchant_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 商家上下文正常")
            print(f"   - 商家名稱: {data['merchant_name']}")
            print(f"   - 時區: {data['timezone']}")
            print(f"   - 狀態: {'啟用' if data['is_active'] else '停用'}")
        else:
            print(f"   ❌ 商家上下文失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 商家上下文異常: {e}")
    
    # 測試 2: 預約時段 API
    print(f"\n2. 測試預約時段 API")
    try:
        response = requests.get(f"{base_url}/api/v1/slots/{test_date}?merchant_id={merchant_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 預約時段正常，返回 {len(data)} 個時段")
            for slot in data:
                print(f"   - {slot['time']}: {'可用' if slot['available'] else '不可用'}")
        else:
            print(f"   ❌ 預約時段失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 預約時段異常: {e}")
    
    # 測試 3: 服務列表 API
    print(f"\n3. 測試服務列表 API")
    try:
        response = requests.get(f"{base_url}/api/v1/services?merchant_id={merchant_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 服務列表正常，返回 {len(data)} 個服務")
            for service in data:
                print(f"   - {service['name']}: ${service['price']} ({service['duration_minutes']}分鐘)")
        else:
            print(f"   ❌ 服務列表失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 服務列表異常: {e}")
    
    # 測試 4: 前端頁面
    print(f"\n4. 測試前端頁面")
    try:
        response = requests.get("http://localhost:3001")
        if response.status_code == 200:
            print(f"   ✅ 前端頁面正常載入")
        else:
            print(f"   ❌ 前端頁面失敗: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 前端頁面異常: {e}")
    
    print(f"\n=== 測試完成 ===")
    print(f"現在您可以訪問 http://localhost:3001 來使用預約系統")
    print(f"應該可以看到可預約時段：12:00, 15:00, 18:00")

if __name__ == "__main__":
    final_test()
