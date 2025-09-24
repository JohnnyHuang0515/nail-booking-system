from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from pydantic import BaseModel
from decimal import Decimal

from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import Transaction as OrmTransaction, User as OrmUser, Appointment as OrmAppointment
from app.infrastructure.repositories.sql_transaction_repository import SqlTransactionRepository
from app.application.transaction_service import TransactionService

router = APIRouter()


class TransactionCreate(BaseModel):
    user_id: uuid.UUID
    appointment_id: Optional[uuid.UUID] = None
    amount: Decimal
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    appointment_id: Optional[uuid.UUID]
    amount: Decimal
    notes: Optional[str]
    created_at: str
    user_name: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    service_name: Optional[str] = None

    class Config:
        from_attributes = True


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """Dependency to get transaction service."""
    repository = SqlTransactionRepository(db)
    return TransactionService(repository)


@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Get all transactions with optional filtering."""
    try:
        transactions = transaction_service.get_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        result = []
        for transaction in transactions:
            # 獲取相關的用戶和預約資訊
            user_name = None
            appointment_date = None
            appointment_time = None
            service_name = None
            
            if transaction.user:
                user_name = transaction.user.name
            
            if transaction.appointment:
                appointment_date = transaction.appointment.appointment_date.isoformat() if transaction.appointment.appointment_date else None
                appointment_time = transaction.appointment.appointment_time.isoformat() if transaction.appointment.appointment_time else None
                if transaction.appointment.service:
                    service_name = transaction.appointment.service.name
            
            result.append(TransactionResponse(
                id=transaction.id,
                user_id=transaction.user_id,
                appointment_id=transaction.appointment_id,
                amount=transaction.amount,
                notes=transaction.notes,
                created_at=transaction.created_at.isoformat(),
                user_name=user_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                service_name=service_name
            ))
        
        return result
    except Exception as e:
        print(f"List transactions error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Get a specific transaction by ID."""
    try:
        transaction = transaction_service.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # 獲取相關資訊
        user_name = transaction.user.name if transaction.user else None
        appointment_date = None
        appointment_time = None
        service_name = None
        
        if transaction.appointment:
            appointment_date = transaction.appointment.appointment_date.isoformat() if transaction.appointment.appointment_date else None
            appointment_time = transaction.appointment.appointment_time.isoformat() if transaction.appointment.appointment_time else None
            if transaction.appointment.service:
                service_name = transaction.appointment.service.name
        
        return TransactionResponse(
            id=transaction.id,
            user_id=transaction.user_id,
            appointment_id=transaction.appointment_id,
            amount=transaction.amount,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            user_name=user_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service_name=service_name
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get transaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Create a new transaction."""
    try:
        transaction = transaction_service.create_transaction(
            user_id=transaction_data.user_id,
            appointment_id=transaction_data.appointment_id,
            amount=transaction_data.amount,
            notes=transaction_data.notes
        )
        
        # 獲取相關資訊
        user_name = transaction.user.name if transaction.user else None
        appointment_date = None
        appointment_time = None
        service_name = None
        
        if transaction.appointment:
            appointment_date = transaction.appointment.appointment_date.isoformat() if transaction.appointment.appointment_date else None
            appointment_time = transaction.appointment.appointment_time.isoformat() if transaction.appointment.appointment_time else None
            if transaction.appointment.service:
                service_name = transaction.appointment.service.name
        
        return TransactionResponse(
            id=transaction.id,
            user_id=transaction.user_id,
            appointment_id=transaction.appointment_id,
            amount=transaction.amount,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            user_name=user_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service_name=service_name
        )
    except Exception as e:
        print(f"Create transaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_data: TransactionUpdate,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Update a transaction."""
    try:
        transaction = transaction_service.update_transaction(
            transaction_id=transaction_id,
            amount=transaction_data.amount,
            notes=transaction_data.notes
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # 獲取相關資訊
        user_name = transaction.user.name if transaction.user else None
        appointment_date = None
        appointment_time = None
        service_name = None
        
        if transaction.appointment:
            appointment_date = transaction.appointment.appointment_date.isoformat() if transaction.appointment.appointment_date else None
            appointment_time = transaction.appointment.appointment_time.isoformat() if transaction.appointment.appointment_time else None
            if transaction.appointment.service:
                service_name = transaction.appointment.service.name
        
        return TransactionResponse(
            id=transaction.id,
            user_id=transaction.user_id,
            appointment_id=transaction.appointment_id,
            amount=transaction.amount,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            user_name=user_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service_name=service_name
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update transaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: uuid.UUID,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Delete a transaction."""
    try:
        success = transaction_service.delete_transaction(transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete transaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    user_id: uuid.UUID,
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Get all transactions for a specific user."""
    try:
        transactions = transaction_service.get_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        result = []
        for transaction in transactions:
            # 獲取相關資訊
            user_name = transaction.user.name if transaction.user else None
            appointment_date = None
            appointment_time = None
            service_name = None
            
            if transaction.appointment:
                appointment_date = transaction.appointment.appointment_date.isoformat() if transaction.appointment.appointment_date else None
                appointment_time = transaction.appointment.appointment_time.isoformat() if transaction.appointment.appointment_time else None
                if transaction.appointment.service:
                    service_name = transaction.appointment.service.name
            
            result.append(TransactionResponse(
                id=transaction.id,
                user_id=transaction.user_id,
                appointment_id=transaction.appointment_id,
                amount=transaction.amount,
                notes=transaction.notes,
                created_at=transaction.created_at.isoformat(),
                user_name=user_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                service_name=service_name
            ))
        
        return result
    except Exception as e:
        print(f"Get user transactions error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
