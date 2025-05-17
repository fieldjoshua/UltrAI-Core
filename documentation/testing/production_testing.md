# Production Environment Testing

This document explains how to test the Ultra application in a production environment configuration.

## Overview

The production testing ensures that Ultra can run with real services instead of mock mode. The testing framework is designed to be resilient to different environments and handles scenarios where the API server might not be running.

## Testing Process

The production testing process involves:

1. Setting up a clean production test environment
2. Validating core functionality without mock services
3. Testing API endpoints for production readiness
4. Verifying authentication and authorization systems
5. Testing with real LLM service providers when API keys are available

## Running Tests

To run production readiness tests:

```bash
# Make sure you're in the project root directory
cd /path/to/Ultra

# Run the production test script
bash scripts/test_production.sh
```

## Test Environment

The test script creates a temporary environment file (.env.test_production) with production-ready settings. This file:

- Sets `ENVIRONMENT=production`
- Disables mock mode (`USE_MOCK=false`, `MOCK_MODE=false`)
- Configures authentication settings for testing
- Sets up necessary API paths and keys

## Special Test Headers

Tests use the `X-Test-Mode: true` header to bypass authentication in production mode. This allows testing API endpoints without valid tokens during automated testing.

## Endpoints Tested

The following endpoints are tested in production mode:

- `/api/health` - Basic health check endpoint
- `/api/analyze` - LLM orchestration endpoint

## Troubleshooting

If tests fail:

1. **Server Not Running**: Most tests will be skipped if the API server isn't running. Start it with:

   ```bash
   python -m uvicorn backend.app:app --reload --port 8085
   ```

2. **Auth Middleware Issues**: If authentication fails, check that the middleware is properly configured to handle test headers.

3. **Missing API Keys**: Some tests will report issues if real LLM API keys aren't configured. This is expected and doesn't necessarily indicate a problem.

## How to Add New Production Tests

To add a new production test:

1. Create a new test file in `backend/tests/` directory
2. Ensure tests can bypass authentication with the `X-Test-Mode: true` header
3. Add timeout handling to prevent tests from hanging
4. Handle both server-running and server-not-running scenarios gracefully
5. Add the test to the `test_production.sh` script

## Environment Variables

The test environment includes these critical variables:

- `ENVIRONMENT=production`
- `TESTING=true`
- `USE_MOCK=false`
- `MOCK_MODE=false`
- `API_KEY_ENCRYPTION_KEY` - Test encryption key
- `SECRET_KEY` - Test secret key
- `JWT_SECRET` - Test JWT secret

## Production vs Development Testing

The main differences between production and development testing:

1. **Authentication**: Production tests require proper auth headers
2. **Real Services**: Production tests use real external services
3. **Mock Bypass**: Development tests can run with mock services
4. **API Keys**: Production tests need actual API keys for full functionality
