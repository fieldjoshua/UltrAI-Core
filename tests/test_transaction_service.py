import pytest
from app.services.transaction_service import TransactionService, Transaction


@pytest.mark.asyncio
async def test_get_balance_default_zero():
    service = TransactionService()
    balance = await service.get_balance("user1")
    assert balance == 0.0


@pytest.mark.asyncio
async def test_add_funds_positive_amount():
    service = TransactionService()
    user_id = "user1"
    transaction = await service.add_funds(user_id, 100.0, "Test credit")
    assert isinstance(transaction, Transaction)
    assert transaction.user_id == user_id
    assert transaction.amount == 100.0
    assert transaction.type == "credit"
    assert transaction.description == "Test credit"
    balance = await service.get_balance(user_id)
    assert balance == 100.0
    history = service.get_transaction_history(user_id)
    assert len(history) == 1
    assert history[0] is transaction


@pytest.mark.asyncio
async def test_add_funds_negative_amount_raises():
    service = TransactionService()
    with pytest.raises(ValueError):
        await service.add_funds("user1", -50.0, "Invalid credit")


@pytest.mark.asyncio
async def test_deduct_cost_insufficient_returns_none():
    service = TransactionService()
    user_id = "user2"
    result = await service.deduct_cost(user_id, 10.0, "Test debit")
    assert result is None
    balance = await service.get_balance(user_id)
    assert balance == 0.0
    history = service.get_transaction_history(user_id)
    assert history == []


@pytest.mark.asyncio
async def test_deduct_cost_negative_amount_raises():
    service = TransactionService()
    with pytest.raises(ValueError):
        await service.deduct_cost("user1", -20.0, "Invalid debit")


@pytest.mark.asyncio
async def test_deduct_cost_successful_after_credit():
    service = TransactionService()
    user_id = "user3"
    await service.add_funds(user_id, 100.0, "Initial credit")
    debit_tx = await service.deduct_cost(user_id, 40.0, "Test debit")
    assert isinstance(debit_tx, Transaction)
    assert debit_tx.user_id == user_id
    assert debit_tx.amount == 40.0
    assert debit_tx.type == "debit"
    assert debit_tx.description == "Test debit"
    balance = await service.get_balance(user_id)
    assert balance == 60.0
    history = service.get_transaction_history(user_id)
    assert len(history) == 2
    assert history[0].type == "credit"
    assert history[1] is debit_tx
