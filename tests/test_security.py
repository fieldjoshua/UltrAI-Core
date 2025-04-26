import pytest
import asyncio
from datetime import datetime
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics


class MockSecurityLLMClient:
    def __init__(self, name):
        self.name = name
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        return f"Response from {self.name} for: {prompt}"


@pytest.fixture
def security_orchestrator():
    return TriLLMOrchestrator(
        llama_client=MockSecurityLLMClient("Llama"),
        chatgpt_client=MockSecurityLLMClient("ChatGPT"),
        gemini_client=MockSecurityLLMClient("Gemini"),
        cache_enabled=True,
    )


@pytest.mark.asyncio
async def test_input_validation(security_orchestrator):
    # Test SQL injection attempt
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("'; DROP TABLE users; --")

    # Test XSS attempt
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("<script>alert('xss')</script>")

    # Test command injection attempt
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("; rm -rf /;")


@pytest.mark.asyncio
async def test_rate_limiting(security_orchestrator):
    # Test rapid requests
    prompts = [f"Test rate limit {i}" for i in range(10)]

    for prompt in prompts:
        try:
            await security_orchestrator.process_responses(prompt)
        except Exception as e:
            assert "rate limit" in str(e).lower()
            break
    else:
        pytest.fail("Rate limiting not enforced")


@pytest.mark.asyncio
async def test_token_validation(security_orchestrator):
    # Test with invalid token
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("test", token="invalid_token")

    # Test with expired token
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("test", token="expired_token")

    # Test with missing token
    with pytest.raises(ValueError):
        await security_orchestrator.process_responses("test", token=None)


@pytest.mark.asyncio
async def test_response_sanitization(security_orchestrator):
    # Test response sanitization
    result = await security_orchestrator.process_responses("test")

    # Verify no HTML in response
    assert "<script>" not in str(result)
    assert "<iframe>" not in str(result)

    # Verify no SQL in response
    assert "DROP TABLE" not in str(result)
    assert "DELETE FROM" not in str(result)

    # Verify no command injection in response
    assert "rm -rf" not in str(result)
    assert ";" not in str(result)


@pytest.mark.asyncio
async def test_error_message_security(security_orchestrator):
    # Test error message security
    try:
        await security_orchestrator.process_responses("'; DROP TABLE users; --")
    except ValueError as e:
        error_message = str(e)
        # Verify error message doesn't expose sensitive information
        assert "DROP TABLE" not in error_message
        assert "users" not in error_message
        assert "SQL" not in error_message


@pytest.mark.asyncio
async def test_cache_security(security_orchestrator):
    # Test cache security
    prompt = "Test cache security"

    # First call
    result1 = await security_orchestrator.process_responses(prompt)

    # Second call should use cache
    result2 = await security_orchestrator.process_responses(prompt)

    # Verify cached data is sanitized
    assert "<script>" not in str(result2)
    assert "DROP TABLE" not in str(result2)
    assert "rm -rf" not in str(result2)

    # Verify cache doesn't expose sensitive information
    assert "password" not in str(result2)
    assert "token" not in str(result2)
    assert "secret" not in str(result2)
