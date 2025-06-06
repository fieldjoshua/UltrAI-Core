"""
Transaction Service

This service handles user balance management, cost deduction, and payment processing.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from app.utils.logging import get_logger

logger = get_logger("transaction_service")


@dataclass
class Transaction:
    """A financial transaction."""

    user_id: str
    amount: float
    type: str  # "credit" or "debit"
    description: str
    timestamp: datetime = datetime.now()
    status: str = "pending"  # "pending", "completed", "failed"


class TransactionService:
    """Service for managing financial transactions."""

    def __init__(self):
        """Initialize the transaction service."""
        self._balances: Dict[str, float] = {}
        self._transactions: Dict[str, list[Transaction]] = {}

    async def get_balance(self, user_id: str) -> float:
        """
        Get user's current balance.

        Args:
            user_id: ID of the user

        Returns:
            float: Current balance
        """
        return self._balances.get(user_id, 0.0)

    async def add_funds(
        self, user_id: str, amount: float, description: str
    ) -> Transaction:
        """
        Add funds to user's balance.

        Args:
            user_id: ID of the user
            amount: Amount to add
            description: Transaction description

        Returns:
            Transaction: The transaction record
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        transaction = Transaction(
            user_id=user_id, amount=amount, type="credit", description=description
        )

        current_balance = await self.get_balance(user_id)
        self._balances[user_id] = current_balance + amount

        if user_id not in self._transactions:
            self._transactions[user_id] = []
        self._transactions[user_id].append(transaction)

        logger.info(
            f"Added ${amount:.2f} to user {user_id}. "
            f"New balance: ${self._balances[user_id]:.2f}"
        )

        return transaction

    async def deduct_cost(
        self, user_id: str, amount: float, description: str
    ) -> Optional[Transaction]:
        """
        Deduct cost from user's balance.

        Args:
            user_id: ID of the user
            amount: Amount to deduct
            description: Transaction description

        Returns:
            Optional[Transaction]: The transaction record if successful
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        current_balance = await self.get_balance(user_id)
        if current_balance < amount:
            logger.warning(
                f"Insufficient funds for user {user_id}. "
                f"Required: ${amount:.2f}, Available: ${current_balance:.2f}"
            )
            return None

        transaction = Transaction(
            user_id=user_id, amount=amount, type="debit", description=description
        )

        self._balances[user_id] = current_balance - amount

        if user_id not in self._transactions:
            self._transactions[user_id] = []
        self._transactions[user_id].append(transaction)

        logger.info(
            f"Deducted ${amount:.2f} from user {user_id}. "
            f"New balance: ${self._balances[user_id]:.2f}"
        )

        return transaction

    def get_transaction_history(self, user_id: str) -> list[Transaction]:
        """
        Get transaction history for a user.

        Args:
            user_id: ID of the user

        Returns:
            list[Transaction]: List of transactions
        """
        return self._transactions.get(user_id, [])
