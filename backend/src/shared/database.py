"""
Shared Kernel - Database Connection
SQLAlchemy Engine 與 Session 管理
"""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from .config import settings


# SQLAlchemy Base for ORM models
Base = declarative_base()


# Database Engine
def create_db_engine():
    """建立資料庫引擎"""
    engine = create_engine(
        str(settings.database_url),
        poolclass=QueuePool if not settings.debug else NullPool,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.database_echo,
        pool_pre_ping=True,  # 驗證連線有效性
    )
    
    # 設定 PostgreSQL 時區
    @event.listens_for(engine, "connect")
    def set_timezone(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute(f"SET TIME ZONE '{settings.default_timezone}'")
        cursor.close()
    
    return engine


# Create engine instance
engine = create_db_engine()


# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency - 取得資料庫 Session
    
    用法：
        @app.get("/bookings")
        def get_bookings(db: Session = Depends(get_db)):
            return db.query(Booking).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """建立所有資料表（僅用於開發環境）"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """刪除所有資料表（僅用於測試環境）"""
    Base.metadata.drop_all(bind=engine)

