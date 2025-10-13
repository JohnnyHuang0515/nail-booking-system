#!/usr/bin/env python3
"""
測試前端 JavaScript 執行腳本
"""
import requests
import json

def test_frontend_js():
    """測試前端 JavaScript 執行"""
    
    print("=== 測試前端 JavaScript 執行 ===")
    
    # 測試前端頁面是否正常載入
    try:
        response = requests.get("http://localhost:3001")
        print(f"前端頁面狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 前端頁面正常載入")
            
            # 檢查頁面內容
            content = response.text
            if "美甲預約系統" in content:
                print("✅ 頁面標題正確")
            else:
                print("❌ 頁面標題不正確")
                
            if "react" in content.lower() or "app" in content.lower():
                print("✅ 頁面包含 React 應用")
            else:
                print("❌ 頁面可能沒有正確載入 React 應用")
        else:
            print(f"❌ 前端頁面載入失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 無法連接到前端: {e}")
    
    # 測試前端是否能正確呼叫 API
    print(f"\n--- 測試前端 API 呼叫 ---")
    
    # 模擬前端的 API 呼叫
    test_url = "http://localhost:8000/api/v1/slots/2024-10-06?merchant_id=930d5cde-2e01-456a-915c-92c234b613bc"
    
    try:
        # 使用與前端相同的 headers
        headers = {
            'Origin': 'http://localhost:3001',
            'Referer': 'http://localhost:3001/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers)
        print(f"API 呼叫狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 呼叫成功，返回 {len(data)} 個時段")
            print(f"時段資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API 呼叫失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ API 呼叫異常: {e}")

if __name__ == "__main__":
    test_frontend_js()
