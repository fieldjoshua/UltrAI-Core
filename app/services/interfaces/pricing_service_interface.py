"""
Pricing service interface for token usage cost calculation.

This interface defines the contract for implementing pricing functionality
in the Ultra AI system. Implementations should handle model-specific pricing,
token cost calculations, and cost estimations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel


class TokenUsage(BaseModel):
    """Token usage details for a request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime = None


class PricingInfo(BaseModel):
    """Pricing information for a model."""
    model: str
    provider: str
    prompt_token_price: float  # Price per 1K tokens
    completion_token_price: float  # Price per 1K tokens
    effective_date: datetime
    currency: str = "USD"


class CostCalculation(BaseModel):
    """Detailed cost breakdown."""
    token_usage: TokenUsage
    prompt_cost: float
    completion_cost: float
    total_cost: float
    currency: str = "USD"
    pricing_info: Optional[PricingInfo] = None


class PricingServiceInterface(ABC):
    """
    Abstract interface for pricing service implementation.
    
    This service is responsible for calculating costs based on token usage
    and model pricing. Implementations should handle price updates, caching,
    and integration with billing systems.
    """
    
    @abstractmethod
    async def calculate_cost(
        self, 
        token_usage: TokenUsage
    ) -> CostCalculation:
        """
        Calculate the cost for given token usage.
        
        Args:
            token_usage: Token usage details including model and counts
            
        Returns:
            CostCalculation with detailed breakdown
            
        Raises:
            PricingNotFoundError: If pricing for model is not available
        """
        pass
    
    @abstractmethod
    async def calculate_cost_batch(
        self, 
        token_usages: List[TokenUsage]
    ) -> List[CostCalculation]:
        """
        Calculate costs for multiple token usages efficiently.
        
        Args:
            token_usages: List of token usage details
            
        Returns:
            List of cost calculations in same order as input
        """
        pass
    
    @abstractmethod
    async def get_model_pricing(
        self, 
        model: str,
        effective_date: Optional[datetime] = None
    ) -> PricingInfo:
        """
        Get pricing information for a specific model.
        
        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-opus")
            effective_date: Get pricing as of this date (default: current)
            
        Returns:
            Current pricing information for the model
            
        Raises:
            ModelNotFoundError: If model is not recognized
        """
        pass
    
    @abstractmethod
    async def list_model_pricing(
        self,
        provider: Optional[str] = None
    ) -> List[PricingInfo]:
        """
        List pricing for all available models.
        
        Args:
            provider: Filter by provider (e.g., "openai", "anthropic")
            
        Returns:
            List of pricing information for all models
        """
        pass
    
    @abstractmethod
    async def estimate_cost(
        self, 
        prompt: str, 
        model: str,
        max_tokens: Optional[int] = None
    ) -> CostCalculation:
        """
        Estimate cost before running a prompt.
        
        This method should estimate token counts and calculate expected costs.
        Useful for showing users costs before execution.
        
        Args:
            prompt: The prompt text
            model: Target model
            max_tokens: Maximum completion tokens (if known)
            
        Returns:
            Estimated cost calculation
        """
        pass
    
    @abstractmethod
    async def update_pricing(
        self,
        pricing_info: PricingInfo
    ) -> bool:
        """
        Update pricing for a model.
        
        This method allows administrators to update model pricing.
        Should handle versioning and historical pricing.
        
        Args:
            pricing_info: New pricing information
            
        Returns:
            True if update successful
            
        Raises:
            UnauthorizedError: If caller lacks permission
        """
        pass
    
    @abstractmethod
    async def get_usage_cost_summary(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> Dict[str, float]:
        """
        Get cost summary for a user over a time period.
        
        Args:
            user_id: User identifier
            start_date: Start of period
            end_date: End of period
            group_by: Grouping period ("hour", "day", "week", "month")
            
        Returns:
            Dictionary mapping period to total cost
        """
        pass
    
    @abstractmethod
    async def export_usage_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        format: str = "csv"
    ) -> bytes:
        """
        Export detailed usage report.
        
        Args:
            user_id: User identifier
            start_date: Start of period
            end_date: End of period
            format: Export format ("csv", "json", "xlsx")
            
        Returns:
            Report data in requested format
        """
        pass


class PricingError(Exception):
    """Base exception for pricing-related errors."""
    pass


class PricingNotFoundError(PricingError):
    """Raised when pricing information is not available for a model."""
    pass


class ModelNotFoundError(PricingError):
    """Raised when a model identifier is not recognized."""
    pass