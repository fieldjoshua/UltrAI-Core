import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture(scope="session")
def client():
    """
    Create a TestClient for the FastAPI application."""
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.mark.e2e
def test_user_financial_flow(client):
    """End-to-end test: user adds funds and checks balance."""
    # Initial balance should be zero
    response = client.get("/api/user/balance")
    assert response.status_code == 200
    assert response.json() == 0.0

    # Add funds
    deposit = {"amount": 150.0, "description": "Test deposit"}
    response = client.post("/api/user/add-funds", json=deposit)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == pytest.approx(150.0)
    assert data["type"] == "credit"

    # New balance should reflect deposit
    response = client.get("/api/user/balance")
    assert response.status_code == 200
    assert response.json() == pytest.approx(150.0)


@pytest.mark.e2e
def test_user_transaction_history(client):
    """End-to-end test: transaction history includes recent deposit."""
    response = client.get("/api/user/transactions")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    # Expect at least one transaction with 150.0 amount
    assert any(txn.get("amount") == pytest.approx(150.0) for txn in history)
