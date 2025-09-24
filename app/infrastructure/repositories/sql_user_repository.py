import uuid
from sqlalchemy.orm import Session

from app.domain.membership.models import User as DomainUser
from app.domain.membership.repository import AbstractUserRepository
from app.infrastructure.database.models import User as OrmUser


class SqlUserRepository(AbstractUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: DomainUser) -> None:
        orm_user = OrmUser(
            id=user.id,
            line_user_id=user.line_user_id,
            name=user.name,
            phone=user.phone
        )
        self.session.add(orm_user)

    def get_by_id(self, user_id: uuid.UUID) -> DomainUser | None:
        orm_user = self.session.query(OrmUser).filter(OrmUser.id == user_id).first()
        if orm_user:
            return DomainUser.model_validate(orm_user)
        return None

    def get_by_line_user_id(self, line_user_id: str) -> DomainUser | None:
        orm_user = self.session.query(OrmUser).filter(OrmUser.line_user_id == line_user_id).first()
        if orm_user:
            return DomainUser.model_validate(orm_user)
        return None
