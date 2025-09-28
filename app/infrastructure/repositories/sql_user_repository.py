import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.membership.models import User as DomainUser
from app.domain.membership.repository import AbstractUserRepository
from app.infrastructure.database.models import User as OrmUser


class SqlUserRepository(AbstractUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: DomainUser) -> None:
        orm_user = OrmUser(
            id=user.id,
            merchant_id=user.merchant_id,
            line_user_id=user.line_user_id,
            name=user.name,
            phone=user.phone
        )
        self.session.add(orm_user)

    def get_by_id(self, user_id: uuid.UUID) -> DomainUser | None:
        stmt = select(OrmUser).where(OrmUser.id == user_id)
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        if orm_user:
            return DomainUser.model_validate(orm_user)
        return None

    def get_by_line_user_id(self, line_user_id: str) -> DomainUser | None:
        stmt = select(OrmUser).where(OrmUser.line_user_id == line_user_id)
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        if orm_user:
            return DomainUser.model_validate(orm_user)
        return None

    def get_by_merchant_and_line_user_id(self, merchant_id: uuid.UUID, line_user_id: str) -> DomainUser | None:
        """根據商家ID和LINE用戶ID查找用戶"""
        stmt = select(OrmUser).where(
            OrmUser.merchant_id == merchant_id,
            OrmUser.line_user_id == line_user_id
        )
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        if orm_user:
            return DomainUser.model_validate(orm_user)
        return None

    def get_or_create_by_line_user_id(self, merchant_id: uuid.UUID, line_user_id: str) -> OrmUser:
        """根據商家ID和LINE用戶ID取得或創建用戶"""
        stmt = select(OrmUser).where(
            OrmUser.merchant_id == merchant_id,
            OrmUser.line_user_id == line_user_id
        )
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        
        if not orm_user:
            orm_user = OrmUser(
                merchant_id=merchant_id,
                line_user_id=line_user_id
            )
            self.session.add(orm_user)
            self.session.flush()
        
        return orm_user

    def list_by_merchant(self, merchant_id: uuid.UUID) -> List[DomainUser]:
        """列出指定商家的所有用戶"""
        stmt = select(OrmUser).where(OrmUser.merchant_id == merchant_id)
        orm_users = self.session.execute(stmt).scalars().all()
        return [DomainUser.model_validate(u) for u in orm_users]


# 向後兼容的別名
SQLUserRepository = SqlUserRepository
