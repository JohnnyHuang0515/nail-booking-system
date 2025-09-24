from typing import List, Optional
import uuid
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.domain.transaction.repository import AbstractTransactionRepository
from app.domain.transaction.models import Transaction
from app.infrastructure.database.models import Transaction as OrmTransaction


class SqlTransactionRepository(AbstractTransactionRepository):
    """SQL implementation of Transaction repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add(self, transaction: Transaction) -> Transaction:
        """Add a new transaction."""
        orm_transaction = OrmTransaction(
            id=transaction.id or uuid.uuid4(),
            user_id=transaction.user_id,
            appointment_id=transaction.appointment_id,
            amount=transaction.amount,
            notes=transaction.notes
        )
        
        self.db.add(orm_transaction)
        self.db.commit()
        self.db.refresh(orm_transaction)
        
        return Transaction(
            id=orm_transaction.id,
            user_id=orm_transaction.user_id,
            appointment_id=orm_transaction.appointment_id,
            amount=orm_transaction.amount,
            notes=orm_transaction.notes,
            created_at=orm_transaction.created_at
        )
    
    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[Transaction]:
        """Get a transaction by ID."""
        orm_transaction = self.db.query(OrmTransaction)\
            .options(
                joinedload(OrmTransaction.user),
                joinedload(OrmTransaction.appointment)
            )\
            .filter(OrmTransaction.id == transaction_id)\
            .first()
        
        if not orm_transaction:
            return None
        
        transaction = Transaction(
            id=orm_transaction.id,
            user_id=orm_transaction.user_id,
            appointment_id=orm_transaction.appointment_id,
            amount=orm_transaction.amount,
            notes=orm_transaction.notes,
            created_at=orm_transaction.created_at
        )
        # 添加關聯資料
        transaction.user = orm_transaction.user
        transaction.appointment = orm_transaction.appointment
        
        return transaction
    
    def get_transactions(
        self, 
        user_id: Optional[uuid.UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions with optional filtering."""
        query = self.db.query(OrmTransaction)\
            .options(
                joinedload(OrmTransaction.user),
                joinedload(OrmTransaction.appointment)
            )
        
        # Apply filters
        filters = []
        
        if user_id:
            filters.append(OrmTransaction.user_id == user_id)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            filters.append(OrmTransaction.created_at >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            filters.append(OrmTransaction.created_at <= end_date_obj)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by created_at descending
        orm_transactions = query.order_by(OrmTransaction.created_at.desc()).all()
        
        transactions = []
        for orm_transaction in orm_transactions:
            transaction = Transaction(
                id=orm_transaction.id,
                user_id=orm_transaction.user_id,
                appointment_id=orm_transaction.appointment_id,
                amount=orm_transaction.amount,
                notes=orm_transaction.notes,
                created_at=orm_transaction.created_at
            )
            # 添加關聯資料到 transaction 物件
            transaction.user = orm_transaction.user
            transaction.appointment = orm_transaction.appointment
            transactions.append(transaction)
        
        return transactions
    
    def update(self, transaction: Transaction) -> Transaction:
        """Update a transaction."""
        orm_transaction = self.db.query(OrmTransaction)\
            .filter(OrmTransaction.id == transaction.id)\
            .first()
        
        if not orm_transaction:
            raise ValueError(f"Transaction with id {transaction.id} not found")
        
        orm_transaction.amount = transaction.amount
        orm_transaction.notes = transaction.notes
        
        self.db.commit()
        self.db.refresh(orm_transaction)
        
        return Transaction(
            id=orm_transaction.id,
            user_id=orm_transaction.user_id,
            appointment_id=orm_transaction.appointment_id,
            amount=orm_transaction.amount,
            notes=orm_transaction.notes,
            created_at=orm_transaction.created_at
        )
    
    def delete(self, transaction_id: uuid.UUID) -> None:
        """Delete a transaction."""
        orm_transaction = self.db.query(OrmTransaction)\
            .filter(OrmTransaction.id == transaction_id)\
            .first()
        
        if orm_transaction:
            self.db.delete(orm_transaction)
            self.db.commit()
