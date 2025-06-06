"""
Unit tests for TransactionService.
"""

import pytest
from datetime import datetime
from app.services.transaction_service import TransactionService, Transaction


@pytest.fixture
def transaction_service():
    """Create a TransactionService instance for testing."""
    return TransactionService()


@pytest.mark.asyncio
async def test_get_balance(transaction_service):
    """Test getting user balance."""
    # Initial balance should be 0
    balance = await transaction_service.get_balance("test_user")
    assert balance == 0.0

    # Add funds and check balance
    await transaction_service.add_funds(
        user_id="test_user", amount=100.0, description="Test deposit"
    )
    balance = await transaction_service.get_balance("test_user")
    assert balance == 100.0


@pytest.mark.asyncio
async def test_add_funds(transaction_service):
    """Test adding funds to user balance."""
    transaction = await transaction_service.add_funds(
        user_id="test_user", amount=50.0, description="Test deposit"
    )

    assert isinstance(transaction, Transaction)
    assert transaction.user_id == "test_user"
    assert transaction.amount == 50.0
    assert transaction.type == "credit"
    assert transaction.description == "Test deposit"
    assert transaction.status == "pending"


@pytest.mark.asyncio
async def test_deduct_cost(transaction_service):
    """Test deducting costs from user balance."""
    # Add funds first
    await transaction_service.add_funds(
        user_id="test_user", amount=100.0, description="Initial deposit"
    )

    # Deduct cost
    transaction = await transaction_service.deduct_cost(
        user_id="test_user", amount=30.0, description="Test cost"
    )

    assert isinstance(transaction, Transaction)
    assert transaction.user_id == "test_user"
    assert transaction.amount == 30.0
    assert transaction.type == "debit"
    assert transaction.description == "Test cost"

    # Check updated balance
    balance = await transaction_service.get_balance("test_user")
    assert balance == 70.0


@pytest.mark.asyncio
async def test_insufficient_funds(transaction_service):
    """Test handling of insufficient funds."""
    # Try to deduct more than available
    transaction = await transaction_service.deduct_cost(
        user_id="test_user", amount=50.0, description="Test cost"
    )

    assert transaction is None
    balance = await transaction_service.get_balance("test_user")
    assert balance == 0.0


@pytest.mark.asyncio
async def test_get_transaction_history(transaction_service):
    """Test retrieving transaction history."""
    # Add some transactions
    await transaction_service.add_funds(
        user_id="test_user", amount=100.0, description="First deposit"
    )
    await transaction_service.deduct_cost(
        user_id="test_user", amount=30.0, description="First cost"
    )
    await transaction_service.add_funds(
        user_id="test_user", amount=50.0, description="Second deposit"
    )

    history = transaction_service.get_transaction_history("test_user")
    assert len(history) == 3
    assert history[0].type == "credit"
    assert history[1].type == "debit"
    assert history[2].type == "credit"


@pytest.mark.asyncio
async def test_invalid_amount(transaction_service):
    """Test handling of invalid amounts."""
    with pytest.raises(ValueError, match="Amount must be positive"):
        await transaction_service.add_funds(
            user_id="test_user", amount=-50.0, description="Invalid deposit"
        )

    with pytest.raises(ValueError, match="Amount must be positive"):
        await transaction_service.deduct_cost(
            user_id="test_user", amount=-30.0, description="Invalid cost"
        )
