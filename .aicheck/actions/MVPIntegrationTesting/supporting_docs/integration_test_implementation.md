# Integration Test Implementation Details

## Overview

This document provides implementation details for the Ultra MVP integration tests.

## Test Infrastructure

### Docker Environment

- Test database (PostgreSQL 15)
- Test cache (Redis 7)
- Mock LLM service
- Test application instance
- Test runners (Cypress, pytest)

### Service Configuration

All services are containerized for consistency:

- Database: Port 5433 (test) vs 5432 (production)
- Redis: Port 6380 (test) vs 6379 (production)
- API: Port 8087 (test) vs 8085 (production)
- Mock LLM: Port 8086

## Test Organization

### Directory Structure

```
integration_tests/
├── api/          # API endpoint tests
├── e2e/          # End-to-end UI tests
├── performance/  # Load and stress tests
├── fixtures/     # Test data and mocks
├── utils/        # Test helpers
└── infrastructure/  # Docker configs
```

### Test Categories

- `smoke`: Quick basic functionality tests
- `auth`: Authentication and authorization
- `api`: API endpoint validation
- `integration`: Cross-component tests
- `performance`: Load and stress tests
- `security`: Security vulnerability tests

## Implementation Guidelines

### Test Isolation

- Each test runs in isolated transaction
- No shared state between tests
- Automatic cleanup after each test

### Data Management

- Use factories for consistent test data
- Avoid hardcoded test values
- Reset database between test suites

### Mock Strategies

- Mock external services (LLM providers)
- Use realistic response delays
- Simulate common failure scenarios

### Performance Considerations

- Run tests in parallel when possible
- Use pytest-xdist for distribution
- Optimize fixture creation

## CI/CD Integration

### GitHub Actions

- Run smoke tests on every PR
- Full suite on merge to main
- Nightly extended test runs

### Test Reporting

- JUnit XML for CI integration
- HTML reports for debugging
- Performance metrics tracking

## Debugging Failed Tests

### Local Reproduction

```bash
# Run specific test
pytest integration_tests/api/test_auth.py::test_login -v

# Run with debugging
pytest --pdb integration_tests/api/test_auth.py

# Run last failed
pytest --lf
```

### Common Issues

1. Port conflicts - check running services
2. Database state - ensure clean reset
3. Timing issues - use proper waits
4. Environment differences - check config

## Best Practices

1. Keep tests independent and idempotent
2. Use descriptive test names
3. Avoid time-dependent assertions
4. Mock external dependencies
5. Test both success and failure paths
6. Document complex test scenarios
7. Maintain test performance
