from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from pydantic import BaseModel

from app.infrastructure.database.session import get_db
from app.domain.membership.models import User as DomainUser
from app.infrastructure.repositories.sql_user_repository import SqlUserRepository
from app.infrastructure.database.models import User as OrmUser

router = APIRouter()


class LoginRequest(BaseModel):
    line_user_id: str
    name: str = None


class UserCreate(BaseModel):
    name: str
    phone: str = None
    line_user_id: str = None


class UserUpdate(BaseModel):
    name: str = None
    phone: str = None


@router.post("/users/login", response_model=DomainUser)
async def login_with_line(request: LoginRequest, db: Session = Depends(get_db)):
    """Login or register a user with LINE User ID."""
    try:
        # 先嘗試找到現有用戶
        orm_user = db.query(OrmUser).filter(OrmUser.line_user_id == request.line_user_id).first()
        
        if orm_user:
            # 用戶存在，更新名稱（如果提供）
            if request.name and request.name != orm_user.name:
                orm_user.name = request.name
                db.commit()
            
            return DomainUser(
                id=orm_user.id,
                line_user_id=orm_user.line_user_id,
                name=orm_user.name,
                phone=orm_user.phone
            )
        else:
            # 用戶不存在，創建新用戶
            new_user = DomainUser(
                line_user_id=request.line_user_id,
                name=request.name
            )
            
            orm_user = OrmUser(
                id=new_user.id,
                line_user_id=new_user.line_user_id,
                name=new_user.name,
                phone=new_user.phone
            )
            
            db.add(orm_user)
            db.commit()
            db.refresh(orm_user)
            
            return DomainUser(
                id=orm_user.id,
                line_user_id=orm_user.line_user_id,
                name=orm_user.name,
                phone=orm_user.phone
            )
            
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users", response_model=List[DomainUser])
async def list_users(db: Session = Depends(get_db)):
    """Get all users."""
    try:
        # 直接查詢資料庫獲取所有用戶
        orm_users = db.query(OrmUser).all()
        users = []
        for orm_user in orm_users:
            user = DomainUser(
                id=orm_user.id,
                line_user_id=orm_user.line_user_id,
                name=orm_user.name,
                phone=orm_user.phone
            )
            users.append(user)
        return users
    except Exception as e:
        print(f"Users error: {e}")
        return []


@router.get("/users/{user_id}", response_model=DomainUser)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a user by ID."""
    try:
        repository = SqlUserRepository(db)
        user = repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        print(f"User error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/users", response_model=DomainUser)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        # 檢查是否已存在相同的手機號碼
        if user_data.phone:
            existing_user = db.query(OrmUser).filter(OrmUser.phone == user_data.phone).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Phone number already exists")
        
        # 檢查是否已存在相同的 LINE User ID
        if user_data.line_user_id:
            existing_user = db.query(OrmUser).filter(OrmUser.line_user_id == user_data.line_user_id).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="LINE User ID already exists")
        
        new_user = DomainUser(
            name=user_data.name,
            phone=user_data.phone,
            line_user_id=user_data.line_user_id
        )
        
        orm_user = OrmUser(
            id=new_user.id,
            line_user_id=new_user.line_user_id,
            name=new_user.name,
            phone=new_user.phone
        )
        
        db.add(orm_user)
        db.commit()
        db.refresh(orm_user)
        
        return DomainUser(
            id=orm_user.id,
            line_user_id=orm_user.line_user_id,
            name=orm_user.name,
            phone=orm_user.phone
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"User creation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/users/{user_id}", response_model=DomainUser)
async def update_user(user_id: uuid.UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update a user."""
    try:
        orm_user = db.query(OrmUser).filter(OrmUser.id == user_id).first()
        if not orm_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 檢查手機號碼是否已被其他用戶使用
        if user_data.phone and user_data.phone != orm_user.phone:
            existing_user = db.query(OrmUser).filter(
                OrmUser.phone == user_data.phone,
                OrmUser.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Phone number already exists")
        
        # 更新用戶資料
        if user_data.name is not None:
            orm_user.name = user_data.name
        if user_data.phone is not None:
            orm_user.phone = user_data.phone
        
        db.commit()
        db.refresh(orm_user)
        
        return DomainUser(
            id=orm_user.id,
            line_user_id=orm_user.line_user_id,
            name=orm_user.name,
            phone=orm_user.phone
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"User update error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/users/{user_id}")
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a user."""
    try:
        orm_user = db.query(OrmUser).filter(OrmUser.id == user_id).first()
        if not orm_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(orm_user)
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"User deletion error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
