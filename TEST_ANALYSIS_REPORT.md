# Test Suite Analysis Report

Total test files: 62

## Test Categories

- e2e: 3 files
- integration: 5 files
- live: 3 files
- production: 1 files
- unit: 26 files
- unknown: 24 files

## Potential Duplicates

Found 21 potential duplicate groups:


### module_services.auth_service
- /Users/joshuafield/Documents/Ultra/tests/e2e/test_cache_in_orchestration.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_cache_redis_integration.py
- /Users/joshuafield/Documents/Ultra/tests/test_auth_rate_limit.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_auth_service.py

### module_services.cache_service
- /Users/joshuafield/Documents/Ultra/tests/e2e/test_cache_in_orchestration.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_cache_redis_integration.py
- /Users/joshuafield/Documents/Ultra/tests/test_api_failure_handler.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_cache_service.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_cache_service_comprehensive.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_health_service.py

### module_app
- /Users/joshuafield/Documents/Ultra/tests/e2e/test_cache_in_orchestration.py
- /Users/joshuafield/Documents/Ultra/tests/e2e/test_e2e_financial_flow.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_cache_redis_integration.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_health_integration.py
- /Users/joshuafield/Documents/Ultra/tests/test_auth_rate_limit.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_auth_orchestrator_protection.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_streaming_orchestration.py

### module_database.connection
- /Users/joshuafield/Documents/Ultra/tests/integration/test_cache_redis_integration.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_health_service.py

### module_database.models.user
- /Users/joshuafield/Documents/Ultra/tests/integration/test_cache_redis_integration.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_database_integration.py
- /Users/joshuafield/Documents/Ultra/tests/test_auth_rate_limit.py
- /Users/joshuafield/Documents/Ultra/tests/test_rate_limit_service_logic.py

### module_utils.health_check
- /Users/joshuafield/Documents/Ultra/tests/integration/test_correct_endpoints.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_health_check_behavior.py

### module_main
- /Users/joshuafield/Documents/Ultra/tests/integration/test_correct_endpoints.py
- /Users/joshuafield/Documents/Ultra/tests/production/test_network_and_orchestrator.py

### module_database.repositories.user
- /Users/joshuafield/Documents/Ultra/tests/integration/test_database_integration.py
- /Users/joshuafield/Documents/Ultra/tests/integration/test_database_integration_mock.py

### module_config
- /Users/joshuafield/Documents/Ultra/tests/test_auth_rate_limit.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_auth_orchestrator_protection.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_service_unavailable.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_single_model_fallback.py
- /Users/joshuafield/Documents/Ultra/tests/unit/test_streaming_orchestration.py

### module_services.rate_limit_service
- /Users/joshuafield/Documents/Ultra/tests/test_auth_rate_limit.py
- /Users/joshuafield/Documents/Ultra/tests/test_rate_limit_service_logic.py

## Weak Tests

Found 15 tests with weak assertions:

- /Users/joshuafield/Documents/Ultra/tests/live/test_live_providers.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/test_prompt_service.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/test_prompt_templates.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/test_rate_limit_service.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/test_rate_limit_service_logic.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/test_service_instantiation.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/unit/test_auth_orchestrator_protection.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/unit/test_billing_service.py (low_assertions)
- /Users/joshuafield/Documents/Ultra/tests/unit/test_billing_service.py (no_assertions)
- /Users/joshuafield/Documents/Ultra/tests/unit/test_budget_service.py (low_assertions)

## Mock Usage

- 31/62 files use mocks