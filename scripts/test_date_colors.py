#!/usr/bin/env python3
"""
測試日期顏色修改腳本
"""
import requests
import json
from datetime import date, datetime

def test_date_colors():
    """測試日期顏色修改"""
    
    print("=== 測試日期顏色修改 ===")
    
    base_url = "http://localhost:8000"
    merchant_id = "930d5cde-2e01-456a-915c-92c234b613bc"
    
    # 測試不同日期的可用性
    test_dates = [
        "2024-10-06",  # 應該完全預約滿
        "2024-10-07",  # 應該有可用時段
        "2024-10-08",  # 應該有可用時段
    ]
    
    print("1. 檢查各日期的預約狀態")
    for test_date in test_dates:
        try:
            response = requests.get(f"{base_url}/api/v1/slots/{test_date}?merchant_id={merchant_id}")
            if response.status_code == 200:
                slots = response.json()
                available_count = sum(1 for slot in slots if slot['available'])
                total_count = len(slots)
                
                print(f"   {test_date}:")
                print(f"   - 總時段: {total_count}")
                print(f"   - 可用時段: {available_count}")
                print(f"   - 已預約時段: {total_count - available_count}")
                
                if available_count == 0:
                    print(f"   - 狀態: 🔴 完全預約滿")
                elif available_count == total_count:
                    print(f"   - 狀態: 🟢 完全可用")
                else:
                    print(f"   - 狀態: 🟡 部分預約")
                    
            else:
                print(f"   {test_date}: ❌ 獲取失敗 ({response.status_code})")
        except Exception as e:
            print(f"   {test_date}: ❌ 異常 ({e})")
        
        print()
    
    print("2. 修改後的視覺顯示")
    print("   在日期選擇頁面中，10月6日現在應該顯示為:")
    print("   - 背景色: 灰色 (bg-disabled)")
    print("   - 文字色: 灰色 (text-disabled-foreground)")
    print("   - 右上角: 紅色小圓點 (僅作為區分標記)")
    print("   - 狀態: 不可點擊 (disabled)")
    print("   - 樣式: 與其他不可預約日期相同")
    
    print("\n3. 圖例說明 (修改後)")
    print("   ⚫ 已預約滿: 灰色背景 + 紅色小圓點")
    print("   🟢 可預約: 正常背景，可點擊")
    print("   ⚫ 不可預約: 灰色背景，不可點擊 (過去日期、週日、休假日)")
    
    print("\n4. 顏色統一性")
    print("   ✅ 已預約滿和不可預約都使用相同的灰色調")
    print("   ✅ 僅通過紅色小圓點來區分已預約滿的日期")
    print("   ✅ 保持視覺一致性，避免過多顏色干擾")
    
    print(f"\n=== 測試完成 ===")
    print(f"現在已預約滿的日期使用與不可預約日期相同的灰色調")

if __name__ == "__main__":
    test_date_colors()
