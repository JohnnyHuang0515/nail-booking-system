"""
Row Level Security (RLS) 管理器
用於在應用層面設定和驗證資料隔離
"""
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.context import RequestContext

logger = logging.getLogger(__name__)


class RLSManager:
    """Row Level Security 管理器"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._merchant_id: Optional[UUID] = None
    
    def set_merchant_context(self, merchant_id: UUID) -> None:
        """
        設定當前會話的商家上下文
        
        Args:
            merchant_id: 商家ID
        """
        try:
            # 設定 PostgreSQL 會話變數
            self.db_session.execute(
                text("SET app.merchant_id = :merchant_id"),
                {"merchant_id": str(merchant_id)}
            )
            self.db_session.commit()
            self._merchant_id = merchant_id
            
            logger.info(f"RLS 上下文已設定為商家: {merchant_id}")
            
        except Exception as e:
            logger.error(f"設定 RLS 上下文失敗: {str(e)}")
            self.db_session.rollback()
            raise
    
    def clear_merchant_context(self) -> None:
        """清除當前會話的商家上下文"""
        try:
            self.db_session.execute(text("RESET app.merchant_id"))
            self.db_session.commit()
            self._merchant_id = None
            
            logger.info("RLS 上下文已清除")
            
        except Exception as e:
            logger.error(f"清除 RLS 上下文失敗: {str(e)}")
            self.db_session.rollback()
            raise
    
    def get_current_merchant_id(self) -> Optional[UUID]:
        """取得當前設定的商家ID"""
        return self._merchant_id
    
    def verify_merchant_access(self, resource_merchant_id: UUID) -> bool:
        """
        驗證當前上下文是否有權限存取指定商家的資源
        
        Args:
            resource_merchant_id: 資源所屬的商家ID
            
        Returns:
            bool: 是否有存取權限
        """
        if not self._merchant_id:
            logger.warning("未設定商家上下文")
            return False
        
        has_access = self._merchant_id == resource_merchant_id
        if not has_access:
            logger.warning(
                f"商家存取權限驗證失敗: 請求商家 {self._merchant_id} "
                f"嘗試存取商家 {resource_merchant_id} 的資源"
            )
        
        return has_access
    
    def validate_merchant_isolation(self, table_name: str, merchant_id: UUID) -> bool:
        """
        驗證資料隔離是否正確
        
        Args:
            table_name: 表名
            merchant_id: 預期的商家ID
            
        Returns:
            bool: 隔離是否正確
        """
        try:
            # 查詢指定表的所有記錄，檢查是否都屬於指定商家
            query = text(f"""
                SELECT COUNT(*) as total_count,
                       COUNT(CASE WHEN merchant_id = :merchant_id THEN 1 END) as matching_count
                FROM {table_name}
            """)
            
            result = self.db_session.execute(query, {"merchant_id": str(merchant_id)}).fetchone()
            
            if result:
                total_count = result.total_count
                matching_count = result.matching_count
                
                # 如果表中沒有記錄，或所有記錄都屬於指定商家，則隔離正確
                is_isolated = total_count == 0 or total_count == matching_count
                
                if not is_isolated:
                    logger.error(
                        f"資料隔離驗證失敗: 表 {table_name} 中有 "
                        f"{total_count - matching_count} 筆記錄不屬於商家 {merchant_id}"
                    )
                
                return is_isolated
            
            return True
            
        except Exception as e:
            logger.error(f"驗證資料隔離時發生錯誤: {str(e)}")
            return False


class RLSSessionManager:
    """RLS 會話管理器 - 用於自動管理 RLS 上下文"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.rls_manager = RLSManager(db_session)
        self._original_merchant_id: Optional[UUID] = None
    
    def __enter__(self):
        """進入上下文管理器"""
        # 從請求上下文取得商家ID
        merchant_id = RequestContext.get_merchant_id()
        
        if merchant_id:
            self.rls_manager.set_merchant_context(merchant_id)
            self._original_merchant_id = merchant_id
        
        return self.rls_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        # 清除 RLS 上下文
        self.rls_manager.clear_merchant_context()
        self._original_merchant_id = None
        
        # 如果有異常，回滾事務
        if exc_type is not None:
            self.db_session.rollback()
            logger.error(f"RLS 會話發生異常: {exc_type.__name__}: {exc_val}")


def get_rls_session(db_session: Session) -> RLSSessionManager:
    """
    取得 RLS 會話管理器
    
    Args:
        db_session: 資料庫會話
        
    Returns:
        RLSSessionManager: RLS 會話管理器
    """
    return RLSSessionManager(db_session)


def ensure_merchant_isolation(db_session: Session, merchant_id: UUID, table_name: str) -> bool:
    """
    確保資料隔離的裝飾器函數
    
    Args:
        db_session: 資料庫會話
        merchant_id: 商家ID
        table_name: 表名
        
    Returns:
        bool: 隔離是否正確
    """
    rls_manager = RLSManager(db_session)
    return rls_manager.validate_merchant_isolation(table_name, merchant_id)


# 使用範例和測試函數
class RLSExample:
    """RLS 使用範例"""
    
    @staticmethod
    def example_usage():
        """RLS 使用範例"""
        from app.infrastructure.database.session import get_db_session
        
        with get_db_session() as db_session:
            # 使用 RLS 會話管理器
            with get_rls_session(db_session) as rls_manager:
                # 現在所有的查詢都會自動套用 RLS 策略
                # 只能看到當前商家的資料
                
                # 查詢用戶（只會返回當前商家的用戶）
                users = db_session.execute(text("SELECT * FROM users")).fetchall()
                print(f"找到 {len(users)} 個用戶")
                
                # 查詢預約（只會返回當前商家的預約）
                appointments = db_session.execute(text("SELECT * FROM appointments")).fetchall()
                print(f"找到 {len(appointments)} 個預約")
    
    @staticmethod
    def test_merchant_isolation():
        """測試商家隔離"""
        from app.infrastructure.database.session import get_db_session
        from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
        
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            merchants = merchant_repo.list_active()
            
            if len(merchants) < 2:
                print("需要至少 2 個商家來測試隔離")
                return
            
            # 測試商家 1 的資料隔離
            merchant1 = merchants[0]
            rls_manager = RLSManager(db_session)
            rls_manager.set_merchant_context(merchant1.id)
            
            # 驗證只能看到商家 1 的資料
            users_count = db_session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            services_count = db_session.execute(text("SELECT COUNT(*) FROM services")).scalar()
            
            print(f"商家 {merchant1.name} 的資料:")
            print(f"  用戶數量: {users_count}")
            print(f"  服務數量: {services_count}")
            
            # 清除上下文
            rls_manager.clear_merchant_context()
            
            # 測試商家 2 的資料隔離
            merchant2 = merchants[1]
            rls_manager.set_merchant_context(merchant2.id)
            
            users_count = db_session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            services_count = db_session.execute(text("SELECT COUNT(*) FROM services")).scalar()
            
            print(f"商家 {merchant2.name} 的資料:")
            print(f"  用戶數量: {users_count}")
            print(f"  服務數量: {services_count}")
            
            # 清除上下文
            rls_manager.clear_merchant_context()


if __name__ == "__main__":
    # 運行測試
    RLSExample.test_merchant_isolation()
