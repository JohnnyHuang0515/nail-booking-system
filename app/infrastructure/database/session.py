import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Database Configuration ---
# To run the application, you need to set the DATABASE_URL environment variable.
# This URL specifies how to connect to your PostgreSQL database.
#
# Format: postgresql://<user>:<password>@<host>:<port>/<database_name>
#
# Example for a local PostgreSQL instance:
# export DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/nail_booking_db"
#
# If the DATABASE_URL is not set, it will fall back to a default value,
# which is intended for demonstration purposes and may not work in your environment.
def get_database_url():
    """Get DATABASE_URL from environment variable."""
    return os.getenv("DATABASE_URL", "postgresql://user:password@localhost/nail_booking_db")

def get_engine():
    """Get database engine, creating it dynamically."""
    database_url = get_database_url()
    if database_url == "postgresql://user:password@localhost/nail_booking_db":
        print("WARNING: Using default DATABASE_URL. Please set the environment variable for your database.")
    
    # 優化連接池設定以降低 CPU 使用
    return create_engine(
        database_url,
        pool_size=5,           # 連接池大小（預設 5）
        max_overflow=10,       # 最大溢出連接數（預設 10）
        pool_pre_ping=True,    # 使用前檢查連接是否有效
        pool_recycle=3600,     # 1小時後回收連接
        echo=False             # 關閉 SQL 日誌（減少 I/O）
    )

def get_session_local():
    """Get session maker, creating it dynamically."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# For backward compatibility
DATABASE_URL = get_database_url()
engine = get_engine()
SessionLocal = get_session_local()

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Get database session directly (not a generator)."""
    return SessionLocal()
