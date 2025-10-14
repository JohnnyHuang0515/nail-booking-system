"""
Identity Context - Infrastructure Layer - Repository Implementation
使用 SQLAlchemy 實作 UserRepository
"""
from typing import Optional
from sqlalchemy.orm import Session

from identity.domain.models import User, Role, RoleType, Permission
from identity.domain.repositories import UserRepository
from identity.infrastructure.orm.models import UserORM


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy 實作的 User Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, user: User) -> None:
        """儲存用戶"""
        user_orm = self.db.query(UserORM).filter_by(id=user.id).first()
        
        if user_orm:
            # 更新現有記錄
            user_orm.email = user.email
            user_orm.line_user_id = user.line_user_id
            user_orm.name = user.name
            user_orm.password_hash = user.password_hash
            user_orm.merchant_id = user.merchant_id
            user_orm.role = user.role.name.value
            user_orm.is_active = user.is_active
            user_orm.is_verified = user.is_verified
            user_orm.last_login_at = user.last_login_at
            user_orm.updated_at = user.updated_at
        else:
            # 新建記錄
            user_orm = UserORM(
                id=user.id,
                email=user.email,
                line_user_id=user.line_user_id,
                name=user.name,
                password_hash=user.password_hash,
                merchant_id=user.merchant_id,
                role=user.role.name.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login_at=user.last_login_at
            )
            self.db.add(user_orm)
        
        self.db.flush()
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """依 ID 查詢用戶"""
        user_orm = self.db.query(UserORM).filter_by(id=user_id).first()
        
        if user_orm is None:
            return None
        
        return self._to_domain(user_orm)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """依 email 查詢用戶"""
        user_orm = self.db.query(UserORM).filter_by(email=email).first()
        
        if user_orm is None:
            return None
        
        return self._to_domain(user_orm)
    
    def find_by_line_user_id(self, line_user_id: str) -> Optional[User]:
        """依 LINE User ID 查詢用戶"""
        user_orm = self.db.query(UserORM).filter_by(line_user_id=line_user_id).first()
        
        if user_orm is None:
            return None
        
        return self._to_domain(user_orm)
    
    def exists_by_email(self, email: str) -> bool:
        """檢查 email 是否存在"""
        count = self.db.query(UserORM).filter_by(email=email).count()
        return count > 0
    
    def find_by_merchant(self, merchant_id: str) -> list[User]:
        """查詢商家的所有用戶"""
        users_orm = self.db.query(UserORM).filter_by(merchant_id=merchant_id).all()
        
        return [self._to_domain(u) for u in users_orm]
    
    def _to_domain(self, user_orm: UserORM) -> User:
        """將 ORM 模型轉換為 Domain 模型"""
        # 建立 Role
        role = Role(
            id=0,  # 簡化：不儲存 role ID
            name=RoleType(user_orm.role)
        )
        
        return User(
            id=user_orm.id,
            email=user_orm.email,
            line_user_id=user_orm.line_user_id,
            name=user_orm.name,
            password_hash=user_orm.password_hash,
            merchant_id=user_orm.merchant_id,
            role=role,
            is_active=user_orm.is_active,
            is_verified=user_orm.is_verified,
            last_login_at=user_orm.last_login_at,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at
        )

