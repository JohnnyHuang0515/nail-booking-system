from typing import List, Optional
import uuid
from decimal import Decimal
from datetime import datetime, date

from app.domain.transaction.repository import AbstractTransactionRepository
from app.domain.transaction.models import Transaction
from app.infrastructure.database.models import Transaction as OrmTransaction


class TransactionService:
    """Service layer for transaction operations."""
    
    def __init__(self, repository: AbstractTransactionRepository):
        self.repository = repository
    
    def get_transactions(
        self, 
        user_id: Optional[uuid.UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        merchant_id: Optional[uuid.UUID] = None
    ) -> List[Transaction]:
        """Get transactions with optional filtering."""
        return self.repository.get_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            merchant_id=merchant_id
        )
    
    def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return self.repository.get_by_id(transaction_id)
    
    def create_transaction(
        self,
        user_id: uuid.UUID,
        appointment_id: Optional[uuid.UUID] = None,
        amount: Decimal = None,
        notes: Optional[str] = None
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            user_id=user_id,
            appointment_id=appointment_id,
            amount=amount,
            notes=notes
        )
        
        return self.repository.add(transaction)
    
    def update_transaction(
        self,
        transaction_id: uuid.UUID,
        amount: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> Optional[Transaction]:
        """Update a transaction."""
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            return None
        
        if amount is not None:
            transaction.amount = amount
        if notes is not None:
            transaction.notes = notes
        
        return self.repository.update(transaction)
    
    def delete_transaction(self, transaction_id: uuid.UUID) -> bool:
        """Delete a transaction."""
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            return False
        
        self.repository.delete(transaction_id)
        return True
    
    def get_user_transaction_summary(self, user_id: uuid.UUID) -> dict:
        """Get transaction summary for a user."""
        transactions = self.repository.get_transactions(user_id=user_id)
        
        total_amount = sum(t.amount for t in transactions)
        transaction_count = len(transactions)
        
        return {
            "user_id": user_id,
            "total_amount": total_amount,
            "transaction_count": transaction_count,
            "transactions": transactions
        }
