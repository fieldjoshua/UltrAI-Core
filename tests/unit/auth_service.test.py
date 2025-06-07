from app.services.auth_service import AuthService


def test_create_and_verify_access_token():
    service = AuthService()
    token_data = service.create_access_token(user_id="123")
    assert "access_token" in token_data
    assert "expires_in" in token_data and isinstance(token_data["expires_in"], int)
    payload = service.verify_token(token_data["access_token"])
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["type"] == "access"


def test_verify_invalid_token():
    service = AuthService()
    payload = service.verify_token("invalid.token.string")
    assert payload is None
