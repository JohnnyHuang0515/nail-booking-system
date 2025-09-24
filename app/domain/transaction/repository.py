import abc
from typing import List, Optional
import uuid

from app.domain.transaction.models import Transaction


class AbstractTransactionRepository(abc.ABC):
    """Abstract repository for Transaction operations."""
    
    @abc.abstractmethod
    def add(self, transaction: Transaction) -> Transaction:
        """Add a new transaction."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[Transaction]:
        """Get a transaction by ID."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_transactions(
        self, 
        user_id: Optional[uuid.UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions with optional filtering."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def update(self, transaction: Transaction) -> Transaction:
        """Update a transaction."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def delete(self, transaction_id: uuid.UUID) -> None:
        """Delete a transaction."""
        raise NotImplementedError
