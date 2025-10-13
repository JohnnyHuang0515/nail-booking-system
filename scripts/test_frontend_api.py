#!/usr/bin/env python3
"""
測試前端 API 呼叫腳本
"""
import requests
import json

def test_api_calls():
    """測試前端會用到的 API 呼叫"""
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    test_date = "2024-10-06"
    
    print("=== 測試前端 API 呼叫 ===")
    
    # 測試 1: 獲取可用時段
    print(f"\n1. 測試獲取可用時段: {test_date}")
    try:
        url = f"{base_url}/api/v1/slots/{test_date}?merchant_id={merchant_id}"
        response = requests.get(url)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"   請求失敗: {e}")
    
    # 測試 2: 獲取服務列表
    print(f"\n2. 測試獲取服務列表")
    try:
        url = f"{base_url}/api/v1/services?merchant_id={merchant_id}"
        response = requests.get(url)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"   請求失敗: {e}")
    
    # 測試 3: 獲取休假日
    print(f"\n3. 測試獲取休假日")
    try:
        url = f"{base_url}/api/v1/schedule/time_off/all"
        response = requests.get(url)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"   請求失敗: {e}")

if __name__ == "__main__":
    test_api_calls()
