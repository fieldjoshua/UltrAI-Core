# Test Configuration System

The Ultra project uses a unified test configuration system that allows running tests in different modes depending on your needs.

## Test Modes

### 1. **OFFLINE Mode** (Default)
- All external dependencies are mocked
- No network calls
- Fastest execution
- Use: `make test` or `make test-offline`

### 2. **MOCK Mode**
- Sophisticated mock responses
- Authentication enabled
- More realistic test scenarios
- Use: `make test-mock`

### 3. **INTEGRATION Mode**
- Uses local Redis and PostgreSQL
- LLM APIs are still mocked
- Tests service integration
- Use: `make test-integration`

### 4. **LIVE Mode**
- Real API calls to LLM providers
- Requires API keys
- Tests actual integration
- Use: `make test-live`

### 5. **PRODUCTION Mode**
- Tests against deployed endpoints
- Full end-to-end validation
- Use: `make test-production`

## Configuration

Set the test mode using the `TEST_MODE` environment variable:

```bash
TEST_MODE=offline pytest tests/
TEST_MODE=live pytest tests/
```

Or use the Makefile commands:

```bash
make test          # Runs offline tests
make test-live     # Runs live tests
```

## Writing Tests

### Using Test Mode Decorators

```python
from tests.test_config import requires_mode, skip_in_modes, TestMode

@requires_mode(TestMode.LIVE, TestMode.PRODUCTION)
def test_real_api_call():
    # This test only runs in LIVE or PRODUCTION mode
    pass

@skip_in_modes(TestMode.OFFLINE)
def test_needs_services():
    # This test is skipped in OFFLINE mode
    pass
```

### Using Pytest Markers

```python
@pytest.mark.live_online
def test_live_api():
    # Automatically skipped in offline/mock modes
    pass

@pytest.mark.integration
def test_with_database():
    # Requires local services
    pass
```

### Using Mock Fixtures

```python
def test_with_mocks(mock_llm_adapters):
    # mock_llm_adapters is automatically injected based on test mode
    if mock_llm_adapters:
        # We're in a mocked mode
        pass
    else:
        # We're in live mode
        pass
```

## Environment Variables

Each mode sets appropriate environment variables:

- `TESTING=true` - Always set in test mode
- `USE_MOCK=true/false` - Controls LLM mocking
- `ENABLE_AUTH=true/false` - Controls authentication
- `REDIS_URL` - Redis connection (empty in offline mode)
- `DATABASE_URL` - Database connection (empty in offline mode)

## CI/CD Integration

For continuous integration, use:

```yaml
# GitHub Actions example
- name: Run offline tests
  run: make test-offline

- name: Run integration tests
  run: |
    docker-compose up -d redis postgres
    make test-integration
```

## Troubleshooting

1. **Import errors**: Ensure you have `tests/__init__.py`
2. **Fixture not found**: Check that conftest.py is loading correctly
3. **Tests running in wrong mode**: Check `TEST_MODE` environment variable
4. **API key errors in LIVE mode**: Ensure all required keys are set

## Examples

See `tests/test_example_modes.py` for examples of how to use the configuration system.