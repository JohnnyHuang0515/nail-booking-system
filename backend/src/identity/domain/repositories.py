"""
Identity Context - Domain Layer - Repository Interfaces
定義 User Repository 抽象介面
"""
from abc import ABC, abstractmethod
from typing import Optional

from .models import User


class UserRepository(ABC):
    """User Repository 抽象基類"""
    
    @abstractmethod
    def save(self, user: User) -> None:
        """儲存用戶"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """依 ID 查詢用戶"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """依 email 查詢用戶"""
        pass
    
    @abstractmethod
    def find_by_line_user_id(self, line_user_id: str) -> Optional[User]:
        """依 LINE User ID 查詢用戶"""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """檢查 email 是否已存在"""
        pass
    
    @abstractmethod
    def find_by_merchant(self, merchant_id: str) -> list[User]:
        """查詢商家的所有用戶"""
        pass

