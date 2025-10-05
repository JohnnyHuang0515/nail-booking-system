#!/usr/bin/env python3
"""
調試前端 API 呼叫腳本
"""
import requests
import json
from datetime import datetime, date

def debug_frontend_api():
    """調試前端 API 呼叫"""
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試今天的日期
    today = date.today()
    test_dates = [
        today.strftime("%Y-%m-%d"),
        "2024-10-06",
        "2024-10-07",
        "2024-10-08"
    ]
    
    print("=== 調試前端 API 呼叫 ===")
    print(f"商家 ID: {merchant_id}")
    print(f"今天日期: {today}")
    
    for test_date in test_dates:
        print(f"\n--- 測試日期: {test_date} ---")
        
        # 測試 API 呼叫
        try:
            url = f"{base_url}/api/v1/slots/{test_date}?merchant_id={merchant_id}"
            print(f"API URL: {url}")
            
            response = requests.get(url)
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"返回資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print(f"時段數量: {len(data)}")
                
                if len(data) == 0:
                    print("⚠️  沒有返回任何時段！")
                else:
                    print("✅ 有返回時段")
            else:
                print(f"❌ API 錯誤: {response.text}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")

if __name__ == "__main__":
    debug_frontend_api()
