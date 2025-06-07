import pytest
from app.services.oauth_service import OAuthService, oauth_states


@pytest.mark.asyncio
async def test_generate_oauth_url_unsupported():
    service = OAuthService()
    result = await service.generate_oauth_url("invalid")
    assert "error" in result


@pytest.mark.asyncio
async def test_generate_oauth_url_google(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "uri")
    service = OAuthService()
    result = await service.generate_oauth_url("google")
    assert "url" in result and "state" in result
    assert result["state"] in oauth_states


@pytest.mark.asyncio
async def test_validate_oauth_state():
    service = OAuthService()
    state = "teststate"
    oauth_states[state] = {"provider": "test"}
    assert await service.validate_oauth_state(state) is True
    assert await service.validate_oauth_state("invalid") is False
