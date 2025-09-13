import os
import importlib
from typing import Generator
import pytest


@pytest.fixture()
def temp_db_url(tmp_path) -> Generator[str, None, None]:
    db_file = tmp_path / "test_integration.db"
    url = f"sqlite:///{db_file}"
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        yield url
    finally:
        if old is not None:
            os.environ["DATABASE_URL"] = old
        else:
            os.environ.pop("DATABASE_URL", None)


@pytest.fixture()
def db_session(temp_db_url):
    # Reload session module so it picks up the temp DATABASE_URL
    session_module = importlib.import_module("app.database.session")
    importlib.reload(session_module)

    # Initialize schema
    session_module.init_db()

    with session_module.get_db_session() as db:
        yield db


@pytest.mark.integration
def test_user_creation_and_retrieval(db_session):
    from app.database.repositories.user import UserRepository
    from app.database.models.user import User
    from app.utils.exceptions import ResourceAlreadyExistsException

    repo = UserRepository()

    data = {
        "email": "alice@example.com",
        "username": "alice",
        "full_name": "Alice A",
        "hashed_password": "x",
    }

    user = repo.create_user(db_session, data)
    assert isinstance(user, User)
    fetched = repo.get_by_email(db_session, "alice@example.com")
    assert fetched is not None
    assert fetched.email == "alice@example.com"

    # Duplicate email should raise
    with pytest.raises(ResourceAlreadyExistsException):
        repo.create_user(db_session, data)


@pytest.mark.integration
def test_transaction_rollback(db_session):
    from app.database.models.user import User

    # Start a transaction, add a user, then roll back
    user = User(
        email="bob@example.com",
        username="bob",
        full_name="Bob B",
        hashed_password="x",
    )
    db_session.add(user)
    # No commit; rollback should discard
    db_session.rollback()

    found = db_session.query(User).filter(User.email == "bob@example.com").first()
    assert found is None
