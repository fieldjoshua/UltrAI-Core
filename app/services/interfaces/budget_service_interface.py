"""
Budget service interface for user budget management.

This interface defines the contract for implementing budget tracking
and enforcement in the Ultra AI system.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class BudgetPeriod(str, Enum):
    """Budget period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class BudgetStatus(BaseModel):
    """Current budget status for a user."""
    user_id: str
    period: BudgetPeriod
    limit: float
    used: float
    remaining: float
    percentage_used: float
    reset_date: datetime
    currency: str = "USD"
    is_exceeded: bool = False
    
    @property
    def is_near_limit(self) -> bool:
        """Check if budget is near limit (>80% used)."""
        return self.percentage_used >= 80.0


class BudgetAlert(BaseModel):
    """Budget alert configuration."""
    threshold_percentage: float  # e.g., 80.0 for 80%
    email_enabled: bool = True
    webhook_url: Optional[str] = None
    message_template: Optional[str] = None


class BudgetTransaction(BaseModel):
    """Record of a budget-affecting transaction."""
    transaction_id: str
    user_id: str
    amount: float
    description: str
    timestamp: datetime
    balance_after: float
    metadata: Optional[Dict] = None


class BudgetServiceInterface(ABC):
    """
    Abstract interface for budget service implementation.
    
    This service manages user budgets, tracks usage, and enforces limits
    to prevent unexpected costs.
    """
    
    @abstractmethod
    async def check_budget(
        self, 
        user_id: str, 
        estimated_cost: float
    ) -> bool:
        """
        Check if user has sufficient budget for an operation.
        
        Args:
            user_id: User identifier
            estimated_cost: Estimated cost of the operation
            
        Returns:
            True if user has sufficient budget, False otherwise
        """
        pass
    
    @abstractmethod
    async def deduct_from_budget(
        self, 
        user_id: str, 
        amount: float,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> BudgetTransaction:
        """
        Deduct amount from user's budget.
        
        This should be called after successful completion of an operation.
        
        Args:
            user_id: User identifier
            amount: Amount to deduct
            description: Description of the charge
            metadata: Additional metadata about the transaction
            
        Returns:
            Transaction record
            
        Raises:
            InsufficientBudgetError: If deduction would exceed budget
        """
        pass
    
    @abstractmethod
    async def refund_to_budget(
        self,
        user_id: str,
        amount: float,
        original_transaction_id: str,
        reason: str
    ) -> BudgetTransaction:
        """
        Refund amount to user's budget.
        
        Used when an operation fails after budget deduction.
        
        Args:
            user_id: User identifier
            amount: Amount to refund
            original_transaction_id: ID of the original deduction
            reason: Reason for refund
            
        Returns:
            Refund transaction record
        """
        pass
    
    @abstractmethod
    async def get_budget_status(
        self, 
        user_id: str
    ) -> BudgetStatus:
        """
        Get current budget status for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Current budget status
        """
        pass
    
    @abstractmethod
    async def set_budget_limit(
        self,
        user_id: str,
        limit: float,
        period: BudgetPeriod = BudgetPeriod.MONTHLY
    ) -> bool:
        """
        Set or update budget limit for a user.
        
        Args:
            user_id: User identifier
            limit: New budget limit
            period: Budget period type
            
        Returns:
            True if update successful
        """
        pass
    
    @abstractmethod
    async def get_budget_history(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[BudgetTransaction]:
        """
        Get budget transaction history.
        
        Args:
            user_id: User identifier
            start_date: Start of period (default: beginning of current period)
            end_date: End of period (default: now)
            limit: Maximum number of transactions to return
            
        Returns:
            List of budget transactions
        """
        pass
    
    @abstractmethod
    async def configure_alerts(
        self,
        user_id: str,
        alerts: List[BudgetAlert]
    ) -> bool:
        """
        Configure budget alerts for a user.
        
        Args:
            user_id: User identifier
            alerts: List of alert configurations
            
        Returns:
            True if configuration successful
        """
        pass
    
    @abstractmethod
    async def reset_budget(
        self,
        user_id: str,
        reason: str
    ) -> bool:
        """
        Reset user's budget (admin operation).
        
        Args:
            user_id: User identifier
            reason: Reason for reset
            
        Returns:
            True if reset successful
            
        Raises:
            UnauthorizedError: If caller lacks admin permissions
        """
        pass
    
    @abstractmethod
    async def get_usage_forecast(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> Dict[str, float]:
        """
        Forecast future usage based on historical patterns.
        
        Args:
            user_id: User identifier
            days_ahead: Number of days to forecast
            
        Returns:
            Dictionary mapping dates to forecasted usage
        """
        pass


class BudgetError(Exception):
    """Base exception for budget-related errors."""
    pass


class InsufficientBudgetError(BudgetError):
    """Raised when an operation would exceed budget limits."""
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient budget: required ${required:.2f}, "
            f"available ${available:.2f}"
        )