# Integration Tests

Comprehensive integration testing suite for Ultra LLM Orchestrator.

## Structure

```
integration_tests/
├── api/          # API endpoint tests
├── e2e/          # End-to-end user flow tests
├── fixtures/     # Test data and mocks
├── infrastructure/  # Docker and service configs
├── performance/  # Load and performance tests
├── utils/        # Test helpers and utilities
├── config.py     # Test configuration
├── pytest.ini    # Pytest configuration
└── README.md     # This file
```

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start test infrastructure:

```bash
docker-compose -f infrastructure/docker-compose.test.yml up -d
```

3. Run tests:

```bash
# All tests
pytest

# Specific category
pytest -m smoke
pytest -m auth
pytest -m integration

# Specific test file
pytest api/test_auth_endpoints.py
```

## Test Categories

### Smoke Tests (`-m smoke`)

Quick tests to verify basic functionality:

- Health endpoints
- Basic authentication
- Simple analysis request

### Authentication Tests (`-m auth`)

- User registration
- Login/logout
- Token management
- Permissions

### API Tests (`-m api`)

- Document upload
- Analysis requests
- Result retrieval
- Error handling

### Integration Tests (`-m integration`)

- Complete user flows
- Multi-service interactions
- LLM provider fallback
- Cache behavior

### Performance Tests (`-m performance`)

- Load testing
- Stress testing
- Spike testing
- Large document processing

### Security Tests (`-m security`)

- Authentication bypass attempts
- Authorization checks
- Input validation
- Rate limiting

### Resilience Tests (`-m resilience`)

- Service recovery
- Circuit breaker
- Retry mechanisms
- Graceful degradation

## Environment Configuration

Set test environment:

```bash
export TEST_ENV=local     # Default
export TEST_ENV=docker    # Docker environment
export TEST_ENV=staging   # Staging environment
export TEST_ENV=production  # Production (careful!)
```

## Test Profiles

Choose test intensity:

```bash
# Small profile (quick tests)
pytest --profile=small

# Medium profile (default)
pytest --profile=medium

# Large profile (comprehensive)
pytest --profile=large

# Stress profile (extreme load)
pytest --profile=stress
```

## Performance Testing

### Load Testing with Locust

```bash
# Start Locust UI
cd performance
locust -f locustfile.py --host=http://localhost:8087

# Headless mode
locust -f locustfile.py --host=http://localhost:8087 \
  --users=100 --spawn-rate=10 --run-time=5m --headless
```

### Custom Load Scenarios

```python
# Use async load tester
from utils.async_helpers import AsyncLoadTester

async def test_ramp_up():
    tester = AsyncLoadTester(client)
    await tester.ramp_up(
        endpoint="/api/analyze",
        start_users=1,
        end_users=100,
        duration=300
    )
    report = tester.get_report()
```

## E2E Testing with Cypress

```bash
# Run Cypress tests
cd e2e
cypress run

# Interactive mode
cypress open
```

## Test Data Management

### Using Data Factory

```python
from utils.data_factory import TestDataFactory

# Create test user
user = TestDataFactory.create_user_data()

# Create test document
document = TestDataFactory.create_document_data()

# Create complete scenario
scenario = ScenarioDataFactory.create_authentication_flow()
```

## Writing New Tests

### Basic Test Structure

```python
import pytest
from utils.test_helpers import APIClient, TestUser

@pytest.mark.auth
class TestAuthentication:
    def test_user_registration(self, api_client: APIClient):
        response = api_client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "Test123!@#"
        })
        assert response.status_code == 201
```

### Async Test

```python
import pytest
from utils.async_helpers import AsyncAPIClient

@pytest.mark.asyncio
async def test_concurrent_requests(async_client: AsyncAPIClient):
    tasks = [
        async_client.get("/api/health")
        for _ in range(10)
    ]
    responses = await asyncio.gather(*tasks)
    assert all(r.status == 200 for r in responses)
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run Integration Tests
  run: |
    docker-compose -f integration_tests/infrastructure/docker-compose.test.yml up -d
    pytest integration_tests -m "not slow" --junit-xml=test-results.xml
    docker-compose -f integration_tests/infrastructure/docker-compose.test.yml down
```

### Generate Reports

```bash
# Coverage report
pytest --cov=. --cov-report=html

# Allure report
pytest --alluredir=./allure-results
allure generate allure-results --clean -o allure-report
```

## Debugging

### Verbose Output

```bash
pytest -vv -s
```

### Debug Failed Tests

```bash
pytest --pdb  # Drop into debugger on failure
pytest --lf   # Run last failed tests
pytest --ff   # Run failed tests first
```

### Capture Logs

```bash
pytest --log-cli-level=DEBUG
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Data Cleanup**: Use fixtures for setup/teardown
3. **Mock External Services**: Use mock LLM service for consistency
4. **Parameterized Tests**: Test multiple scenarios efficiently
5. **Async Testing**: Use asyncio for concurrent scenarios
6. **Performance Baselines**: Track metrics over time
7. **Environment Parity**: Keep test env close to production

## Troubleshooting

### Service Not Available

```bash
# Check service health
curl http://localhost:8087/api/health

# Check logs
docker logs integration_tests_test-app_1
```

### Database Connection Issues

```bash
# Reset test database
docker-compose exec test-db psql -U ultra_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Port Conflicts

```bash
# Find process using port
lsof -i :8087

# Kill process
kill -9 <PID>
```

### Test Timeouts

```python
# Increase timeout for specific test
@pytest.mark.timeout(600)
def test_long_running_operation():
    pass
```

## Phase 1 Implementation Status

✅ Test planning and scenario definition
✅ Infrastructure setup (Docker Compose)
✅ Test utilities and helpers
✅ Data factories
✅ Configuration management
✅ Pytest setup
✅ Documentation

Next: Phase 2 - Core API Test Implementation
