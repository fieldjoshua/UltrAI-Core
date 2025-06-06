# Ultra Testing Suite

This directory contains all tests for the Ultra AI framework. The tests are organized by type and component.

## Running Tests

### Standard Testing

```bash
# Run all tests (using mock mode by default)
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_specific_file.py

# Run with coverage report
python -m pytest tests/ --cov=ultra
```

### Mock vs. Real Mode Testing

Ultra supports testing in both mock mode (for development) and real mode (for production validation):

```bash
# Run tests in mock mode (default for development)
./scripts/run_tests.sh

# Run tests in real mode with API endpoints
./scripts/test_real_mode.sh

# Toggle between testing modes
export USE_MOCK=true   # Use mock services
export USE_MOCK=false  # Use real services
```

### Environment-specific Testing

```bash
# Set environment variables for testing
export ENVIRONMENT=testing
export TESTING=true

# Test with mock mode
export USE_MOCK=true
export MOCK_MODE=true
python -m pytest tests/

# Test with real APIs
export USE_MOCK=false
export MOCK_MODE=false
export API_KEY_ENCRYPTION_KEY="your-key-here"
python -m pytest tests/
```

For detailed information on mock vs. real testing strategies, see [Mock vs. Real Testing Guide](../documentation/testing/mock_vs_real_testing.md).

## Test Files

### API Tests

- `test_api.py` - Tests for the API endpoints
- `test_document_upload.py` - Tests for document upload functionality

### Core Component Tests

- `test_clients.py` - Tests for API client implementations
- `test_config.py` - Tests for configuration management
- `test_orchestrator.py` - Tests for the pattern orchestrator

### Performance Tests

- `performance_test.py` - Performance benchmarking tests

## Adding New Tests

When adding new tests:

1. Follow the naming convention `test_*.py` for test files
2. Use descriptive test function names that express what's being tested
3. Group related tests in the same file or class
4. Add proper assertions to verify expected behavior
5. Consider adding tests for both success and failure cases

## Test Fixtures

Common test fixtures are available in `conftest.py` files. These provide reusable components for tests such as:

- Mock LLM services
- Test prompts and responses
- Sample documents for testing
- Environment configuration (mock/real modes)
- Authentication tokens for testing
- API request/response mocks

### Environment-aware Fixtures

The test fixtures in `conftest.py` are environment-aware and will adapt based on your configuration:

```python
@pytest.fixture(scope="module")
def client():
    """Create a TestClient for testing sync endpoints"""
    # Configure testing environment
    Config.TESTING = True
    Config.USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"
    Config.MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

    # Set up test token for all requests
    test_token = "test-jwt-token"

    # Create test client with appropriate configuration
    app = get_application()
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {test_token}"}
    return client
```

This approach allows tests to work properly in both mock and real modes without code changes.
