from app.services.auth_service import AuthService


def test_create_and_verify_access_token():
    service = AuthService()
    token_data = service.create_access_token(user_id="123")
    assert "access_token" in token_data
    assert token_data["user_id"] == "123"
    payload = service.verify_token(token_data["access_token"])
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["type"] == "access"


def test_create_and_verify_refresh_token():
    service = AuthService()
    refresh_token = service.create_refresh_token(user_id="456")
    payload = service.verify_refresh_token(refresh_token)
    assert payload is not None
    assert payload["sub"] == "456"
    assert payload["type"] == "refresh"


def test_verify_invalid_tokens():
    service = AuthService()
    assert service.verify_token("invalid.token") is None
    assert service.verify_refresh_token("invalid.token") is None
