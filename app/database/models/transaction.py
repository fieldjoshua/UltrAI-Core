"""
Transaction model for the Ultra backend.

This module provides the SQLAlchemy ORM model for financial transaction tracking.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import relationship

from app.database.models.base import Base


class TransactionType(str, enum.Enum):
    """Types of financial transactions"""
    
    CREDIT = "credit"  # Money added to account
    DEBIT = "debit"    # Money deducted from account
    REFUND = "refund"  # Money refunded
    ADJUSTMENT = "adjustment"  # Manual adjustment


class TransactionStatus(str, enum.Enum):
    """Status of financial transactions"""
    
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class Transaction(Base):
    """Financial transaction model for tracking user credits and debits"""
    
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transactions_user_created", "user_id", "created_at"),
        Index("idx_transactions_status", "status"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Store as decimal for accuracy
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    
    # Description and metadata
    description = Column(String(255), nullable=False)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Payment provider information
    provider = Column(String(50), nullable=True)  # stripe, paypal, manual, etc.
    provider_transaction_id = Column(String(255), nullable=True, unique=True)
    
    # Related entity (optional)
    related_entity_type = Column(String(50), nullable=True)  # analysis, document, etc.
    related_entity_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="transactions")
    
    def __repr__(self) -> str:
        return f"<Transaction {self.id} {self.type.value} ${self.amount} for user {self.user_id}>"
    
    @property
    def amount_float(self) -> float:
        """Get amount as float for convenience"""
        return float(self.amount) if self.amount else 0.0
    
    def complete(self) -> None:
        """Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.utcnow()


class UsageTracking(Base):
    """Track API usage for billing purposes"""
    
    __tablename__ = "usage_tracking"
    __table_args__ = (
        Index("idx_usage_user_timestamp", "user_id", "timestamp"),
        Index("idx_usage_model_timestamp", "model", "timestamp"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage details
    model = Column(String(100), nullable=False)  # gpt-4, claude-3, etc.
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    
    # Token counts
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # Cost calculation
    input_cost = Column(Numeric(10, 6), default=0, nullable=False)  # 6 decimal places for small costs
    output_cost = Column(Numeric(10, 6), default=0, nullable=False)
    total_cost = Column(Numeric(10, 6), default=0, nullable=False)
    
    # Context
    endpoint = Column(String(255), nullable=True)  # API endpoint that triggered usage
    request_id = Column(String(255), nullable=True, index=True)  # For tracking specific requests
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="usage_records")
    
    def __repr__(self) -> str:
        return f"<UsageTracking {self.model} {self.total_tokens} tokens ${self.total_cost}>"