#!/usr/bin/env python3
"""
檢查營業時間設定腳本
"""
import sys
import os
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.session import engine
from app.infrastructure.database.models import BusinessHour, Merchant

# 創建資料庫會話
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_business_hours():
    """檢查營業時間設定"""
    
    db_session = SessionLocal()
    try:
        print("=== 商家列表 ===")
        merchants = db_session.query(Merchant).all()
        if not merchants:
            print("沒有找到任何商家")
            return
        
        for merchant in merchants:
            print(f"  - {merchant.id}: {merchant.name} (帳號: {merchant.account})")

        print("\n=== 營業時間設定 ===")
        business_hours = db_session.query(BusinessHour).all()
        if not business_hours:
            print("❌ 沒有找到營業時間設定！")
            print("這就是為什麼沒有可預約時段的原因。")
            return
        
        # 按商家分組顯示
        merchant_hours = {}
        for bh in business_hours:
            if bh.merchant_id not in merchant_hours:
                merchant_hours[bh.merchant_id] = []
            merchant_hours[bh.merchant_id].append(bh)
        
        for merchant_id, hours in merchant_hours.items():
            merchant = next((m for m in merchants if m.id == merchant_id), None)
            merchant_name = merchant.name if merchant else f"未知商家 ({merchant_id})"
            print(f"\n商家: {merchant_name}")
            for bh in sorted(hours, key=lambda x: x.day_of_week):
                day_names = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
                print(f"  - {day_names[bh.day_of_week]}: {bh.start_time} - {bh.end_time}")
        
    except Exception as e:
        print(f"檢查失敗: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    check_business_hours()
