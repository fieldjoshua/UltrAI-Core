# Ultra Test Index

This document provides a comprehensive index of all tests in the Ultra project, their purpose, status, and associated processes.

## Test Categories

The Ultra test suite is divided into several categories:

1. **Backend API Tests** - Tests for the backend API endpoints and services
2. **Orchestrator Tests** - Tests for the LLM orchestration system
3. **Authentication Tests** - Tests for authentication and authorization
4. **Rate Limiting Tests** - Tests for rate limiting functionality
5. **Integration Tests** - End-to-end integration tests
6. **Unit Tests** - Isolated tests for specific components
7. **Performance Tests** - Tests for performance and scalability

## Backend API Tests

| Test Name | Location | Description | Status | Process |
|-----------|----------|-------------|--------|---------|
| `test_health_endpoint.py` | `/backend/tests/` | Tests the health check endpoint functionality | ✅ Active | CI, Pre-deploy |
| `test_analyze_endpoint.py` | `/backend/tests/` | Tests the analysis endpoint for processing text | ✅ Active | CI, Pre-deploy |
| `test_available_models_endpoint.py` | `/backend/tests/` | Tests the endpoint returning available LLM models | ✅ Active | CI, Pre-deploy |
| `test_llm_request_endpoint.py` | `/backend/tests/` | Tests the direct LLM request endpoint | ✅ Active | CI, Pre-deploy |
| `test_api.py` | `/backend/tests/` | Tests general API functionality and error handling | ✅ Active | CI |
| `test_document_upload.py` | `/backend/tests/` | Tests the document upload functionality | ⚠️ Incomplete | Manual |

## Authentication Tests

| Test Name | Location | Description | Status | Process |
|-----------|----------|-------------|--------|---------|
| `test_jwt_utils.py` | `/backend/tests/` | Tests JWT token creation, validation, and security features | ✅ Active | CI |
| `test_auth_edge_cases.py` | `/backend/tests/` | Tests authentication edge cases and security aspects | ✅ Active | CI |
| `test_auth_endpoints.py` | `/backend/tests/` | Tests authentication endpoints (login, register, etc.) | ✅ Active | CI |
| `test_e2e_auth_workflow.py` | `/backend/tests/` | Tests complete authentication workflow | ✅ Active | CI |
| `test_security.py` | `/` | Tests security-related aspects of the application | ⚠️ Incomplete | Manual |

## Rate Limiting Tests

| Test Name | Location | Description | Status | Process |
|-----------|----------|-------------|--------|---------|
| `test_rate_limit_service.py` | `/backend/tests/` | Tests rate limiting service functionality | ✅ Active | CI |
| `test_rate_limit_middleware.py` | `/backend/tests/` | Tests rate limiting middleware integration | ✅ Active | CI |

## Orchestrator Tests

| Test Name | Location | Description | Status | Process |
|-----------|----------|-------------|--------|---------|
| `test_basic_orchestrator.py` | `/` | Tests basic orchestrator functionality | ✅ Active | Manual |
| `test_orchestrator.py` | `/` | Tests standard orchestrator functionality | ✅ Active | CI |
| `test_orchestrator_with_real_apis.py` | `/` | Tests orchestrator with actual API connections | ⚠️ Optional | Manual |
| `test_real_orchestrator.py` | `/` | Tests production orchestrator configuration | ⚠️ Optional | Pre-deploy |

## Integration Tests

| Test Name | Location | Description | Status | Process |
|-----------|----------|-------------|--------|---------|
| `test_e2e_analysis_flow.py` | `/backend/tests/` | Tests the complete analysis flow from upload to results | ✅ Active | CI |
| `test_health_check.py` | `/` | Tests the complete health check system | ✅ Active | CI, Pre-deploy |
| `test_docker_modelrunner.py` | `/` | Tests the Docker ModelRunner integration | ⚠️ Incomplete | Manual |

## Test Runners

| Runner Name | Location | Description | Usage |
|-------------|----------|-------------|-------|
| `run_tests.sh` | `/backend/tests/` | Runs all backend tests with proper environment setup | `./backend/tests/run_tests.sh` |
| `run_tests.sh` | `/scripts/` | Runs project-wide tests with CI configuration | `./scripts/run_tests.sh` |
| `run_enhanced_test.py` | `/` | Runs tests with enhanced reporting | `python run_enhanced_test.py` |
| `run_factual_test.py` | `/` | Runs tests focused on factual correctness | `python run_factual_test.py` |
| `run_modular_test.py` | `/` | Runs tests in a modular fashion | `python run_modular_test.py` |

## Test Coverage Summary

| Component | Test Coverage | Status |
|-----------|---------------|--------|
| API Endpoints | 6/6 critical endpoints (100%) | ✅ Complete |
| Core Functionality | 6/6 critical flows (100%) | ✅ Complete |
| JWT Utilities | ~85% | ✅ Complete |
| Authentication Routes | ~75% | ✅ Complete |
| Rate Limiting | ~90% | ✅ Complete |
| Document Analysis | ~80% | ✅ Complete |
| Orchestrator | ~70% | ⚠️ In Progress |

## Test Status Legend

- ✅ **Active**: Test is fully implemented and actively maintained
- ⚠️ **Incomplete**: Test is partially implemented or needs updates
- ❌ **Failing**: Test is implemented but currently failing
- 🔄 **In Progress**: Test is being actively developed
- ⏸️ **Deprecated**: Test is no longer maintained/relevant

## Test Process Legend

- **CI**: Run in continuous integration pipeline
- **Pre-deploy**: Run before deployment to production
- **Manual**: Run manually by developers when necessary
- **All**: Run in all contexts

## Test Fixtures

The project provides several test fixtures in `conftest.py` files:

1. **Client Fixtures**: `client()`, `test_client()`, `async_client()`
2. **Environment Fixtures**: `mock_environment()`, `mock_env_vars()`, `mock_settings()`
3. **Data Fixtures**: `test_document_file()`, `sample_content()`
4. **Service Fixtures**: `mock_llm_service()`

## Future Test Plans

1. Increase test coverage for document analysis flow to 85%+
2. Implement comprehensive CI pipeline with GitHub Actions
3. Add performance testing suite for high-load scenarios
4. Enhance security testing with dedicated security test suite
