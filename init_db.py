#!/usr/bin/env python3
"""
資料庫初始化腳本
創建所有必要的資料表
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import get_database_url

def init_database():
    """初始化資料庫，創建所有表"""
    try:
        # 獲取資料庫 URL
        database_url = get_database_url()
        print(f"連接資料庫: {database_url}")
        
        # 創建引擎
        engine = create_engine(database_url)
        
        # 測試連接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("資料庫連接成功")
        
        # 創建所有表
        print("創建資料表...")
        Base.metadata.create_all(bind=engine)
        print("資料表創建完成")
        
        # 創建預設商家（用於測試）
        with engine.connect() as conn:
            # 檢查是否已有商家
            result = conn.execute(text("SELECT COUNT(*) FROM merchants"))
            count = result.scalar()
            
            if count == 0:
                print("創建預設商家...")
                conn.execute(text("""
                    INSERT INTO merchants (id, name, line_channel_id, line_channel_secret, line_channel_access_token, timezone, is_active)
                    VALUES (
                        '00000000-0000-0000-0000-000000000001',
                        '預設美甲店',
                        'test_channel_id',
                        'test_channel_secret',
                        'test_access_token',
                        'Asia/Taipei',
                        true
                    )
                """))
                conn.commit()
                print("預設商家創建完成")
            else:
                print(f"已有 {count} 個商家，跳過創建預設商家")
        
        print("資料庫初始化完成！")
        return True
        
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
        return False

if __name__ == "__main__":
    # 設置環境變數
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost/nail_booking_db"
    
    if not os.getenv("REDIS_URL"):
        os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    
    success = init_database()
    sys.exit(0 if success else 1)
