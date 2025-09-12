th# flake8: noqa
"""
Transaction Service with Database Integration

This service handles user balance management, cost deduction, and payment processing
using the database for persistence.
"""

from typing import Dict, Optional, List, Any, cast
from datetime import datetime
from decimal import Decimal

from sqlalchemy import desc

from app.database.models.user import User
from app.database.models.transaction import (
    Transaction, TransactionType, TransactionStatus, UsageTracking
)
from app.utils.logging import get_logger

logger = get_logger("transaction_service")


class TransactionServiceDB:
    """Transaction service with database persistence."""

    def __init__(self, db_session_factory):
        """
        Initialize transaction service.

        Args:
            db_session_factory: SQLAlchemy session factory
        """
        self.db_session_factory = db_session_factory

    async def get_user_balance(self, user_id: str) -> float:
        """
        Get user's current balance.

        Args:
            user_id: User ID

        Returns:
            Current balance
        """
        with self.db_session_factory() as db:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return 0.0
            return float(user.account_balance)

    async def create_transaction(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,
        description: str,
        provider: Optional[str] = None,
        provider_transaction_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new financial transaction.

        Args:
            user_id: User ID
            amount: Transaction amount
            transaction_type: "credit" or "debit"
            description: Transaction description
            provider: Payment provider
            provider_transaction_id: Provider's transaction ID
            related_entity_type: Related entity type (e.g., "analysis")
            related_entity_id: Related entity ID

        Returns:
            Transaction details
        """
        with self.db_session_factory() as db:
            # Get user
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Calculate new balance
            balance_before = user.account_balance

            if transaction_type == "credit":
                new_balance = balance_before + Decimal(str(amount))
                trans_type = TransactionType.CREDIT
            elif transaction_type == "debit":
                if balance_before < Decimal(str(amount)):
                    raise ValueError("Insufficient balance")
                new_balance = balance_before - Decimal(str(amount))
                trans_type = TransactionType.DEBIT
            else:
                raise ValueError(f"Invalid transaction type: {transaction_type}")

            # Create transaction
            transaction = Transaction(
                user_id=int(user_id),
                type=trans_type,
                amount=Decimal(str(amount)),
                balance_before=balance_before,
                balance_after=new_balance,
                description=description,
                provider=provider,
                provider_transaction_id=provider_transaction_id,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                status=TransactionStatus.COMPLETED,
                completed_at=datetime.utcnow(),
            )

            # Update user balance
            user.account_balance = new_balance

            # Save to database
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(
                f"Transaction created: {trans_type.value} ${amount} for user {user_id}"
            )

            return {
                "id": transaction.id,
                "user_id": transaction.user_id,
                "type": transaction.type.value,
                "amount": float(cast(Decimal, transaction.amount)),
                "balance_before": float(cast(Decimal, transaction.balance_before)),
                "balance_after": float(cast(Decimal, transaction.balance_after)),
                "description": transaction.description,
                "status": transaction.status.value,
                "created_at": transaction.created_at.isoformat(),
            }

    async def deduct_cost(
        self,
        user_id: str,
        amount: float,
        description: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
    ) -> bool:
        """
        Deduct cost from user's balance.

        Args:
            user_id: User ID
            amount: Amount to deduct
            description: Description of the charge
            related_entity_type: Related entity type
            related_entity_id: Related entity ID

        Returns:
            True if successful, False if insufficient funds
        """
        try:
            await self.create_transaction(
                user_id=user_id,
                amount=amount,
                transaction_type="debit",
                description=description,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
            )
            return True
        except ValueError as e:
            if "Insufficient balance" in str(e):
                logger.warning(f"Insufficient funds for user {user_id}: ${amount}")
                return False
            raise

    async def add_credit(
        self,
        user_id: str,
        amount: float,
        description: str,
        provider: Optional[str] = None,
        provider_transaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add credit to user's balance.

        Args:
            user_id: User ID
            amount: Amount to add
            description: Credit description
            provider: Payment provider
            provider_transaction_id: Provider's transaction ID

        Returns:
            Transaction details
        """
        return await self.create_transaction(
            user_id=user_id,
            amount=amount,
            transaction_type="credit",
            description=description,
            provider=provider,
            provider_transaction_id=provider_transaction_id,
        )

    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user's transaction history.

        Args:
            user_id: User ID
            limit: Maximum number of transactions
            offset: Offset for pagination
            transaction_type: Filter by transaction type

        Returns:
            List of transactions
        """
        with self.db_session_factory() as db:
            query = db.query(Transaction).filter(
                Transaction.user_id == int(user_id)
            )

            if transaction_type:
                trans_type = TransactionType(transaction_type)
                query = query.filter(Transaction.type == trans_type)

            transactions = query.order_by(
                desc(Transaction.created_at)
            ).limit(limit).offset(offset).all()

            return [
                {
                    "id": t.id,
                    "type": t.type.value,
                    "amount": float(cast(Decimal, t.amount)),
                    "balance_after": float(cast(Decimal, t.balance_after)),
                    "description": t.description,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ]

    async def track_usage(
        self,
        user_id: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        input_cost: float,
        output_cost: float,
        endpoint: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """
        Track LLM usage for billing purposes.

        Args:
            user_id: User ID
            model: Model name
            provider: Provider name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_cost: Cost of input tokens
            output_cost: Cost of output tokens
            endpoint: API endpoint
            request_id: Request ID for tracking
        """
        with self.db_session_factory() as db:
            usage = UsageTracking(
                user_id=int(user_id),
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                input_cost=Decimal(str(input_cost)),
                output_cost=Decimal(str(output_cost)),
                total_cost=Decimal(str(input_cost + output_cost)),
                endpoint=endpoint,
                request_id=request_id,
            )

            db.add(usage)
            db.commit()

            logger.debug(
                f"Usage tracked: {model} {input_tokens}+{output_tokens} tokens "
                f"${input_cost + output_cost:.6f} for user {user_id}"
            )

    async def get_usage_summary(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get usage summary for a user.

        Args:
            user_id: User ID
            start_date: Start date filter
            end_date: End date filter

        Returns:
            Usage summary
        """
        with self.db_session_factory() as db:
            query = db.query(UsageTracking).filter(
                UsageTracking.user_id == int(user_id)
            )

            if start_date:
                query = query.filter(UsageTracking.timestamp >= start_date)
            if end_date:
                query = query.filter(UsageTracking.timestamp <= end_date)

            usage_records = query.all()

            # Aggregate by model
            model_usage: Dict[str, Dict[str, Any]] = {}
            total_cost = Decimal("0")
            total_tokens = 0

            for record in usage_records:
                if record.model not in model_usage:
                    model_usage[record.model] = {
                        "count": 0,
                        "tokens": 0,
                        "cost": Decimal("0"),
                    }

                model_usage[record.model]["count"] += 1
                model_usage[record.model]["tokens"] += record.total_tokens
                model_usage[record.model]["cost"] += record.total_cost

                total_cost += record.total_cost
                total_tokens += record.total_tokens

            return {
                "user_id": user_id,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None,
                },
                "total_cost": float(total_cost),
                "total_tokens": total_tokens,
                "by_model": {
                    model: {
                        "count": stats["count"],
                        "tokens": stats["tokens"],
                        "cost": float(stats["cost"]),
                    }
                    for model, stats in model_usage.items()
                },
            }

