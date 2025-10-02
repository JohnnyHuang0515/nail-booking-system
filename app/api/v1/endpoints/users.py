from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from pydantic import BaseModel

from app.infrastructure.database.session import get_db_session, get_db
from app.domain.membership.models import User as DomainUser
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.database.models import User as OrmUser
from app.context import RequestContext
from app.liff_auth import liff_security_middleware
from app.api.v1.dependencies import get_current_merchant_from_token

router = APIRouter()


class LIFFLoginRequest(BaseModel):
    """LIFF 登入請求"""
    id_token: str
    access_token: Optional[str] = None


class UserCreate(BaseModel):
    """創建用戶請求"""
    name: str
    phone: str = None


class UserUpdate(BaseModel):
    """更新用戶請求"""
    name: str = None
    phone: str = None


class UserResponse(BaseModel):
    """用戶回應"""
    id: str
    line_user_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    merchant_id: str
    merchant_name: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/users/liff-login", response_model=UserResponse)
async def liff_login(
    request: LIFFLoginRequest,
    merchant_id: str,
    db_session = Depends(get_db_session)
):
    """LIFF 登入 - 使用 idToken 驗證身分"""
    try:
        merchant_uuid = uuid.UUID(merchant_id)
        
        # 驗證 LIFF token 和取得用戶資訊
        auth_result = await liff_security_middleware.verify_request(
            id_token=request.id_token,
            merchant_id=merchant_uuid,
            access_token=request.access_token
        )
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="LIFF 驗證失敗")
        
        # 取得商家資訊
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_uuid)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        # 取得用戶資訊
        user_repo = SQLUserRepository(db_session)
        user = user_repo.find_by_id(uuid.UUID(auth_result["user_id"]))
        
        if not user:
            raise HTTPException(status_code=404, detail="找不到用戶")
        
        return UserResponse(
            id=str(user.id),
            line_user_id=user.line_user_id,
            name=user.name,
            phone=user.phone,
            merchant_id=str(merchant_uuid),
            merchant_name=merchant.name,
            created_at=user.created_at.isoformat()
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的商家ID格式")
    except Exception as e:
        print(f"LIFF 登入錯誤: {e}")
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")


@router.post("/users/login", response_model=UserResponse)
async def legacy_login_with_line(
    line_user_id: str,
    name: Optional[str] = None,
    merchant_id: str = None,
    db_session = Depends(get_db_session)
):
    """傳統 LINE 登入（向後兼容）"""
    try:
        if not merchant_id:
            raise HTTPException(status_code=400, detail="缺少商家ID")
        
        merchant_uuid = uuid.UUID(merchant_id)
        
        # 取得或創建用戶
        user_repo = SQLUserRepository(db_session)
        user = user_repo.get_or_create_by_line_user_id(merchant_uuid, line_user_id)
        
        # 更新用戶名稱（如果提供）
        if name and name != user.name:
            user.name = name
            db_session.commit()
        
        # 取得商家資訊
        merchant_repo = SQLMerchantRepository(db_session)
        merchant = merchant_repo.find_by_id(merchant_uuid)
        
        if not merchant:
            raise HTTPException(status_code=404, detail="找不到指定的商家")
        
        return UserResponse(
            id=str(user.id),
            line_user_id=user.line_user_id,
            name=user.name,
            phone=user.phone,
            merchant_id=str(merchant_uuid),
            merchant_name=merchant.name,
            created_at=user.created_at.isoformat()
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的商家ID格式")
    except Exception as e:
        print(f"傳統登入錯誤: {e}")
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_merchant: dict = Depends(get_current_merchant_from_token()),
    db_session = Depends(get_db_session)
):
    """取得指定商家的所有用戶"""
    try:
        merchant_uuid = uuid.UUID(current_merchant["id"])
        
        # 取得該商家的所有用戶
        user_repo = SQLUserRepository(db_session)
        users = user_repo.list_by_merchant(merchant_uuid)
        
        return [
            UserResponse(
                id=str(user.id),
                line_user_id=user.line_user_id,
                name=user.name,
                phone=user.phone,
                merchant_id=str(merchant_uuid),
                merchant_name=current_merchant["name"],
                created_at=user.created_at.isoformat()
            )
            for user in users
        ]
        
    except Exception as e:
        print(f"取得用戶列表錯誤: {e}")
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")


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
