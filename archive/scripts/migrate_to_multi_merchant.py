"""
多商家架構資料庫遷移腳本
"""
from app.infrastructure.database.session import engine, Base
from app.infrastructure.database import models
from sqlalchemy import text
import uuid

def migrate_to_multi_merchant():
    """遷移到多商家架構"""
    print("開始遷移到多商家架構...")
    
    # 1. 創建新的資料表結構
    print("1. 創建新的資料表結構...")
    Base.metadata.create_all(bind=engine)
    
    # 2. 創建預設商家（如果沒有現有資料）
    print("2. 創建預設商家...")
    with engine.connect() as conn:
        # 檢查是否已有商家
        result = conn.execute(text("SELECT COUNT(*) FROM merchants"))
        merchant_count = result.scalar()
        
        if merchant_count == 0:
            # 創建預設商家
            default_merchant_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO merchants (id, name, line_channel_id, line_channel_secret, 
                                     line_channel_access_token, timezone, is_active, created_at)
                VALUES (:id, :name, :channel_id, :secret, :token, :timezone, :active, NOW())
            """), {
                'id': default_merchant_id,
                'name': '預設美甲店',
                'channel_id': 'default_channel_id',
                'secret': 'default_channel_secret',
                'token': 'default_access_token',
                'timezone': 'Asia/Taipei',
                'active': True
            })
            conn.commit()
            print(f"   創建預設商家 ID: {default_merchant_id}")
        else:
            print(f"   已有 {merchant_count} 個商家，跳過創建預設商家")
    
    # 3. 遷移現有資料（如果有的話）
    print("3. 遷移現有資料...")
    with engine.connect() as conn:
        try:
            # 檢查是否有舊的 users 表結構
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'merchant_id'
            """))
            
            if not result.fetchone():
                print("   舊資料結構需要遷移...")
                
                # 取得預設商家ID
                result = conn.execute(text("SELECT id FROM merchants LIMIT 1"))
                default_merchant_id = result.scalar()
                
                if default_merchant_id:
                    # 為現有用戶添加 merchant_id
                    conn.execute(text("""
                        UPDATE users 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    # 為現有服務添加 merchant_id
                    conn.execute(text("""
                        UPDATE services 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    # 為現有預約添加 merchant_id
                    conn.execute(text("""
                        UPDATE appointments 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    # 為現有交易添加 merchant_id
                    conn.execute(text("""
                        UPDATE transactions 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    # 為營業時間添加 merchant_id
                    conn.execute(text("""
                        UPDATE business_hours 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    # 為休假時間添加 merchant_id
                    conn.execute(text("""
                        UPDATE time_off 
                        SET merchant_id = :merchant_id 
                        WHERE merchant_id IS NULL
                    """), {'merchant_id': default_merchant_id})
                    
                    conn.commit()
                    print("   現有資料遷移完成")
                else:
                    print("   找不到預設商家，無法遷移現有資料")
            else:
                print("   資料結構已是最新，無需遷移")
                
        except Exception as e:
            print(f"   遷移現有資料時發生錯誤: {str(e)}")
            conn.rollback()
    
    print("多商家架構遷移完成！")
    print("\n注意事項：")
    print("1. 請更新 LINE Channel 設定，使用正確的 Channel ID 和憑證")
    print("2. 請為每個商家設定正確的 LINE Webhook URL")
    print("3. 請測試多商家功能是否正常運作")


def create_sample_merchants():
    """創建範例商家資料"""
    print("創建範例商家資料...")
    
    with engine.connect() as conn:
        # 創建範例商家 1
        merchant1_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO merchants (id, name, line_channel_id, line_channel_secret, 
                                 line_channel_access_token, timezone, is_active, created_at)
            VALUES (:id, :name, :channel_id, :secret, :token, :timezone, :active, NOW())
        """), {
            'id': merchant1_id,
            'name': '台北美甲店',
            'channel_id': 'taipei_channel_id',
            'secret': 'taipei_channel_secret',
            'token': 'taipei_access_token',
            'timezone': 'Asia/Taipei',
            'active': True
        })
        
        # 創建範例商家 2
        merchant2_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO merchants (id, name, line_channel_id, line_channel_secret, 
                                 line_channel_access_token, timezone, is_active, created_at)
            VALUES (:id, :name, :channel_id, :secret, :token, :timezone, :active, NOW())
        """), {
            'id': merchant2_id,
            'name': '高雄美甲店',
            'channel_id': 'kaohsiung_channel_id',
            'secret': 'kaohsiung_channel_secret',
            'token': 'kaohsiung_access_token',
            'timezone': 'Asia/Taipei',
            'active': True
        })
        
        conn.commit()
        print(f"創建範例商家：")
        print(f"  - 台北美甲店 (ID: {merchant1_id})")
        print(f"  - 高雄美甲店 (ID: {merchant2_id})")


if __name__ == "__main__":
    migrate_to_multi_merchant()
    
    # 詢問是否創建範例資料
    create_samples = input("\n是否創建範例商家資料？(y/N): ").lower().strip()
    if create_samples == 'y':
        create_sample_merchants()
