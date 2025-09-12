"""
Billing service interface for payment processing and invoicing.

This interface defines the contract for implementing billing functionality
in the Ultra AI system, including payment processing, invoicing, and
subscription management.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    """Invoice status types."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(BaseModel):
    """Payment method information."""
    method_id: str
    user_id: str
    type: str  # "card", "bank", "paypal", etc.
    last_four: Optional[str] = None
    brand: Optional[str] = None  # "visa", "mastercard", etc.
    is_default: bool = False
    created_at: datetime
    metadata: Optional[Dict] = None


class Invoice(BaseModel):
    """Invoice information."""
    invoice_id: str
    user_id: str
    amount: float
    currency: str = "USD"
    status: InvoiceStatus
    due_date: datetime
    created_at: datetime
    paid_at: Optional[datetime] = None
    line_items: List[Dict[str, Any]]
    payment_method_id: Optional[str] = None
    metadata: Optional[Dict] = None


class Payment(BaseModel):
    """Payment transaction information."""
    payment_id: str
    invoice_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus
    payment_method_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    metadata: Optional[Dict] = None


class Subscription(BaseModel):
    """Subscription information."""
    subscription_id: str
    user_id: str
    plan_id: str
    status: str  # "active", "cancelled", "past_due", etc.
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    metadata: Optional[Dict] = None


class BillingServiceInterface(ABC):
    """
    Abstract interface for billing service implementation.
    
    This service handles payment processing, invoicing, and subscription
    management. Implementations should integrate with payment processors
    like Stripe, PayPal, or similar services.
    """
    
    @abstractmethod
    async def create_invoice(
        self,
        user_id: str,
        amount: float,
        line_items: List[Dict[str, Any]],
        due_date: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Invoice:
        """
        Create an invoice for a user.
        
        Args:
            user_id: User identifier
            amount: Total amount
            line_items: List of items on the invoice
            due_date: When payment is due (default: 30 days)
            metadata: Additional invoice metadata
            
        Returns:
            Created invoice
        """
        pass
    
    @abstractmethod
    async def send_invoice(
        self,
        invoice_id: str,
        email: Optional[str] = None
    ) -> bool:
        """
        Send invoice to user via email.
        
        Args:
            invoice_id: Invoice identifier
            email: Override email address (uses user's default if not provided)
            
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    async def process_payment(
        self,
        invoice_id: str,
        payment_method_id: str,
        amount: Optional[float] = None
    ) -> Payment:
        """
        Process payment for an invoice.
        
        Args:
            invoice_id: Invoice to pay
            payment_method_id: Payment method to use
            amount: Amount to pay (default: full invoice amount)
            
        Returns:
            Payment transaction record
            
        Raises:
            PaymentFailedError: If payment processing fails
        """
        pass
    
    @abstractmethod
    async def add_payment_method(
        self,
        user_id: str,
        payment_details: Dict[str, Any],
        set_as_default: bool = False
    ) -> PaymentMethod:
        """
        Add a payment method for a user.
        
        Args:
            user_id: User identifier
            payment_details: Payment method details (provider-specific)
            set_as_default: Whether to set as default method
            
        Returns:
            Added payment method
            
        Raises:
            InvalidPaymentMethodError: If payment method is invalid
        """
        pass
    
    @abstractmethod
    async def remove_payment_method(
        self,
        user_id: str,
        payment_method_id: str
    ) -> bool:
        """
        Remove a payment method.
        
        Args:
            user_id: User identifier
            payment_method_id: Payment method to remove
            
        Returns:
            True if removed successfully
        """
        pass
    
    @abstractmethod
    async def list_payment_methods(
        self,
        user_id: str
    ) -> List[PaymentMethod]:
        """
        List all payment methods for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of payment methods
        """
        pass
    
    @abstractmethod
    async def get_billing_history(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Get billing history for a user.
        
        Args:
            user_id: User identifier
            start_date: Start of period
            end_date: End of period
            limit: Maximum number of invoices to return
            
        Returns:
            List of invoices
        """
        pass
    
    @abstractmethod
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: str,
        trial_days: int = 0
    ) -> Subscription:
        """
        Create a subscription for a user.
        
        Args:
            user_id: User identifier
            plan_id: Subscription plan identifier
            payment_method_id: Payment method for recurring charges
            trial_days: Number of trial days before first charge
            
        Returns:
            Created subscription
        """
        pass
    
    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_immediately: bool = False
    ) -> Subscription:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Subscription to cancel
            cancel_immediately: If True, cancel now; else at period end
            
        Returns:
            Updated subscription
        """
        pass
    
    @abstractmethod
    async def update_subscription(
        self,
        subscription_id: str,
        plan_id: Optional[str] = None,
        payment_method_id: Optional[str] = None
    ) -> Subscription:
        """
        Update a subscription.
        
        Args:
            subscription_id: Subscription to update
            plan_id: New plan (if changing)
            payment_method_id: New payment method (if changing)
            
        Returns:
            Updated subscription
        """
        pass
    
    @abstractmethod
    async def process_refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Payment:
        """
        Process a refund for a payment.
        
        Args:
            payment_id: Payment to refund
            amount: Amount to refund (default: full amount)
            reason: Reason for refund
            
        Returns:
            Refund transaction record
        """
        pass
    
    @abstractmethod
    async def handle_webhook(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """
        Handle webhook events from payment processor.
        
        Args:
            event_type: Type of webhook event
            event_data: Event payload
            
        Returns:
            True if handled successfully
        """
        pass


class BillingError(Exception):
    """Base exception for billing-related errors."""
    pass


class PaymentFailedError(BillingError):
    """Raised when payment processing fails."""
    pass


class InvalidPaymentMethodError(BillingError):
    """Raised when payment method is invalid or expired."""
    pass