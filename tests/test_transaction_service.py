import pytest
from app.services.transaction_service import TransactionService, Transaction


@pytest.fixture
def transaction_service(tmp_path):
    """Fixture to create a fresh TransactionService instance for each test,
    using a temporary file for persistence to ensure test isolation.
    """
    # Create a temporary data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    persistence_file = data_dir / "financial_transactions.json"

    # Patch the service to use the temporary file
    service = TransactionService()
    service._persistence_file = str(persistence_file)
    # Clear any in-memory data that might have been loaded from a real file
    service._balances.clear()
    service._transactions.clear()
    
    return service


@pytest.mark.asyncio
async def test_get_balance_default_zero(transaction_service):
    balance = await transaction_service.get_balance("user1")
    assert balance == 0.0


@pytest.mark.asyncio
async def test_add_funds_positive_amount(transaction_service):
    user_id = "user1"
    transaction = await transaction_service.add_funds(user_id, 100.0, "Test credit")
    assert isinstance(transaction, Transaction)
    assert transaction.user_id == user_id
    assert transaction.amount == 100.0
    assert transaction.type == "credit"
    assert transaction.description == "Test credit"
    balance = await transaction_service.get_balance(user_id)
    assert balance == 100.0
    history = transaction_service.get_transaction_history(user_id)
    assert len(history) == 1
    assert history[0] is transaction


@pytest.mark.asyncio
async def test_add_funds_negative_amount_raises(transaction_service):
    with pytest.raises(ValueError):
        await transaction_service.add_funds("user1", -50.0, "Invalid credit")


@pytest.mark.asyncio
async def test_deduct_cost_insufficient_returns_none(transaction_service):
    user_id = "user2"
    result = await transaction_service.deduct_cost(user_id, 10.0, "Test debit")
    assert result is None
    balance = await transaction_service.get_balance(user_id)
    assert balance == 0.0
    history = transaction_service.get_transaction_history(user_id)
    assert history == []


@pytest.mark.asyncio
async def test_deduct_cost_negative_amount_raises(transaction_service):
    with pytest.raises(ValueError):
        await transaction_service.deduct_cost("user1", -20.0, "Invalid debit")


@pytest.mark.asyncio
async def test_deduct_cost_successful_after_credit(transaction_service):
    user_id = "user3"
    await transaction_service.add_funds(user_id, 100.0, "Initial credit")
    debit_tx = await transaction_service.deduct_cost(user_id, 40.0, "Test debit")
    assert isinstance(debit_tx, Transaction)
    assert debit_tx.user_id == user_id
    assert debit_tx.amount == 40.0
    assert debit_tx.type == "debit"
    assert debit_tx.description == "Test debit"
    balance = await transaction_service.get_balance(user_id)
    assert balance == 60.0
    history = transaction_service.get_transaction_history(user_id)
    assert len(history) == 2
    assert history[0].type == "credit"
    assert history[1] is debit_tx
