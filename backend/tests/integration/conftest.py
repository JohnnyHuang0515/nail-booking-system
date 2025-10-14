"""
整合測試框架 - Pytest Fixtures
提供資料庫連線、Session、資料清理等fixture
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

from shared.database import Base
from shared.config import settings


# PostgreSQL 連線引擎（整合測試用）
@pytest.fixture(scope="session")
def db_engine():
    """
    Session-scoped 資料庫引擎
    所有測試共用，測試結束後不關閉
    """
    engine = create_engine(
        str(settings.database_url),
        echo=False,  # 關閉 SQL 日誌（測試時太多）
        pool_pre_ping=True  # 測試連線是否有效
    )
    
    yield engine
    
    # Session 結束後關閉引擎
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Function-scoped 資料庫 Session
    每個測試函式獨立 Session，測試後自動回滾
    """
    # 建立 SessionLocal
    SessionLocal = sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False
    )
    
    session = SessionLocal()
    
    # 開啟交易
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    # 測試後回滾（不影響其他測試）
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def cleanup_booking_locks(db_engine):
    """
    每個測試後自動清理 booking_locks 表
    使用 autouse=True 確保所有測試後都執行
    """
    yield
    
    # 測試後清理
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        from booking.infrastructure.orm.models import BookingORM, BookingLockORM
        
        session.query(BookingORM).delete()
        session.query(BookingLockORM).delete()
        session.commit()
    except Exception as e:
        print(f"⚠️  清理失敗: {e}")
        session.rollback()
    finally:
        session.close()


@pytest.fixture(scope="function")
def db_session_commit(db_engine):
    """
    Function-scoped 資料庫 Session（會提交）
    用於需要真實寫入資料庫的測試（如測試 EXCLUDE 約束）
    """
    SessionLocal = sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False
    )
    
    session = SessionLocal()
    
    yield session
    
    # Session 結束
    try:
        session.close()
    except Exception:
        pass


# 測試資料工廠 Fixtures
@pytest.fixture
def test_merchant_id():
    """測試商家 ID（UUID 格式）"""
    from uuid import uuid4
    return str(uuid4())


@pytest.fixture
def test_staff_id():
    """測試員工 ID"""
    return 1


@pytest.fixture
def test_service_id():
    """測試服務 ID"""
    return 1


@pytest.fixture
def test_datetime_range():
    """測試時間範圍（用於預約）"""
    from datetime import datetime, timezone, timedelta
    
    TZ = timezone(timedelta(hours=8))
    start = datetime(2025, 10, 16, 10, 0, tzinfo=TZ)
    end = datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
    
    return {"start": start, "end": end}

