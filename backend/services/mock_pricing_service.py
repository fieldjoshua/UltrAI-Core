"""
Mock pricing service for testing.

This module provides a mock implementation of the pricing service for testing and development.
"""

from typing import Dict, Any, Optional


class MockPricingService:
    """Mock pricing service that simulates authorization and charging"""

    def __init__(self):
        """Initialize the mock pricing service"""
        self.pricing_enabled = True
        self.pricing_tiers = {
            "free": {"analyze_limit": 10, "tokens_limit": 5000},
            "basic": {"analyze_limit": 100, "tokens_limit": 100000},
            "premium": {"analyze_limit": 1000, "tokens_limit": 1000000},
            "enterprise": {"analyze_limit": -1, "tokens_limit": -1}
        }
        self.mock_users = {
            "user_123": {"tier": "free", "balance": 10.0, "usage": {"requests": 5, "tokens": 2500}},
            "user_456": {"tier": "basic", "balance": 25.0, "usage": {"requests": 50, "tokens": 50000}},
            "user_789": {"tier": "premium", "balance": 100.0, "usage": {"requests": 500, "tokens": 500000}},
            "admin_123": {"tier": "enterprise", "balance": 1000.0, "usage": {"requests": 0, "tokens": 0}}
        }
        self.pricing_rates = {
            "analyze": 0.01,  # $0.01 per analyze request
            "token": 0.00002,  # $0.00002 per token
            "document": 0.02   # $0.02 per document operation
        }

    def authorize_request(
        self,
        user_id: str,
        request_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Authorize a request based on user balance and limits

        Args:
            user_id: User ID
            request_type: Type of request (analyze, document, etc.)
            details: Additional request details

        Returns:
            Authorization result
        """
        # Default authorization result
        result = {
            "authorized": True,
            "message": "Request authorized",
            "user_id": user_id,
            "request_type": request_type
        }

        # If pricing is disabled, always authorize
        if not self.pricing_enabled:
            return result

        # If user doesn't exist, deny
        if user_id not in self.mock_users:
            return {
                "authorized": False,
                "message": "User not found",
                "user_id": user_id,
                "request_type": request_type
            }

        user = self.mock_users[user_id]

        # Check for enterprise tier which has no limits
        if user["tier"] == "enterprise":
            return result

        # Check balance
        if user["balance"] <= 0:
            return {
                "authorized": False,
                "message": "Insufficient balance",
                "user_id": user_id,
                "request_type": request_type,
                "balance": user["balance"]
            }

        # Check request limits based on tier
        tier_info = self.pricing_tiers[user["tier"]]

        if request_type == "analyze":
            analyze_limit = tier_info["analyze_limit"]
            current_usage = user["usage"]["requests"]

            # Check if user has reached their limit
            if analyze_limit > 0 and current_usage >= analyze_limit:
                return {
                    "authorized": False,
                    "message": f"Monthly request limit reached ({analyze_limit})",
                    "user_id": user_id,
                    "request_type": request_type,
                    "limit": analyze_limit,
                    "usage": current_usage
                }

        # Check token limits for certain operations
        if details and details.get("estimated_tokens"):
            tokens_limit = tier_info["tokens_limit"]
            current_token_usage = user["usage"]["tokens"]
            estimated_tokens = details["estimated_tokens"]

            # Check if user has reached token limit
            if tokens_limit > 0 and current_token_usage + estimated_tokens > tokens_limit:
                return {
                    "authorized": False,
                    "message": f"Monthly token limit reached ({tokens_limit})",
                    "user_id": user_id,
                    "request_type": request_type,
                    "limit": tokens_limit,
                    "usage": current_token_usage,
                    "estimated": estimated_tokens
                }

        # If everything passes, authorize the request
        return result

    def record_usage(
        self,
        user_id: str,
        request_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record usage and charge the user for a request

        Args:
            user_id: User ID
            request_type: Type of request (analyze, document, etc.)
            details: Additional usage details

        Returns:
            Charge result
        """
        # Default charge result
        result = {
            "status": "success",
            "message": "Usage recorded",
            "user_id": user_id,
            "request_type": request_type,
            "amount_charged": 0.0
        }

        # If pricing is disabled, don't charge
        if not self.pricing_enabled:
            return result

        # If user doesn't exist, return error
        if user_id not in self.mock_users:
            return {
                "status": "error",
                "message": "User not found",
                "user_id": user_id
            }

        user = self.mock_users[user_id]

        # Calculate charge based on request type
        charge = 0.0

        if request_type == "analyze":
            charge = self.pricing_rates["analyze"]
            user["usage"]["requests"] += 1

        elif request_type == "document":
            charge = self.pricing_rates["document"]

        # Add token charges if specified
        if details and details.get("token_count"):
            token_count = details["token_count"]
            token_charge = token_count * self.pricing_rates["token"]
            charge += token_charge
            user["usage"]["tokens"] += token_count

        # Apply the charge to the user's balance
        if charge > 0 and user["tier"] != "enterprise":  # Enterprise tier is not charged
            user["balance"] -= charge

        # Update the result with charge information
        result["amount_charged"] = charge
        result["new_balance"] = user["balance"]

        return result

    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Get current pricing information

        Returns:
            Pricing information
        """
        return {
            "pricing_enabled": self.pricing_enabled,
            "tiers": self.pricing_tiers,
            "rates": self.pricing_rates
        }