# UltraAI Test Suite Inventory

**Total Tests:** 322

**Generated:** Tue Sep 30 02:54:10 PDT 2025

## Summary

| Category | Count |
|----------|-------|
| Core | 54 |
| E2E | 13 |
| Integration | 44 |
| Live | 3 |
| Production | 1 |
| Unit | 207 |

| Module | Count |
|--------|-------|
| 1. Core Synthesis | 14 |
| 11. Model Registry | 4 |
| 12. Documents | 5 |
| 13. Analysis | 6 |
| 14. API Endpoints | 2 |
| 15. Streaming | 7 |
| 16. Configuration | 42 |
| 17. Database | 6 |
| 18. UI/Frontend | 1 |
| 2. LLM Providers | 48 |
| 21. Miscellaneous | 41 |
| 3. Authentication | 35 |
| 5. Rate Limiting | 44 |
| 6. Caching | 34 |
| 7. Health & Monitoring | 17 |
| 8. Prompts & Templates | 16 |

## Complete Test Inventory

| # | Category | Module | File | Test Name | Description | Parameters/Fixtures | Markers |
|---|----------|--------|------|-----------|-------------|---------------------|----------|
| 1 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_orchestration_...` | Test that orchestration properly caches responses | HTTP client, Cache service service, Auth... | none |
| 2 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_orchestration_...` | Test that different parameters generate different cache... | HTTP client, Cache service service, Auth... | none |
| 3 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_orchestration_...` | Test orchestration when caching is disabled | HTTP client, Cache service service, Auth... | none |
| 4 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_cache_ttl_in_o...` | Test that cached orchestration responses expire | HTTP client, Cache service service, Monk... | none |
| 5 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_cache_clear_af...` | Test that clearing cache affects orchestration | HTTP client, Cache service service, Auth... | none |
| 6 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `TestCacheInOrchestration::test_cache_pattern_...` | Test pattern-based cache clearing for orchestration | HTTP client, Cache service service, Auth... | none |
| 7 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_orchestration_caching_workflow` | Test that orchestration properly caches responses | HTTP client, Cache service service, Auth... | none |
| 8 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_orchestration_cache_invalidation_on_diff...` | Test that different parameters generate different cache... | HTTP client, Cache service service, Auth... | none |
| 9 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_orchestration_without_caching` | Test orchestration when caching is disabled | HTTP client, Cache service service, Auth... | none |
| 10 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_cache_ttl_in_orchestration` | Test that cached orchestration responses expire | HTTP client, Cache service service, Monk... | none |
| 11 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_cache_clear_affects_orchestration` | Test that clearing cache affects orchestration | HTTP client, Cache service service, Auth... | none |
| 12 | E2E | 1. Core Synthesis | `test_cache_in_orchestration.py` | `test_cache_pattern_clear_orchestration` | Test pattern-based cache clearing for orchestration | HTTP client, Cache service service, Auth... | none |
| 13 | E2E | 1. Core Synthesis | `test_web_orchestrator_ui.py` | `test_ultra_synthesis_via_ui` | Drive the web interface and ensure Ultra-Synthesis retu... | page | e2e, playwright |
| 14 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_app` | Create test application with auth enabled | None | none |
| 15 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_public_endpoints_no_...` | Test that public endpoints don't require authentication | HTTP client | none |
| 16 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_admin_endpoints_requ...` | Test that admin endpoints require authentication | HTTP client | none |
| 17 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_debug_endpoints_requ...` | Test that debug endpoints require authentication | HTTP client | none |
| 18 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_valid_jwt_token_allo...` | Test that valid JWT token allows access to protected en... | Mocked expired, Mocked decode, Mocked ge... | none |
| 19 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_valid_api_key_allows...` | Test that valid API key allows access to protected endp... | Mocked verify api key, HTTP client, Mock... | none |
| 20 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthMiddleware::test_invalid_auth_rejecte...` | Test that invalid authentication is rejected | HTTP client | none |
| 21 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestRateLimiting::test_rate_limit_headers_add...` | Test that rate limit headers are added to responses | Mocked redis, HTTP client | none |
| 22 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestRateLimiting::test_rate_limit_exceeded_re...` | Test that exceeding rate limit returns 429 | Mocked redis, HTTP client | none |
| 23 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestRateLimiting::test_per_user_rate_limiting` | Test that rate limiting is per-user when authenticated | Mocked expired, Mocked decode, Mocked ge... | none |
| 24 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestRateLimiting::test_ip_based_rate_limiting...` | Test that rate limiting is IP-based for unauthenticated... | Mocked redis, HTTP client | none |
| 25 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestRateLimiting::test_rate_limiting_disabled...` | Test that rate limiting is disabled when Redis is unava... | Mocked redis, HTTP client | none |
| 26 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthRateLimitIntegration::test_authentica...` | Test that authenticated users get rate limits based on ... | Mocked expired, Mocked decode, Mocked re... | none |
| 27 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthRateLimitIntegration::test_env_variab...` | Test that ENABLE_AUTH and ENABLE_RATE_LIMIT env variabl... | Monkeypatch fixture | none |
| 28 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `TestAuthRateLimitIntegration::test_rate_limit...` | Test that TEST_RATE_LIMIT_TIER env var overrides tier i... | Mocked redis, Monkeypatch fixture | none |
| 29 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_public_endpoints_no_auth` | Test that public endpoints don't require authentication | HTTP client | none |
| 30 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_admin_endpoints_require_auth` | Test that admin endpoints require authentication | HTTP client | none |
| 31 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_debug_endpoints_require_auth` | Test that debug endpoints require authentication | HTTP client | none |
| 32 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_valid_jwt_token_allows_access` | Test that valid JWT token allows access to protected en... | Mocked expired, Mocked decode, Mocked ge... | none |
| 33 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_valid_api_key_allows_access` | Test that valid API key allows access to protected endp... | Mocked verify api key, HTTP client, Mock... | none |
| 34 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_invalid_auth_rejected` | Test that invalid authentication is rejected | HTTP client | none |
| 35 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_rate_limit_headers_added` | Test that rate limit headers are added to responses | Mocked redis, HTTP client | none |
| 36 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_rate_limit_exceeded_returns_429` | Test that exceeding rate limit returns 429 | Mocked redis, HTTP client | none |
| 37 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_per_user_rate_limiting` | Test that rate limiting is per-user when authenticated | Mocked expired, Mocked decode, Mocked ge... | none |
| 38 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_ip_based_rate_limiting_for_unauthenticat...` | Test that rate limiting is IP-based for unauthenticated... | Mocked redis, HTTP client | none |
| 39 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_rate_limiting_disabled_when_redis_unavai...` | Test that rate limiting is disabled when Redis is unava... | Mocked redis, HTTP client | none |
| 40 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_authenticated_user_gets_tier_based_limit...` | Test that authenticated users get rate limits based on ... | Mocked expired, Mocked decode, Mocked re... | none |
| 41 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_env_variable_controls` | Test that ENABLE_AUTH and ENABLE_RATE_LIMIT env variabl... | Monkeypatch fixture | none |
| 42 | Integration | 3. Authentication | `test_auth_rate_limit.py` | `test_rate_limit_tier_override_in_testing` | Test that TEST_RATE_LIMIT_TIER env var overrides tier i... | Mocked redis, Monkeypatch fixture | none |
| 43 | Integration | 6. Caching | `test_cache_redis_integration.py` | `TestCacheRouteIntegration::test_cache_stats_e...` | Test /cache/stats endpoint | HTTP client, Mocked cache service | none |
| 44 | Integration | 6. Caching | `test_cache_redis_integration.py` | `TestCacheRouteIntegration::test_cache_health_...` | Test /cache/health endpoint | HTTP client, Mocked cache service | none |
| 45 | Integration | 6. Caching | `test_cache_redis_integration.py` | `TestCacheRouteIntegration::test_cache_clear_e...` | Test /cache/clear endpoint | HTTP client, Mocked cache service | none |
| 46 | Integration | 6. Caching | `test_cache_redis_integration.py` | `test_cache_stats_endpoint` | Test /cache/stats endpoint | HTTP client, Mocked cache service | none |
| 47 | Integration | 6. Caching | `test_cache_redis_integration.py` | `test_cache_health_endpoint` | Test /cache/health endpoint | HTTP client, Mocked cache service | none |
| 48 | Integration | 6. Caching | `test_cache_redis_integration.py` | `test_cache_clear_endpoint` | Test /cache/clear endpoint | HTTP client, Mocked cache service | none |
| 49 | Integration | 17. Database | `test_database_integration.py` | `test_user_creation_and_retrieval` | User creation and retrieval | Database connection session | integration |
| 50 | Integration | 17. Database | `test_database_integration.py` | `test_transaction_rollback` | Transaction rollback | Database connection session | integration |
| 51 | Integration | 17. Database | `test_database_integration_mock.py` | `test_user_creation_and_retrieval` | Test user creation and retrieval through repository. | None | integration |
| 52 | Integration | 17. Database | `test_database_integration_mock.py` | `test_transaction_rollback` | Test transaction rollback behavior. | None | integration |
| 53 | Integration | 17. Database | `test_database_integration_mock.py` | `test_analysis_creation` | Test creating an analysis record. | None | integration |
| 54 | Integration | 17. Database | `test_database_integration_mock.py` | `test_document_processing` | Test document creation and chunk processing. | None | integration |
| 55 | Integration | 7. Health & Monitoring | `test_health_integration.py` | `test_health_endpoint_basic` | Test the /api/health endpoint returns status and correc... | HTTP client | integration |
| 56 | Integration | 7. Health & Monitoring | `test_health_integration.py` | `test_health_services_endpoint` | Test the /api/health/services endpoint returns correct ... | HTTP client | integration |
| 57 | Integration | 7. Health & Monitoring | `test_health_integration.py` | `test_health_endpoints_not_caught_by_spa` | Test that health endpoints are registered before SPA ca... | HTTP client | integration |
| 58 | Live | 14. API Endpoints | `test_demo_endpoints.py` | `test_demo_health_available_models` | Demo health available models | None | live |
| 59 | Live | 14. API Endpoints | `test_demo_endpoints.py` | `test_demo_models_providers_summary` | Demo models providers summary | None | live |
| 60 | Live | 18. UI/Frontend | `test_live_online_ui.py` | `test_live_ultra_synthesis_via_ui` | Simulate a real user running an analysis through the UI... | page | live_online, playwright |
| 61 | Production | 1. Core Synthesis | `test_network_and_orchestrator.py` | `test_orchestrator_pipeline_openai` | Run the full orchestrator pipeline against OpenAI with ... | None | production |
| 62 | Core | 7. Health & Monitoring | `test_staging_big3_health.py` | `test_providers_summary_all_big3_configured` | Providers summary all big3 configured | None | none |
| 63 | Core | 7. Health & Monitoring | `test_staging_big3_health.py` | `test_at_least_one_healthy_model_per_big3` | At least one healthy model per big3 | None | none |
| 64 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_configuration_l...` | Test that configuration loads without errors | None | none |
| 65 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_endpoints_confi...` | Test that endpoints are properly configured | None | none |
| 66 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_mock_configurat...` | Test that mock settings are correct for mode | None | none |
| 67 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_timeout_configu...` | Test timeout values are set appropriately | None | none |
| 68 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_skip_reasons` | Test that skip reasons are configured correctly | None | none |
| 69 | Core | 16. Configuration | `test_configuration_system.py` | `TestConfigurationSystem::test_environment_var...` | Test that required environment variables are set | None | none |
| 70 | Core | 16. Configuration | `test_configuration_system.py` | `test_pytest_working` | Basic test to ensure pytest is working | None | none |
| 71 | Core | 16. Configuration | `test_configuration_system.py` | `test_configuration_loads` | Test that configuration loads without errors | None | none |
| 72 | Core | 16. Configuration | `test_configuration_system.py` | `test_endpoints_configured` | Test that endpoints are properly configured | None | none |
| 73 | Core | 16. Configuration | `test_configuration_system.py` | `test_mock_configuration` | Test that mock settings are correct for mode | None | none |
| 74 | Core | 16. Configuration | `test_configuration_system.py` | `test_timeout_configuration` | Test timeout values are set appropriately | None | none |
| 75 | Core | 16. Configuration | `test_configuration_system.py` | `test_skip_reasons` | Test that skip reasons are configured correctly | None | none |
| 76 | Core | 16. Configuration | `test_configuration_system.py` | `test_environment_variables` | Test that required environment variables are set | None | none |
| 77 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestBaseAdapter::test_base_adapter_requires_a...` | Test that BaseAdapter requires an API key. | None | none |
| 78 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestBaseAdapter::test_base_adapter_stores_con...` | Test that BaseAdapter stores API key and model correctl... | None | none |
| 79 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestOpenAIAdapter::test_openai_adapter_initia...` | Test OpenAI adapter initialization. | None | none |
| 80 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestAnthropicAdapter::test_anthropic_adapter_...` | Test Anthropic adapter initialization. | None | none |
| 81 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestGeminiAdapter::test_gemini_adapter_initia...` | Test Gemini adapter initialization. | None | none |
| 82 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestHuggingFaceAdapter::test_huggingface_adap...` | Test HuggingFace adapter initialization. | None | none |
| 83 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_init...` | Test circuit breaker initializes in closed state. | None | none |
| 84 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_open...` | Test circuit breaker opens after failure threshold. | None | none |
| 85 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_half...` | Test circuit breaker transitions to half-open after tim... | None | none |
| 86 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestResilientLLMAdapter::test_metrics_trackin...` | Test metrics are properly tracked. | None | none |
| 87 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderConfigurations::test_openai_confi...` | Test OpenAI configuration. | None | none |
| 88 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderConfigurations::test_anthropic_co...` | Test Anthropic configuration. | None | none |
| 89 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderConfigurations::test_google_confi...` | Test Google configuration. | None | none |
| 90 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_base_adapter_requires_api_key` | Test that BaseAdapter requires an API key. | None | none |
| 91 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_base_adapter_stores_config` | Test that BaseAdapter stores API key and model correctl... | None | none |
| 92 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_openai_adapter_initialization` | Test OpenAI adapter initialization. | None | none |
| 93 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_anthropic_adapter_initialization` | Test Anthropic adapter initialization. | None | none |
| 94 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_gemini_adapter_initialization` | Test Gemini adapter initialization. | None | none |
| 95 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_huggingface_adapter_initialization` | Test HuggingFace adapter initialization. | None | none |
| 96 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_initialization` | Test circuit breaker initializes in closed state. | None | none |
| 97 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_opens_after_failures` | Test circuit breaker opens after failure threshold. | None | none |
| 98 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_half_open_after_timeout` | Test circuit breaker transitions to half-open after tim... | None | none |
| 99 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_metrics_tracking` | Test metrics are properly tracked. | None | none |
| 100 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_openai_config` | Test OpenAI configuration. | None | none |
| 101 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_anthropic_config` | Test Anthropic configuration. | None | none |
| 102 | Core | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_google_config` | Test Google configuration. | None | none |
| 103 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_register_and_get_template` | Register and get template | None | none |
| 104 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_list_templates_empty` | List templates empty | None | none |
| 105 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_render_template_success` | Render template success | None | none |
| 106 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_render_template_missing_strict` | Render template missing strict | None | none |
| 107 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_render_template_missing_not_strict` | Render template missing not strict | None | none |
| 108 | Core | 8. Prompts & Templates | `test_prompt_templates.py` | `test_load_templates_from_file` | Load templates from file | Temp path | none |
| 109 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_format` | Test that SSE events follow the standardized format. | None | none |
| 110 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_with_model_info` | Test SSE event with model and provider info. | None | none |
| 111 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_no_cost_fields` | Test that SSE events don't include cost fields. | None | none |
| 112 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_types` | Test all expected SSE event types. | None | none |
| 113 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_schema_validation` | Test that events conform to expected schema. | None | none |
| 114 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_event_order_contract` | Test expected event ordering for a successful pipeline. | None | none |
| 115 | Core | 15. Streaming | `test_sse_contract.py` | `test_sse_format_for_streaming` | Test SSE event formatting for streaming response. | None | none |
| 116 | Unit | 13. Analysis | `test_analysis_service.py` | `test_get_user_analyses` | Get user analyses | service | unit |
| 117 | Unit | 13. Analysis | `test_analysis_service.py` | `test_get_document_analyses_with_access` | Get document analyses with access | service | unit |
| 118 | Unit | 13. Analysis | `test_analysis_service.py` | `test_create_analysis_with_doc_check` | Create analysis with doc check | service | unit |
| 119 | Unit | 13. Analysis | `test_analysis_service.py` | `test_update_analysis_status_and_permission` | Update analysis status and permission | service | unit |
| 120 | Unit | 13. Analysis | `test_analysis_service.py` | `test_get_analysis_by_id_and_permission` | Get analysis by id and permission | service | unit |
| 121 | Unit | 13. Analysis | `test_analysis_service.py` | `test_get_pattern_stats` | Get pattern stats | service | unit |
| 122 | Unit | 11. Model Registry | `test_model_registry.py` | `test_register_and_create_instance` | Register and create instance | registry | none |
| 123 | Unit | 11. Model Registry | `test_model_registry.py` | `test_list_models_and_unregister` | List models and unregister | registry | none |
| 124 | Unit | 11. Model Registry | `test_model_registry.py` | `test_update_config_and_record_usage` | Update config and record usage | registry | none |
| 125 | Unit | 11. Model Registry | `test_model_registry.py` | `test_errors_on_invalid_operations` | Errors on invalid operations | registry | none |
| 126 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_placeholder_prompt_service` | Placeholder prompt service | None | none |
| 127 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_register_and_get_template` | Register and get template | prompt service | none |
| 128 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_register_duplicate_raises` | Register duplicate raises | prompt service | none |
| 129 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_update_template` | Update template | prompt service | none |
| 130 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_format_output_plain` | Format output plain | prompt service | none |
| 131 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_format_output_html` | Format output html | prompt service | none |
| 132 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_format_output_json` | Format output json | prompt service | none |
| 133 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_render_template_success` | Render template success | prompt service | none |
| 134 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_render_template_missing_var` | Render template missing var | prompt service | none |
| 135 | Unit | 8. Prompts & Templates | `test_prompt_service.py` | `test_render_template_invalid_var` | Render template invalid var | prompt service | none |
| 136 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_rate_limit_result_...` | Test RateLimitResult object properties | None | none |
| 137 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_check_rate_limit_f...` | Test rate limit check for first request | rate limit service, Mocked redis, Mocked... | none |
| 138 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_check_rate_limit_e...` | Test rate limit exceeded scenario | rate limit service, Mocked redis, Mocked... | none |
| 139 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_rate_limit_without...` | Test rate limiting when Redis is not available | rate limit service, Mocked request, Mock... | none |
| 140 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_categorize_request` | Test request categorization | rate limit service, Mocked request | none |
| 141 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_get_client_identif...` | Test client identifier generation with authenticated us... | rate limit service, Mocked request, Mock... | none |
| 142 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_get_client_identif...` | Test client identifier generation with IP address | rate limit service, Mocked request | none |
| 143 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_build_key` | Test Redis key generation | rate limit service | none |
| 144 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_tier_configuration` | Test tier configuration is properly set | None | none |
| 145 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `TestRateLimitService::test_get_limit_for_cate...` | Test getting limits for different categories | rate limit service | none |
| 146 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_rate_limit_result_properties` | Test RateLimitResult object properties | None | none |
| 147 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_check_rate_limit_first_request` | Test rate limit check for first request | rate limit service, Mocked redis, Mocked... | none |
| 148 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_check_rate_limit_exceeded` | Test rate limit exceeded scenario | rate limit service, Mocked redis, Mocked... | none |
| 149 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_rate_limit_without_redis` | Test rate limiting when Redis is not available | rate limit service, Mocked request, Mock... | none |
| 150 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_categorize_request` | Test request categorization | rate limit service, Mocked request | none |
| 151 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_get_client_identifier_with_user` | Test client identifier generation with authenticated us... | rate limit service, Mocked request, Mock... | none |
| 152 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_get_client_identifier_with_ip` | Test client identifier generation with IP address | rate limit service, Mocked request | none |
| 153 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_build_key` | Test Redis key generation | rate limit service | none |
| 154 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_tier_configuration` | Test tier configuration is properly set | None | none |
| 155 | Unit | 5. Rate Limiting | `test_rate_limit_service.py` | `test_get_limit_for_category` | Test getting limits for different categories | rate limit service | none |
| 156 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_get_window_s...` | Test window duration calculation for different interval... | interval, expected | none |
| 157 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_tier_limits_...` | Ensure TIER_LIMITS contains all subscription tiers | None | none |
| 158 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_default_tier...` | Verify default tier is FREE for new users | None | none |
| 159 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_tier_limit_p...` | Test that higher tiers have higher limits | None | none |
| 160 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_tier_interva...` | Test that tier intervals are properly configured | None | none |
| 161 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitConfiguration::test_endpoint_spe...` | Test endpoint-specific rate limits are properly configu... | None | none |
| 162 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitKeyGeneration::test_rate_limit_k...` | Test the format of rate limit keys | None | none |
| 163 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitKeyGeneration::test_rate_limit_k...` | Test that rate limit keys are unique per user/endpoint/... | None | none |
| 164 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitBusinessRules::test_free_tier_re...` | Test FREE tier has appropriate restrictions | None | none |
| 165 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitBusinessRules::test_enterprise_t...` | Test ENTERPRISE tier has generous limits | None | none |
| 166 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitBusinessRules::test_rate_limit_h...` | Test rate limit result properties | None | none |
| 167 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `TestRateLimitBusinessRules::test_rate_limit_r...` | Test rate limit result when request is blocked | None | none |
| 168 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_get_window_seconds` | Test window duration calculation for different interval... | interval, expected | none |
| 169 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_tier_limits_completeness` | Ensure TIER_LIMITS contains all subscription tiers | None | none |
| 170 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_default_tier_is_free` | Verify default tier is FREE for new users | None | none |
| 171 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_tier_limit_progression` | Test that higher tiers have higher limits | None | none |
| 172 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_tier_interval_configuration` | Test that tier intervals are properly configured | None | none |
| 173 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_endpoint_specific_limits` | Test endpoint-specific rate limits are properly configu... | None | none |
| 174 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_rate_limit_key_format` | Test the format of rate limit keys | None | none |
| 175 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_rate_limit_key_uniqueness` | Test that rate limit keys are unique per user/endpoint/... | None | none |
| 176 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_free_tier_restrictions` | Test FREE tier has appropriate restrictions | None | none |
| 177 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_enterprise_tier_allowances` | Test ENTERPRISE tier has generous limits | None | none |
| 178 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_rate_limit_headers_format` | Test rate limit result properties | None | none |
| 179 | Unit | 5. Rate Limiting | `test_rate_limit_service_logic.py` | `test_rate_limit_result_for_blocked_request` | Test rate limit result when request is blocked | None | none |
| 180 | Unit | 16. Configuration | `test_service_instantiation.py` | `test_instantiate_service_class` | Smoke test: attempt to instantiate service class with M... | module name, class name, cls | none |
| 181 | Unit | 3. Authentication | `test_auth_service.py` | `test_create_and_verify_access_token` | Create and verify access token | None | none |
| 182 | Unit | 3. Authentication | `test_auth_service.py` | `test_create_and_verify_refresh_token` | Create and verify refresh token | None | none |
| 183 | Unit | 3. Authentication | `test_auth_service.py` | `test_verify_invalid_tokens` | Verify invalid tokens | None | none |
| 184 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheKeyGeneration::test_cache_key_simple...` | Test cache key generation with simple types | None | none |
| 185 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheKeyGeneration::test_cache_key_comple...` | Test cache key generation with complex types | None | none |
| 186 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheKeyGeneration::test_cache_key_none_h...` | Test cache key handles None values | None | none |
| 187 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_initialization_without...` | Test cache initializes correctly when Redis unavailable | Monkeypatch fixture | none |
| 188 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_memory_cache_operation...` | Test memory cache basic operations | Cache service memory only | none |
| 189 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_memory_cache_ttl` | Test memory cache TTL functionality | Cache service memory only | none |
| 190 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_clear_pattern` | Test pattern-based cache clearing | Cache service memory only | none |
| 191 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_get_stats` | Test cache statistics tracking | Cache service memory only | none |
| 192 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheService::test_cleanup_memory_cache` | Test memory cache cleanup of expired entries | Cache service memory only | none |
| 193 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheDecorator::test_cached_sync_function` | Test @cached decorator with sync function | Cache service service, Monkeypatch fixtu... | none |
| 194 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheDecorator::test_cached_with_ttl` | Test @cached decorator with TTL | Cache service service, Monkeypatch fixtu... | none |
| 195 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheSingleton::test_get_cache_service_si...` | Test get_cache_service returns same instance | None | none |
| 196 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheIntegrationScenarios::test_orchestra...` | Test caching pattern used in orchestration service | Cache service service | none |
| 197 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `TestCacheIntegrationScenarios::test_cache_siz...` | Test cache behavior with many entries | Cache service service | none |
| 198 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cache_key_simple_types` | Test cache key generation with simple types | None | none |
| 199 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cache_key_complex_types` | Test cache key generation with complex types | None | none |
| 200 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cache_key_none_handling` | Test cache key handles None values | None | none |
| 201 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_initialization_without_redis` | Test cache initializes correctly when Redis unavailable | Monkeypatch fixture | none |
| 202 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_memory_cache_operations` | Test memory cache basic operations | Cache service memory only | none |
| 203 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_memory_cache_ttl` | Test memory cache TTL functionality | Cache service memory only | none |
| 204 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_clear_pattern` | Test pattern-based cache clearing | Cache service memory only | none |
| 205 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_get_stats` | Test cache statistics tracking | Cache service memory only | none |
| 206 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cleanup_memory_cache` | Test memory cache cleanup of expired entries | Cache service memory only | none |
| 207 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cached_sync_function` | Test @cached decorator with sync function | Cache service service, Monkeypatch fixtu... | none |
| 208 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cached_with_ttl` | Test @cached decorator with TTL | Cache service service, Monkeypatch fixtu... | none |
| 209 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_get_cache_service_singleton` | Test get_cache_service returns same instance | None | none |
| 210 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_orchestration_response_caching` | Test caching pattern used in orchestration service | Cache service service | none |
| 211 | Unit | 6. Caching | `test_cache_service_comprehensive.py` | `test_cache_size_limits` | Test cache behavior with many entries | Cache service service | none |
| 212 | Unit | 12. Documents | `test_document_processor.py` | `test_process_text_file` | Process text file | Temp path | none |
| 213 | Unit | 12. Documents | `test_document_processor.py` | `test_process_unknown_file_type` | Process unknown file type | None | none |
| 214 | Unit | 12. Documents | `test_document_service.py` | `test_get_user_documents` | Get user documents | service | none |
| 215 | Unit | 12. Documents | `test_document_service.py` | `test_get_document_by_id` | Get document by id | service | none |
| 216 | Unit | 12. Documents | `test_document_service.py` | `test_delete_document` | Delete document | service | none |
| 217 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `TestHealthCheckBehavior::test_skip_api_calls_...` | Test that health checks skip API calls when configured. | Monkeypatch fixture | unit |
| 218 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `TestHealthCheckBehavior::test_rate_limited_pr...` | Test that rate-limited providers don't cause degraded s... | Monkeypatch fixture | unit |
| 219 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `TestHealthCheckBehavior::test_all_providers_r...` | Test that all rate-limited providers still show as heal... | Monkeypatch fixture | unit |
| 220 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `TestHealthCheckBehavior::test_truly_unavailab...` | Test that truly unavailable providers cause degraded st... | Monkeypatch fixture | unit |
| 221 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `TestHealthCheckEndpoints::test_correct_endpoi...` | Document correct endpoint paths for health checks. | None | unit |
| 222 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `test_skip_api_calls_when_configured` | Test that health checks skip API calls when configured. | Monkeypatch fixture | unit |
| 223 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `test_rate_limited_providers_considered_health...` | Test that rate-limited providers don't cause degraded s... | Monkeypatch fixture | unit |
| 224 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `test_all_providers_rate_limited_still_healthy` | Test that all rate-limited providers still show as heal... | Monkeypatch fixture | unit |
| 225 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `test_truly_unavailable_providers_cause_degrad...` | Test that truly unavailable providers cause degraded st... | Monkeypatch fixture | unit |
| 226 | Unit | 7. Health & Monitoring | `test_health_check_behavior.py` | `test_correct_endpoint_paths` | Document correct endpoint paths for health checks. | None | unit |
| 227 | Unit | 7. Health & Monitoring | `test_health_service.py` | `test_get_health_simple` | Get health simple | None | none |
| 228 | Unit | 7. Health & Monitoring | `test_health_service.py` | `test_get_health_detailed` | Get health detailed | None | none |
| 229 | Unit | 3. Authentication | `test_jwt_secret_alias.py` | `test_jwt_secret_key_precedence` | Test that JWT_SECRET_KEY takes precedence over JWT_SECR... | None | none |
| 230 | Unit | 3. Authentication | `test_jwt_secret_alias.py` | `test_jwt_refresh_secret_fallback` | Test that refresh secret falls back to main secret + _R... | None | none |
| 231 | Unit | 3. Authentication | `test_jwt_secret_alias.py` | `test_jwt_missing_secret_raises_error` | Test that missing JWT secret raises ValueError | None | none |
| 232 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestBaseAdapter::test_mask_api_key` | Test API key masking for security | None | none |
| 233 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestBaseAdapter::test_base_adapter_properties` | Test BaseAdapter properties | None | none |
| 234 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestSharedHttpClient::test_shared_client_time...` | Test that CLIENT has correct timeout configuration | None | none |
| 235 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestSharedHttpClient::test_all_adapters_use_s...` | Test that all adapters use the shared CLIENT | None | none |
| 236 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_init...` | Test circuit breaker initializes in closed state | None | none |
| 237 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_open...` | Test circuit breaker opens after failure threshold | None | none |
| 238 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestCircuitBreaker::test_circuit_breaker_half...` | Test circuit breaker transitions to half-open after tim... | None | none |
| 239 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderSpecificResilience::test_openai_c...` | Test OpenAI-specific resilient configuration | None | none |
| 240 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderSpecificResilience::test_anthropi...` | Test Anthropic-specific resilient configuration | None | none |
| 241 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestProviderSpecificResilience::test_google_c...` | Test Google-specific resilient configuration | None | none |
| 242 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `TestErrorConsistency::test_error_response_for...` | Test that all errors follow consistent format | None | none |
| 243 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_mask_api_key` | Test API key masking for security | None | none |
| 244 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_base_adapter_properties` | Test BaseAdapter properties | None | none |
| 245 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_shared_client_timeout` | Test that CLIENT has correct timeout configuration | None | none |
| 246 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_all_adapters_use_shared_client` | Test that all adapters use the shared CLIENT | None | none |
| 247 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_initialization` | Test circuit breaker initializes in closed state | None | none |
| 248 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_opens_after_failures` | Test circuit breaker opens after failure threshold | None | none |
| 249 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_circuit_breaker_half_open_after_timeout` | Test circuit breaker transitions to half-open after tim... | None | none |
| 250 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_openai_config` | Test OpenAI-specific resilient configuration | None | none |
| 251 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_anthropic_config` | Test Anthropic-specific resilient configuration | None | none |
| 252 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_google_config` | Test Google-specific resilient configuration | None | none |
| 253 | Unit | 2. LLM Providers | `test_llm_adapters_comprehensive.py` | `test_error_response_format` | Test that all errors follow consistent format | None | none |
| 254 | Unit | 21. Miscellaneous | `test_middleware.py` | `test_security_headers_present` | Security headers present | app with security headers | unit |
| 255 | Unit | 21. Miscellaneous | `test_middleware.py` | `test_rate_limit_headers_present` | Rate limit headers present | app with rate limit | unit |
| 256 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_calculate_cost_singl...` | Test cost calculation for a single model usage. | None | none |
| 257 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_calculate_cost_batch` | Test batch cost calculation for multiple requests. | None | none |
| 258 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_get_model_pricing` | Test retrieving pricing information for a model. | None | none |
| 259 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_get_historical_prici...` | Test retrieving historical pricing information. | None | none |
| 260 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_list_all_model_prici...` | Test listing pricing for all available models. | None | none |
| 261 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_estimate_cost_from_p...` | Test cost estimation before execution. | None | none |
| 262 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_update_pricing_admin` | Test updating model pricing (admin function). | None | none |
| 263 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_pricing_not_found_er...` | Test handling of missing pricing information. | None | none |
| 264 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_usage_cost_summary` | Test generating cost summaries over time periods. | None | none |
| 265 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_export_usage_report` | Test exporting detailed usage reports. | None | none |
| 266 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_token_counting_accur...` | Test accuracy of token counting for different models. | None | none |
| 267 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_multi_currency_suppo...` | Test support for multiple currencies. | None | none |
| 268 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_pricing_cache_perfor...` | Test caching of pricing information. | None | none |
| 269 | Unit | 16. Configuration | `test_pricing_service.py` | `TestPricingService::test_concurrent_cost_calc...` | Test thread-safety of cost calculations. | None | none |
| 270 | Unit | 16. Configuration | `test_pricing_service.py` | `test_calculate_cost_single_model` | Test cost calculation for a single model usage. | None | none |
| 271 | Unit | 16. Configuration | `test_pricing_service.py` | `test_calculate_cost_batch` | Test batch cost calculation for multiple requests. | None | none |
| 272 | Unit | 16. Configuration | `test_pricing_service.py` | `test_get_model_pricing` | Test retrieving pricing information for a model. | None | none |
| 273 | Unit | 16. Configuration | `test_pricing_service.py` | `test_get_historical_pricing` | Test retrieving historical pricing information. | None | none |
| 274 | Unit | 16. Configuration | `test_pricing_service.py` | `test_list_all_model_pricing` | Test listing pricing for all available models. | None | none |
| 275 | Unit | 16. Configuration | `test_pricing_service.py` | `test_estimate_cost_from_prompt` | Test cost estimation before execution. | None | none |
| 276 | Unit | 16. Configuration | `test_pricing_service.py` | `test_update_pricing_admin` | Test updating model pricing (admin function). | None | none |
| 277 | Unit | 16. Configuration | `test_pricing_service.py` | `test_pricing_not_found_error` | Test handling of missing pricing information. | None | none |
| 278 | Unit | 16. Configuration | `test_pricing_service.py` | `test_usage_cost_summary` | Test generating cost summaries over time periods. | None | none |
| 279 | Unit | 16. Configuration | `test_pricing_service.py` | `test_export_usage_report` | Test exporting detailed usage reports. | None | none |
| 280 | Unit | 16. Configuration | `test_pricing_service.py` | `test_token_counting_accuracy` | Test accuracy of token counting for different models. | None | none |
| 281 | Unit | 16. Configuration | `test_pricing_service.py` | `test_multi_currency_support` | Test support for multiple currencies. | None | none |
| 282 | Unit | 16. Configuration | `test_pricing_service.py` | `test_pricing_cache_performance` | Test caching of pricing information. | None | none |
| 283 | Unit | 16. Configuration | `test_pricing_service.py` | `test_concurrent_cost_calculations` | Test thread-safety of cost calculations. | None | none |
| 284 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_app` | Create a test FastAPI app with request tracking. | None | none |
| 285 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDMiddleware::test_generates_reque...` | Test that middleware generates request ID when not prov... | HTTP client | none |
| 286 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDMiddleware::test_preserves_exist...` | Test that middleware preserves existing request ID. | HTTP client | none |
| 287 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDMiddleware::test_correlation_id_...` | Test correlation ID handling. | HTTP client | none |
| 288 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDMiddleware::test_uses_request_id...` | Test that request ID is used as correlation ID when not... | HTTP client | none |
| 289 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDInjector::test_inject_headers` | Test header injection. | None | none |
| 290 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestRequestIDInjector::test_from_request` | Test extracting IDs from request. | None | none |
| 291 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestTrackedOrchestrationService::test_set_req...` | Test setting request context. | tracked service | none |
| 292 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestTrackedLLMAdapters::test_tracked_http_cli...` | Test tracked HTTP client adds headers. | None | none |
| 293 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `TestCorrelationContext::test_correlation_cont...` | Test setting and clearing correlation context. | None | none |
| 294 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_generates_request_id` | Test that middleware generates request ID when not prov... | HTTP client | none |
| 295 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_preserves_existing_request_id` | Test that middleware preserves existing request ID. | HTTP client | none |
| 296 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_correlation_id_handling` | Test correlation ID handling. | HTTP client | none |
| 297 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_uses_request_id_as_correlation_fallback` | Test that request ID is used as correlation ID when not... | HTTP client | none |
| 298 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_inject_headers` | Test header injection. | None | none |
| 299 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_from_request` | Test extracting IDs from request. | None | none |
| 300 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_set_request_context` | Test setting request context. | tracked service | none |
| 301 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_tracked_http_client` | Test tracked HTTP client adds headers. | None | none |
| 302 | Unit | 21. Miscellaneous | `test_request_tracking.py` | `test_correlation_context_lifecycle` | Test setting and clearing correlation context. | None | none |
| 303 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_telemetry_initiali...` | Test that telemetry service initializes properly. | None | none |
| 304 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_record_request` | Test recording HTTP request metrics. | None | none |
| 305 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_record_llm_request` | Test recording LLM request metrics. | None | none |
| 306 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_record_stage_durat...` | Test recording pipeline stage duration. | None | none |
| 307 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_record_error` | Test recording errors. | None | none |
| 308 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_trace_span_context...` | Test trace span context manager. | None | none |
| 309 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryService::test_measure_stage_cont...` | Test measure stage context manager. | None | none |
| 310 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryLLMWrapper::test_token_estimatio...` | Test token estimation logic. | None | none |
| 311 | Unit | 21. Miscellaneous | `test_telemetry.py` | `TestTelemetryLLMWrapper::test_cost_calculatio...` | Test cost calculation. | None | none |
| 312 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_telemetry_initialization` | Test that telemetry service initializes properly. | None | none |
| 313 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_record_request` | Test recording HTTP request metrics. | None | none |
| 314 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_record_llm_request` | Test recording LLM request metrics. | None | none |
| 315 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_record_stage_duration` | Test recording pipeline stage duration. | None | none |
| 316 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_record_error` | Test recording errors. | None | none |
| 317 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_trace_span_context_manager` | Test trace span context manager. | None | none |
| 318 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_measure_stage_context_manager` | Test measure stage context manager. | None | none |
| 319 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_token_estimation` | Test token estimation logic. | None | none |
| 320 | Unit | 21. Miscellaneous | `test_telemetry.py` | `test_cost_calculation` | Test cost calculation. | None | none |
| 321 | Unit | 21. Miscellaneous | `test_three_model_policy.py` | `test_fail_with_fewer_than_three_models` | Fail with fewer than three models | None | none |
| 322 | Unit | 21. Miscellaneous | `test_three_model_policy.py` | `test_succeeds_with_three_models` | Succeeds with three models | None | none |
