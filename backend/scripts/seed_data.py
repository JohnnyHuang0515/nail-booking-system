#!/usr/bin/env python3
"""
測試資料載入腳本
用途：為開發環境載入範例商家、服務、員工資料
"""
import sys
from pathlib import Path
from datetime import time
from decimal import Decimal
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from shared.database import SessionLocal
from catalog.domain.models import Service, Staff, StaffWorkingHours, DayOfWeek, ServiceOption
from catalog.infrastructure.repositories.sqlalchemy_service_repository import SQLAlchemyServiceRepository
from catalog.infrastructure.repositories.sqlalchemy_staff_repository import SQLAlchemyStaffRepository
from merchant.domain.models import Merchant, MerchantStatus
from merchant.infrastructure.repositories.sqlalchemy_merchant_repository import SQLAlchemyMerchantRepository
from billing.domain.models import Plan, PlanTier, Subscription, SubscriptionStatus, PlanFeatures
from billing.infrastructure.repositories.sqlalchemy_plan_repository import SQLAlchemyPlanRepository
from billing.infrastructure.repositories.sqlalchemy_subscription_repository import SQLAlchemySubscriptionRepository
from booking.domain.value_objects import Money, Duration


def seed_merchant_data(db: Session):
    """載入 Merchant 測試資料"""
    
    merchant_repo = SQLAlchemyMerchantRepository(db)
    
    merchant_id = "00000000-0000-0000-0000-000000000001"
    
    print("🏪 載入商家資料...")
    
    # 建立測試商家
    merchant = Merchant(
        id=merchant_id,
        slug="nail-abc",
        name="美甲沙龍 ABC",
        status=MerchantStatus.ACTIVE,
        timezone="Asia/Taipei",
        address="台北市大安區復興南路一段123號",
        phone="02-27001234"
    )
    
    merchant_repo.save(merchant)
    db.commit()
    
    print("✅ 1 個商家已載入")
    
    return merchant_id


def seed_catalog_data(db: Session, merchant_id: str):
    """載入 Catalog 測試資料"""
    
    service_repo = SQLAlchemyServiceRepository(db)
    staff_repo = SQLAlchemyStaffRepository(db)
    
    print("📋 載入服務資料...")
    
    # === 建立服務 ===
    
    # 服務 1: 基礎凝膠指甲
    gel_basic = Service(
        id=1,
        merchant_id=merchant_id,
        name="基礎凝膠指甲",
        base_price=Money(amount=Decimal("800"), currency="TWD"),
        base_duration=Duration(minutes=60),
        category="基礎服務",
        description="基礎凝膠指甲服務",
        is_active=True,
        allow_stack=True,
        options=[
            ServiceOption(
                id=1,
                service_id=1,
                name="法式造型",
                add_price=Money(amount=Decimal("200")),
                add_duration=Duration(minutes=15),
                is_active=True,
                display_order=1
            ),
            ServiceOption(
                id=2,
                service_id=1,
                name="手繪彩繪",
                add_price=Money(amount=Decimal("300")),
                add_duration=Duration(minutes=20),
                is_active=True,
                display_order=2
            )
        ]
    )
    
    # 服務 2: 手部保養
    hand_care = Service(
        id=2,
        merchant_id=merchant_id,
        name="手部保養",
        base_price=Money(amount=Decimal("500"), currency="TWD"),
        base_duration=Duration(minutes=45),
        category="保養護理",
        description="深層手部保養護理",
        is_active=True,
        allow_stack=True,
        options=[]
    )
    
    # 服務 3: 豪華凝膠指甲
    gel_luxury = Service(
        id=3,
        merchant_id=merchant_id,
        name="豪華凝膠指甲",
        base_price=Money(amount=Decimal("1500"), currency="TWD"),
        base_duration=Duration(minutes=90),
        category="豪華服務",
        description="頂級凝膠指甲，含設計",
        is_active=True,
        allow_stack=False,
        options=[]
    )
    
    service_repo.save(gel_basic)
    service_repo.save(hand_care)
    service_repo.save(gel_luxury)
    
    print("✅ 3 個服務已載入")
    
    # === 建立員工 ===
    
    print("👤 載入員工資料...")
    
    # 員工 1: Amy（全能型）
    amy = Staff(
        id=1,
        merchant_id=merchant_id,
        name="Amy",
        email="amy@nail-abc.com",
        phone="0912345678",
        skills=[1, 2, 3],  # 可執行所有服務
        is_active=True,
        working_hours=[
            # 週日到週六 全天
            StaffWorkingHours(DayOfWeek.SUNDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.MONDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.TUESDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.WEDNESDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.THURSDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.FRIDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.SATURDAY, time(0, 0), time(23, 59)),
        ]
    )
    
    # 員工 2: Betty（專精基礎服務）
    betty = Staff(
        id=2,
        merchant_id=merchant_id,
        name="Betty",
        email="betty@nail-abc.com",
        phone="0923456789",
        skills=[1, 2],  # 只能執行基礎服務
        is_active=True,
        working_hours=[
            # 週日到週六 全天
            StaffWorkingHours(DayOfWeek.SUNDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.MONDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.TUESDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.WEDNESDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.THURSDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.FRIDAY, time(0, 0), time(23, 59)),
            StaffWorkingHours(DayOfWeek.SATURDAY, time(0, 0), time(23, 59)),
        ]
    )
    
    staff_repo.save(amy)
    staff_repo.save(betty)
    
    print("✅ 2 個員工已載入")
    
    db.commit()
    print("🎉 測試資料載入完成！")


def seed_billing_data(db: Session, merchant_id: str):
    """載入 Billing 測試資料"""
    
    plan_repo = SQLAlchemyPlanRepository(db)
    subscription_repo = SQLAlchemySubscriptionRepository(db)
    
    print("💳 載入方案資料...")
    
    # 建立方案（直接插入 ORM，因為 Plan 沒有 save 方法）
    from billing.infrastructure.orm.models import PlanORM
    
    # 檢查是否已存在
    existing_plans = db.query(PlanORM).count()
    
    if existing_plans == 0:
        # 基礎方案
        basic_plan = PlanORM(
            id=1,
            tier="basic",
            name="基礎方案",
            description="適合個人工作室",
            price_amount=Decimal("999"),
            price_currency="TWD",
            billing_interval="month",
            features={
                "max_bookings_per_month": 100,
                "max_staff": 3,
                "max_services": 20,
                "enable_line_notification": True,
                "enable_custom_branding": False,
                "enable_analytics": False,
                "support_level": "email"
            },
            is_active=True
        )
        
        db.add(basic_plan)
        db.commit()
        
        print("✅ 1 個方案已載入")
    else:
        print("⏭️  方案已存在，跳過")
    
    print("📋 載入訂閱資料...")
    
    # 為測試商家建立訂閱（試用中）
    from datetime import datetime, timedelta, timezone as dt_timezone
    
    now = datetime.now(dt_timezone.utc)
    trial_end = now + timedelta(days=14)
    
    subscription = Subscription(
        id=str(uuid4()),
        merchant_id=merchant_id,
        plan_id=1,
        status=SubscriptionStatus.TRIALING,
        current_period_start=now,
        current_period_end=trial_end,
        trial_end=trial_end
    )
    
    subscription_repo.save(subscription)
    db.commit()
    
    print("✅ 1 個訂閱已載入（試用中）")


def main():
    """主函式"""
    print("🌱 載入測試資料...")
    
    db = SessionLocal()
    try:
        # 先載入商家
        merchant_id = seed_merchant_data(db)
        
        # 載入計費資料（方案與訂閱）
        seed_billing_data(db, merchant_id)
        
        # 再載入服務與員工
        seed_catalog_data(db, merchant_id)
    except Exception as e:
        print(f"❌ 載入失敗: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

