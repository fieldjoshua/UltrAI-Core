"""
Pricing integration for the Ultra backend.

This module provides integration with external pricing services and APIs.
For the sake of simplicity, this is just a wrapper around our mock pricing service.
"""

from typing import Dict, Any, Optional

# Import the mock service for development
from backend.services.mock_pricing_service import MockPricingService


class PricingIntegration:
    """Integration with pricing services"""

    def __init__(self):
        """Initialize the pricing integration"""
        # Use mock service for now
        self.service = MockPricingService()
        self.pricing_enabled = True

    def authorize_request(
        self,
        user_id: str,
        request_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Authorize a request based on user's tier and balance

        Args:
            user_id: User ID
            request_type: Type of request
            details: Request details

        Returns:
            Authorization result
        """
        if not self.pricing_enabled:
            return {
                "authorized": True,
                "message": "Pricing is disabled",
                "user_id": user_id,
                "request_type": request_type
            }

        # Call the service
        return self.service.authorize_request(user_id, request_type, details)

    def record_usage(
        self,
        user_id: str,
        request_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record usage and charge the user

        Args:
            user_id: User ID
            request_type: Type of request
            details: Usage details

        Returns:
            Charge result
        """
        if not self.pricing_enabled:
            return {
                "status": "success",
                "message": "Pricing is disabled",
                "user_id": user_id,
                "request_type": request_type,
                "amount_charged": 0.0
            }

        # Call the service
        return self.service.record_usage(user_id, request_type, details)

    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Get pricing information

        Returns:
            Pricing information
        """
        return self.service.get_pricing_info()