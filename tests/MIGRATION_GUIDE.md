# Test Configuration Migration Guide

This guide helps you migrate existing tests to use the new test configuration system.

## Quick Migration Checklist

- [ ] Remove hardcoded mocks and patches
- [ ] Import `TestConfig` from `tests.test_config`
- [ ] Use fixture-based mocks (`mock_llm_adapters`, `mock_redis`, etc.)
- [ ] Add appropriate test markers (`@pytest.mark.integration`, etc.)
- [ ] Use `TestConfig.should_mock` for conditional mocking
- [ ] Replace hardcoded URLs with `TestConfig.endpoints`
- [ ] Use `TestConfig.get_timeout()` for timeout values

## Migration Examples

### Example 1: Simple Mock Migration

**Before:**
```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_llm_call():
    with patch('app.services.llm_adapters.OpenAIAdapter') as mock:
        mock_instance = AsyncMock()
        mock_instance.generate.return_value = {"text": "response"}
        mock.return_value = mock_instance
        
        # test code
        result = await some_function_using_llm()
        assert result == "response"
```

**After:**
```python
import pytest
from tests.test_config import TestConfig

@pytest.mark.asyncio
async def test_llm_call(mock_llm_adapters):
    # Mocks are automatically provided in OFFLINE/MOCK modes
    result = await some_function_using_llm()
    
    if TestConfig.should_mock["llm_responses"]:
        # In mock mode, verify mock behavior
        assert "Mock response" in result
    else:
        # In live mode, verify real response
        assert result is not None
```

### Example 2: Integration Test Migration

**Before:**
```python
import pytest
from sqlalchemy import create_engine

@pytest.mark.asyncio
async def test_database_operation():
    # Hardcoded test database
    engine = create_engine("postgresql://localhost/test_db")
    
    # test code
```

**After:**
```python
import pytest
from tests.test_config import TestConfig, skip_if_offline

@pytest.mark.integration
@skip_if_offline()
@pytest.mark.asyncio
async def test_database_operation():
    # Use configured database URL
    db_url = TestConfig.endpoints.database_url
    
    if db_url:
        # Database is available in this mode
        engine = create_engine(db_url)
        # test code
```

### Example 3: API Endpoint Test Migration

**Before:**
```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_api_endpoint():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/models")
        assert response.status_code == 200
```

**After:**
```python
import httpx
import pytest
from tests.test_config import TestConfig

@pytest.mark.asyncio
async def test_api_endpoint(test_client):
    # test_client is pre-configured with correct base URL and timeout
    response = await test_client.get("/api/models")
    assert response.status_code == 200
```

### Example 4: Live Provider Test Migration

**Before:**
```python
import os
import pytest

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
@pytest.mark.asyncio
async def test_openai_live():
    # test code
```

**After:**
```python
import pytest
from tests.test_config import skip_if_no_api_keys

@pytest.mark.live
@skip_if_no_api_keys()
@pytest.mark.asyncio
async def test_openai_live():
    # Test will automatically skip if:
    # - Not in LIVE mode
    # - API keys are missing
    # test code
```

### Example 5: Conditional Logic Migration

**Before:**
```python
import pytest
import os

@pytest.mark.asyncio
async def test_with_conditional():
    if os.getenv("CI"):
        # Use mocks in CI
        with patch(...):
            # test code
    else:
        # Use real services locally
        # test code
```

**After:**
```python
import pytest
from tests.test_config import TestConfig
from tests.mock_config import create_mock_llm_adapter

@pytest.mark.asyncio
async def test_with_conditional():
    if TestConfig.is_offline:
        # Automatically uses mocks
        adapter = create_mock_llm_adapter()
    else:
        # Use real adapter
        adapter = create_real_adapter()
    
    # Single test code path
    result = await adapter.generate("test")
    assert result is not None
```

## Common Patterns

### Pattern 1: Mode-Specific Assertions
```python
def test_response_format(mock_llm_adapters):
    result = call_llm_function()
    
    if TestConfig.mode == TestMode.OFFLINE:
        # Verify mock response format
        assert result.startswith("Mock response")
    elif TestConfig.mode == TestMode.LIVE:
        # Verify real response format
        assert "generated_text" in result
```

### Pattern 2: Timeout Handling
```python
@pytest.mark.asyncio
async def test_slow_operation():
    timeout = TestConfig.get_timeout("orchestration")
    
    async with asyncio.timeout(timeout):
        result = await slow_operation()
```

### Pattern 3: Service Availability
```python
@pytest.mark.asyncio
async def test_requiring_services():
    if TestConfig.endpoints.redis_url:
        # Redis is available
        cache = await connect_redis(TestConfig.endpoints.redis_url)
        # test with cache
    else:
        # Redis not available, test without cache
        # test without cache
```

## Fixture Reference

### Available Fixtures

| Fixture | Description | Available When |
|---------|-------------|----------------|
| `mock_llm_adapters` | Mocked LLM adapters | `should_mock["llm_responses"]` is True |
| `mock_redis` | In-memory Redis mock | `should_mock["redis"]` is True |
| `mock_database` | Mock database session | `should_mock["database"]` is True |
| `test_client` | Configured HTTP client | Always |
| `test_endpoints` | Endpoint configuration | Always |
| `test_timeouts` | Timeout configuration | Always |

### Using Fixtures
```python
@pytest.mark.asyncio
async def test_with_fixtures(mock_llm_adapters, test_client, test_endpoints):
    # Fixtures are automatically injected
    if mock_llm_adapters:
        # Using mocks
        pass
    
    # test_client is pre-configured
    response = await test_client.get("/api/health")
    
    # Access endpoints
    api_url = test_endpoints.api_base_url
```

## Best Practices

1. **Always check TestConfig.mode when behavior differs**
   ```python
   if TestConfig.mode == TestMode.LIVE:
       # Live-specific code
   ```

2. **Use decorators for test selection**
   ```python
   @skip_if_offline()  # Better than manual checks
   ```

3. **Leverage fixture injection**
   ```python
   def test_example(mock_redis):  # Automatically None if not mocking
   ```

4. **Use configuration for all external dependencies**
   ```python
   url = TestConfig.endpoints.api_base_url  # Not hardcoded
   ```

5. **Document mode requirements**
   ```python
   @pytest.mark.integration
   async def test_needs_db():
       """Test requires database (INTEGRATION mode or higher)"""
   ```

## Troubleshooting

### Issue: Tests failing after migration
- Check if `TEST_MODE` is set correctly
- Verify fixtures are being used
- Ensure markers are applied

### Issue: Mocks not being applied
- Confirm `TestConfig.should_mock` settings
- Check fixture usage in test signature
- Verify test mode with `print(TestConfig.mode)`

### Issue: Tests skipped unexpectedly
- Check pytest markers
- Verify skip decorators
- Run with `-v` to see skip reasons

### Issue: Import errors
- Ensure virtual environment is activated
- Add `tests/` to PYTHONPATH if needed
- Check relative imports