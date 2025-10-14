"""
Pytest Configuration - 全局 Fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from shared.database import Base
from booking.domain.models import Booking, BookingItem, Customer
from booking.domain.value_objects import Money, Duration

# 測試資料庫 URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/nail_booking_test"

TZ = ZoneInfo("Asia/Taipei")


@pytest.fixture(scope="session")
def test_engine():
    """測試資料庫引擎（Session 級別，整個測試期間共用）"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """測試資料庫 Session（Function 級別，每個測試獨立）"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_customer() -> Customer:
    """範例客戶"""
    return Customer(
        line_user_id="U123456789",
        name="王小明",
        phone="0912345678",
        email="test@example.com"
    )


@pytest.fixture
def sample_booking_item() -> BookingItem:
    """範例預約項目"""
    return BookingItem(
        service_id=1,
        service_name="Gel Basic",
        service_price=Money(Decimal("800"), "TWD"),
        service_duration=Duration(60),
        option_ids=[],
        option_names=[],
        option_prices=[],
        option_durations=[]
    )


@pytest.fixture
def sample_booking(sample_customer, sample_booking_item) -> Booking:
    """範例預約"""
    return Booking.create_new(
        merchant_id="123e4567-e89b-12d3-a456-426614174000",
        customer=sample_customer,
        staff_id=1,
        start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
        items=[sample_booking_item],
        notes="測試預約"
    )

