#!/usr/bin/env python3
"""
初始化資料庫腳本
用途：建立資料庫、執行遷移、載入測試資料
"""
import sys
from pathlib import Path

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from shared.config import settings
from shared.database import Base, engine


def create_database():
    """建立資料庫（如果不存在）"""
    # 連接到 postgres 預設資料庫
    db_url = str(settings.database_url)
    db_name = db_url.split("/")[-1]
    
    postgres_url = db_url.replace(f"/{db_name}", "/postgres")
    postgres_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
    
    with postgres_engine.connect() as conn:
        # 檢查資料庫是否存在
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )
        exists = result.scalar()
        
        if not exists:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"ℹ️  Database '{db_name}' already exists")
    
    postgres_engine.dispose()


def create_extensions():
    """建立必要的 PostgreSQL Extensions"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
        conn.commit()
        print("✅ Extensions created (btree_gist, uuid-ossp)")


def create_tables():
    """建立所有資料表（開發環境用）"""
    print("⚠️  Creating tables directly (not recommended for production)")
    print("ℹ️  Use 'alembic upgrade head' for production")
    
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")


def main():
    """主函式"""
    print("🔧 初始化資料庫...")
    print(f"📍 Database URL: {settings.database_url}")
    print("")
    
    try:
        create_database()
        create_extensions()
        
        # 建議使用 Alembic
        print("")
        print("📌 下一步：執行 Alembic 遷移")
        print("   alembic upgrade head")
        print("")
        
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

