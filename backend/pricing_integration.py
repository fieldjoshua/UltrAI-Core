#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pricing_simulator import PricingSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pricing_integration")


class PricingIntegration:
    def __init__(
        self,
        pricing_simulator: Optional[PricingSimulator] = None,
        pricing_enabled: bool = False,
        default_tier: str = "basic",
        usage_log_file: str = "token_usage_log.jsonl",
    ):
        """
        Initialize the pricing integration module

        Args:
            pricing_simulator: Instance of PricingSimulator or None to create a new one
            pricing_enabled: Whether to enable pricing calculations
            default_tier: Default pricing tier for users without explicit tier
            usage_log_file: File to log token usage
        """
        self.pricing_simulator = pricing_simulator or PricingSimulator()
        self.pricing_enabled = pricing_enabled
        self.default_tier = default_tier
        self.usage_log_file = usage_log_file

        # User account balances - in a real system, this would be in a database
        self.user_accounts = {}

        # Track current session token usage
        self.session_token_usage = {}

        # Create directory for the log file if it doesn't exist
        log_dir = os.path.dirname(usage_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def load_user_accounts(self, accounts_file: str = "user_accounts.json") -> None:
        """Load user account information from a file"""
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, "r") as f:
                    self.user_accounts = json.load(f)
                logger.info(f"Loaded {len(self.user_accounts)} user accounts")
            except Exception as e:
                logger.error(f"Error loading user accounts: {e}")

    def save_user_accounts(self, accounts_file: str = "user_accounts.json") -> None:
        """Save user account information to a file"""
        try:
            with open(accounts_file, "w") as f:
                json.dump(self.user_accounts, f, indent=2)
            logger.info(f"Saved {len(self.user_accounts)} user accounts")
        except Exception as e:
            logger.error(f"Error saving user accounts: {e}")

    def track_token_usage(
        self,
        user_id: str,
        model: str,
        token_count: int,
        request_type: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track token usage for a user and calculate costs

        Args:
            user_id: User identifier
            model: Model used for generation
            token_count: Number of tokens used
            request_type: Type of request (e.g., "prompt", "completion", "document_processing")
            session_id: Optional session identifier

        Returns:
            dict: Usage information including cost
        """
        # Default to anonymous user if not provided
        if not user_id:
            user_id = "anonymous"

        # Get user's pricing tier or use default
        tier = self.get_user_tier(user_id)

        # Calculate features based on request type
        features = []
        if request_type == "document_processing":
            features.append("document_processing")
        elif request_type == "priority":
            features.append("priority_processing")

        # Calculate cost using the pricing simulator
        cost_info = self.pricing_simulator.calculate_token_cost(
            model=model, token_count=token_count, tier=tier, features=features
        )

        # Create usage record
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "model": model,
            "token_count": token_count,
            "request_type": request_type,
            "session_id": session_id,
            "tier": tier,
            "cost": cost_info["total_cost"],
            "cost_details": cost_info,
        }

        # Log the usage
        self._log_usage(usage_record)

        # Update session token usage
        if session_id:
            if session_id not in self.session_token_usage:
                self.session_token_usage[session_id] = {
                    "start_time": datetime.now().isoformat(),
                    "user_id": user_id,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "models": {},
                }

            # Update session statistics
            session_data = self.session_token_usage[session_id]
            session_data["total_tokens"] += token_count
            session_data["total_cost"] += cost_info["total_cost"]

            if model not in session_data["models"]:
                session_data["models"][model] = {"tokens": 0, "cost": 0}

            session_data["models"][model]["tokens"] += token_count
            session_data["models"][model]["cost"] += cost_info["total_cost"]

        # Update user account if pricing is enabled
        if self.pricing_enabled:
            self._update_user_account(user_id, cost_info["total_cost"])

        return usage_record

    def get_user_tier(self, user_id: str) -> str:
        """Get the pricing tier for a user"""
        if user_id in self.user_accounts:
            return self.user_accounts[user_id].get("tier", self.default_tier)
        return self.default_tier

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get token usage summary for a session"""
        if session_id in self.session_token_usage:
            session_data = self.session_token_usage[session_id]
            session_data["duration"] = self._calculate_duration(
                session_data["start_time"]
            )
            return session_data

        return {"error": "Session not found", "session_id": session_id}

    def get_user_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """Get usage summary for a user"""
        if not os.path.exists(self.usage_log_file):
            return {"error": "No usage data available"}

        try:
            # Read usage log and filter by user_id
            user_usage = []
            with open(self.usage_log_file, "r") as f:
                for line in f:
                    record = json.loads(line.strip())
                    if record["user_id"] == user_id:
                        user_usage.append(record)

            if not user_usage:
                return {"error": f"No usage data found for user {user_id}"}

            # Calculate summary statistics
            total_tokens = sum(record["token_count"] for record in user_usage)
            total_cost = sum(record["cost"] for record in user_usage)

            # Group by model
            model_usage = {}
            for record in user_usage:
                model = record["model"]
                if model not in model_usage:
                    model_usage[model] = {"tokens": 0, "cost": 0, "count": 0}

                model_usage[model]["tokens"] += record["token_count"]
                model_usage[model]["cost"] += record["cost"]
                model_usage[model]["count"] += 1

            # Group by request type
            request_types = {}
            for record in user_usage:
                request_type = record["request_type"]
                if request_type not in request_types:
                    request_types[request_type] = {"count": 0, "tokens": 0, "cost": 0}

                request_types[request_type]["count"] += 1
                request_types[request_type]["tokens"] += record["token_count"]
                request_types[request_type]["cost"] += record["cost"]

            return {
                "user_id": user_id,
                "total_requests": len(user_usage),
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "first_request": user_usage[0]["timestamp"],
                "last_request": user_usage[-1]["timestamp"],
                "tier": self.get_user_tier(user_id),
                "model_usage": model_usage,
                "request_types": request_types,
                "account_balance": self._get_account_balance(user_id),
            }

        except Exception as e:
            logger.error(f"Error generating user usage summary: {e}")
            return {"error": f"Error generating usage summary: {str(e)}"}

    def create_user_account(
        self, user_id: str, tier: str = "basic", initial_balance: float = 0.0
    ) -> Dict[str, Any]:
        """Create a user account with initial balance"""
        if user_id in self.user_accounts:
            return {"error": f"User {user_id} already exists"}

        # Validate tier
        if tier not in self.pricing_simulator.default_pricing["tiers"]:
            tier = self.default_tier

        # Create account
        self.user_accounts[user_id] = {
            "user_id": user_id,
            "tier": tier,
            "balance": initial_balance,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "transactions": (
                [
                    {
                        "type": "deposit",
                        "amount": initial_balance,
                        "timestamp": datetime.now().isoformat(),
                        "description": "Initial deposit",
                    }
                ]
                if initial_balance > 0
                else []
            ),
        }

        # Save user accounts
        self.save_user_accounts()

        return {
            "status": "success",
            "user_id": user_id,
            "tier": tier,
            "balance": initial_balance,
        }

    def add_funds(
        self, user_id: str, amount: float, description: str = "Deposit"
    ) -> Dict[str, Any]:
        """Add funds to a user account"""
        if user_id not in self.user_accounts:
            return {"error": f"User {user_id} not found"}

        if amount <= 0:
            return {"error": "Amount must be positive"}

        # Add funds
        self.user_accounts[user_id]["balance"] += amount
        self.user_accounts[user_id]["updated_at"] = datetime.now().isoformat()

        # Record transaction
        if "transactions" not in self.user_accounts[user_id]:
            self.user_accounts[user_id]["transactions"] = []

        self.user_accounts[user_id]["transactions"].append(
            {
                "type": "deposit",
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "description": description,
            }
        )

        # Save user accounts
        self.save_user_accounts()

        return {
            "status": "success",
            "user_id": user_id,
            "amount_added": amount,
            "new_balance": self.user_accounts[user_id]["balance"],
        }

    def update_user_tier(self, user_id: str, tier: str) -> Dict[str, Any]:
        """Update a user's pricing tier"""
        if user_id not in self.user_accounts:
            return {"error": f"User {user_id} not found"}

        # Validate tier
        if tier not in self.pricing_simulator.default_pricing["tiers"]:
            return {"error": f"Invalid tier: {tier}"}

        # Update tier
        self.user_accounts[user_id]["tier"] = tier
        self.user_accounts[user_id]["updated_at"] = datetime.now().isoformat()

        # Save user accounts
        self.save_user_accounts()

        return {"status": "success", "user_id": user_id, "tier": tier}

    def check_balance(self, user_id: str) -> Dict[str, Any]:
        """Check a user's account balance"""
        if user_id not in self.user_accounts:
            return {"error": f"User {user_id} not found"}

        return {
            "user_id": user_id,
            "balance": self.user_accounts[user_id]["balance"],
            "tier": self.user_accounts[user_id]["tier"],
            "created_at": self.user_accounts[user_id]["created_at"],
            "updated_at": self.user_accounts[user_id]["updated_at"],
        }

    def estimate_request_cost(
        self,
        user_id: str,
        model: str,
        estimated_tokens: int,
        request_type: str = "completion",
    ) -> Dict[str, Any]:
        """
        Estimate the cost of a request before executing it

        Args:
            user_id: User identifier
            model: Model to be used
            estimated_tokens: Estimated token count
            request_type: Type of request

        Returns:
            dict: Cost estimate
        """
        # Get user's pricing tier
        tier = self.get_user_tier(user_id)

        # Calculate features based on request type
        features = []
        if request_type == "document_processing":
            features.append("document_processing")
        elif request_type == "priority":
            features.append("priority_processing")

        # Calculate cost using the pricing simulator
        cost_info = self.pricing_simulator.calculate_token_cost(
            model=model, token_count=estimated_tokens, tier=tier, features=features
        )

        # Check if user has sufficient balance
        has_sufficient_balance = True
        if self.pricing_enabled and user_id in self.user_accounts:
            has_sufficient_balance = (
                self.user_accounts[user_id]["balance"] >= cost_info["total_cost"]
            )

        return {
            "user_id": user_id,
            "model": model,
            "estimated_tokens": estimated_tokens,
            "request_type": request_type,
            "tier": tier,
            "estimated_cost": cost_info["total_cost"],
            "has_sufficient_balance": has_sufficient_balance,
            "cost_details": cost_info,
        }

    def _update_user_account(self, user_id: str, cost: float) -> None:
        """Update user account balance after a request"""
        if user_id in self.user_accounts:
            # Deduct cost from balance
            self.user_accounts[user_id]["balance"] -= cost
            self.user_accounts[user_id]["updated_at"] = datetime.now().isoformat()

            # Record transaction
            if "transactions" not in self.user_accounts[user_id]:
                self.user_accounts[user_id]["transactions"] = []

            self.user_accounts[user_id]["transactions"].append(
                {
                    "type": "usage",
                    "amount": -cost,
                    "timestamp": datetime.now().isoformat(),
                    "description": "API usage",
                }
            )

            # Save user accounts periodically (not after every transaction)
            # In a production system, this would be handled by a database
            if len(self.user_accounts[user_id]["transactions"]) % 10 == 0:
                self.save_user_accounts()

    def _get_account_balance(self, user_id: str) -> float:
        """Get user account balance"""
        if user_id in self.user_accounts:
            return self.user_accounts[user_id]["balance"]
        return 0.0

    def _log_usage(self, usage_record: Dict[str, Any]) -> None:
        """Log usage to file"""
        try:
            with open(self.usage_log_file, "a") as f:
                f.write(json.dumps(usage_record) + "\n")
        except Exception as e:
            logger.error(f"Error logging usage: {e}")

    def _calculate_duration(self, start_time: str) -> str:
        """Calculate duration between start time and now"""
        try:
            start = datetime.fromisoformat(start_time)
            now = datetime.now()
            duration = now - start
            return str(duration)
        except Exception as e:
            logger.error(f"Error calculating duration: {e}")
            return "unknown"


# Main API integration functions - these would be called from the API endpoints
async def track_request_cost(
    price_integration: PricingIntegration,
    user_id: str,
    model: str,
    token_count: int,
    request_type: str = "completion",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Track the cost of a request and update user account

    Args:
        price_integration: PricingIntegration instance
        user_id: User identifier
        model: Model used
        token_count: Number of tokens used
        request_type: Type of request
        session_id: Optional session identifier

    Returns:
        dict: Usage information including cost
    """
    return price_integration.track_token_usage(
        user_id=user_id,
        model=model,
        token_count=token_count,
        request_type=request_type,
        session_id=session_id,
    )


async def check_request_authorization(
    price_integration: PricingIntegration,
    user_id: str,
    model: str,
    estimated_tokens: int,
    request_type: str = "completion",
) -> Dict[str, Any]:
    """
    Check if a user is authorized to make a request based on their account balance

    Args:
        price_integration: PricingIntegration instance
        user_id: User identifier
        model: Model to be used
        estimated_tokens: Estimated token count
        request_type: Type of request

    Returns:
        dict: Authorization status and cost estimate
    """
    if not price_integration.pricing_enabled:
        return {"authorized": True, "reason": "Pricing not enabled"}

    # Anonymous users are always authorized when pricing is disabled
    if user_id == "anonymous":
        return {"authorized": True, "reason": "Anonymous user"}

    # Estimate cost
    estimate = price_integration.estimate_request_cost(
        user_id=user_id,
        model=model,
        estimated_tokens=estimated_tokens,
        request_type=request_type,
    )

    # Check if user has account
    if user_id not in price_integration.user_accounts:
        return {
            "authorized": False,
            "reason": "User account not found",
            "estimated_cost": estimate["estimated_cost"],
        }

    # Check if user has sufficient balance
    if price_integration.user_accounts[user_id]["balance"] < estimate["estimated_cost"]:
        return {
            "authorized": False,
            "reason": "Insufficient funds",
            "estimated_cost": estimate["estimated_cost"],
            "current_balance": price_integration.user_accounts[user_id]["balance"],
        }

    return {
        "authorized": True,
        "estimated_cost": estimate["estimated_cost"],
        "current_balance": price_integration.user_accounts[user_id]["balance"],
        "remaining_balance": price_integration.user_accounts[user_id]["balance"]
        - estimate["estimated_cost"],
    }


# Example integration with FastAPI
"""
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Initialize pricing integration
pricing_integration = PricingIntegration(pricing_enabled=True)
pricing_integration.load_user_accounts()

class TokenUsageRequest(BaseModel):
    user_id: str
    model: str
    token_count: int
    request_type: str = "completion"
    session_id: Optional[str] = None

@app.post("/api/track-usage")
async def track_usage(request: TokenUsageRequest):
    result = await track_request_cost(
        price_integration=pricing_integration,
        user_id=request.user_id,
        model=request.model,
        token_count=request.token_count,
        request_type=request.request_type,
        session_id=request.session_id
    )
    return result

class RequestAuthorizationCheck(BaseModel):
    user_id: str
    model: str
    estimated_tokens: int
    request_type: str = "completion"

@app.post("/api/check-authorization")
async def check_authorization(request: RequestAuthorizationCheck):
    result = await check_request_authorization(
        price_integration=pricing_integration,
        user_id=request.user_id,
        model=request.model,
        estimated_tokens=request.estimated_tokens,
        request_type=request.request_type
    )
    return result

class CreateUserRequest(BaseModel):
    user_id: str
    tier: str = "basic"
    initial_balance: float = 0.0

@app.post("/api/create-user")
async def create_user(request: CreateUserRequest):
    result = pricing_integration.create_user_account(
        user_id=request.user_id,
        tier=request.tier,
        initial_balance=request.initial_balance
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

class AddFundsRequest(BaseModel):
    user_id: str
    amount: float
    description: str = "Deposit"

@app.post("/api/add-funds")
async def add_funds(request: AddFundsRequest):
    result = pricing_integration.add_funds(
        user_id=request.user_id,
        amount=request.amount,
        description=request.description
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.get("/api/user/{user_id}/balance")
async def get_balance(user_id: str):
    result = pricing_integration.check_balance(user_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@app.get("/api/user/{user_id}/usage")
async def get_user_usage(user_id: str):
    result = pricing_integration.get_user_usage_summary(user_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    result = pricing_integration.get_session_summary(session_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
"""
