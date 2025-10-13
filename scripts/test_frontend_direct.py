#!/usr/bin/env python3
"""
直接測試前端行為腳本
"""
import requests
import json
from datetime import datetime, date

def test_frontend_direct():
    """直接測試前端行為"""
    
    print("=== 直接測試前端行為 ===")
    
    # 測試前端是否能正確處理 API 呼叫
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試今天的日期
    today = date.today()
    test_date = today.strftime("%Y-%m-%d")
    
    print(f"測試日期: {test_date}")
    print(f"商家 ID: {merchant_id}")
    
    # 測試 API 呼叫
    try:
        url = f"{base_url}/api/v1/slots/{test_date}?merchant_id={merchant_id}"
        print(f"API URL: {url}")
        
        response = requests.get(url)
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 返回 {len(data)} 個時段")
            print(f"時段資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 檢查時段是否正確
            if len(data) > 0:
                print("✅ 有可用時段")
                for slot in data:
                    print(f"  - {slot['time']}: {'可用' if slot['available'] else '不可用'}")
            else:
                print("❌ 沒有可用時段")
        else:
            print(f"❌ API 錯誤: {response.text}")
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")
    
    # 測試前端頁面
    print(f"\n--- 測試前端頁面 ---")
    try:
        response = requests.get("http://localhost:3001")
        if response.status_code == 200:
            print("✅ 前端頁面正常載入")
            
            # 檢查頁面內容
            content = response.text
            if "美甲預約系統" in content:
                print("✅ 頁面標題正確")
            if "root" in content:
                print("✅ 有 React root 元素")
            if "bundle.js" in content:
                print("✅ 有 React bundle")
        else:
            print(f"❌ 前端頁面載入失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 無法連接到前端: {e}")

if __name__ == "__main__":
    test_frontend_direct()
