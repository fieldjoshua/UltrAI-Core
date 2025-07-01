"""
Transaction Service

This service handles user balance management, cost deduction, and payment processing.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

from app.utils.logging import get_logger

logger = get_logger("transaction_service")

# Redis client for persistent storage
try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info(f"Connected to Redis at {REDIS_URL}")
    REDIS_AVAILABLE = True
except (ImportError, redis.ConnectionError) as e:
    logger.warning(f"Redis not available: {e}. Using file-based persistence as fallback.")
    redis_client = None
    REDIS_AVAILABLE = False


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
        self._persistence_file = "data/financial_transactions.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load financial data from persistent storage."""
        try:
            if REDIS_AVAILABLE and redis_client:
                # Load from Redis
                balances_data = redis_client.get("ultra:balances")
                if balances_data:
                    self._balances = json.loads(balances_data)
                
                transactions_data = redis_client.get("ultra:transactions")
                if transactions_data:
                    # Deserialize transactions
                    tx_dict = json.loads(transactions_data)
                    for user_id, tx_list in tx_dict.items():
                        self._transactions[user_id] = [
                            Transaction(
                                user_id=tx["user_id"],
                                amount=tx["amount"],
                                type=tx["type"],
                                description=tx["description"],
                                timestamp=datetime.fromisoformat(tx["timestamp"]),
                                status=tx["status"]
                            ) for tx in tx_list
                        ]
                logger.info("Loaded financial data from Redis")
            else:
                # Fallback to file storage
                if os.path.exists(self._persistence_file):
                    with open(self._persistence_file, 'r') as f:
                        data = json.load(f)
                        self._balances = data.get("balances", {})
                        
                        # Deserialize transactions
                        tx_dict = data.get("transactions", {})
                        for user_id, tx_list in tx_dict.items():
                            self._transactions[user_id] = [
                                Transaction(
                                    user_id=tx["user_id"],
                                    amount=tx["amount"],
                                    type=tx["type"],
                                    description=tx["description"],
                                    timestamp=datetime.fromisoformat(tx["timestamp"]),
                                    status=tx["status"]
                                ) for tx in tx_list
                            ]
                    logger.info("Loaded financial data from file")
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")

    def _save_data(self):
        """Save financial data to persistent storage."""
        try:
            # Serialize transactions for storage
            serialized_transactions = {}
            for user_id, tx_list in self._transactions.items():
                serialized_transactions[user_id] = [
                    {
                        "user_id": tx.user_id,
                        "amount": tx.amount,
                        "type": tx.type,
                        "description": tx.description,
                        "timestamp": tx.timestamp.isoformat(),
                        "status": tx.status
                    } for tx in tx_list
                ]
            
            if REDIS_AVAILABLE and redis_client:
                # Save to Redis
                redis_client.set("ultra:balances", json.dumps(self._balances))
                redis_client.set("ultra:transactions", json.dumps(serialized_transactions))
                logger.debug("Saved financial data to Redis")
            else:
                # Fallback to file storage
                data = {
                    "balances": self._balances,
                    "transactions": serialized_transactions,
                    "last_updated": datetime.now().isoformat()
                }
                with open(self._persistence_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.debug("Saved financial data to file")
        except Exception as e:
            logger.error(f"Error saving financial data: {e}")

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

        # Persist the data
        self._save_data()

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

        # Persist the data
        self._save_data()

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
