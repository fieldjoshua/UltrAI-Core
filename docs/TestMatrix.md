# Ultra Test Matrix (grouped)

## Auth & Rate Limiting (25 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_auth_rate_limit.TestAuthMiddleware | test_admin_endpoints_require_auth | passed | - | - |
| tests.test_auth_rate_limit.TestAuthMiddleware | test_debug_endpoints_require_auth | passed | - | - |
| tests.test_auth_rate_limit.TestAuthMiddleware | test_invalid_auth_rejected | passed | - | - |
| tests.test_auth_rate_limit.TestAuthMiddleware | test_public_endpoints_no_auth | passed | - | - |
| tests.test_auth_rate_limit.TestAuthMiddleware | test_valid_api_key_allows_access | passed | - | - |
| tests.test_auth_rate_limit.TestAuthMiddleware | test_valid_jwt_token_allows_access | passed | - | - |
| tests.test_auth_rate_limit.TestRateLimiting | test_ip_based_rate_limiting_for_unauthenticated | passed | - | - |
| tests.test_auth_rate_limit.TestRateLimiting | test_per_user_rate_limiting | passed | - | - |
| tests.test_auth_rate_limit.TestRateLimiting | test_rate_limit_exceeded_returns_429 | passed | - | - |
| tests.test_auth_rate_limit.TestRateLimiting | test_rate_limit_headers_added | passed | - | - |
| tests.test_auth_rate_limit.TestRateLimiting | test_rate_limiting_disabled_when_redis_unavailable | passed | - | - |
| tests.test_rate_limit_service | test_placeholder_rate_limit_service | passed | - | - |
| tests.test_rate_limit_service_logic | test_default_tier_is_free | passed | - | - |
| tests.test_rate_limit_service_logic | test_get_window_seconds[day-86400] | passed | - | - |
| tests.test_rate_limit_service_logic | test_get_window_seconds[hour-3600] | passed | - | - |
| tests.test_rate_limit_service_logic | test_get_window_seconds[minute-60] | passed | - | - |
| tests.test_rate_limit_service_logic | test_get_window_seconds[second-1] | passed | - | - |
| tests.test_rate_limit_service_logic | test_tier_limits_keys | passed | - | - |
| tests.test_rate_limiter | test_acquire_increments_current_requests | passed | - | - |
| tests.test_rate_limiter | test_acquire_unregistered_raises | passed | - | - |
| tests.test_rate_limiter | test_register_endpoint_and_stats | passed | - | - |
| tests.test_rate_limiter | test_release_adjusts_backoff | passed | - | - |
| tests.test_rate_limiter | test_release_unregistered_does_nothing_and_stats_empty | passed | - | - |
| tests.unit.test_middleware | test_rate_limit_headers_present | passed | - | - |
| tests.unit.test_middleware | test_security_headers_present | passed | - | - |

## Cache & Health & Telemetry (50 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.unit.test_cache_service | test_async_json_operations | passed | - | - |
| tests.unit.test_cache_service | test_delete_and_flush | passed | - | - |
| tests.unit.test_cache_service | test_sync_cache_operations | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheDecorator | test_cached_async_function | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheDecorator | test_cached_sync_function | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheDecorator | test_cached_with_ttl | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheIntegrationScenarios | test_cache_size_limits | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheIntegrationScenarios | test_concurrent_cache_access | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheIntegrationScenarios | test_orchestration_response_caching | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheKeyGeneration | test_cache_key_complex_types | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheKeyGeneration | test_cache_key_none_handling | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheKeyGeneration | test_cache_key_simple_types | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_cleanup_memory_cache | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_clear_pattern | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_close | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_get_stats | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_initialization_with_redis | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_initialization_without_redis | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_json_operations | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_memory_cache_operations | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_memory_cache_ttl | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_redis_fallback_to_memory | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheService | test_redis_operations | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheSingleton | test_close_cache_service | passed | - | - |
| tests.unit.test_cache_service_comprehensive.TestCacheSingleton | test_get_cache_service_singleton | passed | - | - |
| tests.unit.test_request_tracking.TestCorrelationContext | test_correlation_context_lifecycle | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDInjector | test_from_request | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDInjector | test_inject_headers | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDMiddleware | test_correlation_id_handling | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDMiddleware | test_generates_request_id | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDMiddleware | test_preserves_existing_request_id | passed | - | - |
| tests.unit.test_request_tracking.TestRequestIDMiddleware | test_uses_request_id_as_correlation_fallback | passed | - | - |
| tests.unit.test_request_tracking.TestTrackedLLMAdapters | test_tracked_adapter_logging | passed | - | - |
| tests.unit.test_request_tracking.TestTrackedLLMAdapters | test_tracked_http_client | passed | - | - |
| tests.unit.test_request_tracking.TestTrackedOrchestrationService | test_create_adapter_with_tracking | passed | - | - |
| tests.unit.test_request_tracking.TestTrackedOrchestrationService | test_set_request_context | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_cost_calculation | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_token_estimation | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_wrapper_generate_error | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_wrapper_generate_exception | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_wrapper_generate_success | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_wrapper_initialization | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryLLMWrapper | test_wrapper_metrics | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_measure_stage_context_manager | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_record_error | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_record_llm_request | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_record_request | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_record_stage_duration | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_telemetry_initialization | passed | - | - |
| tests.unit.test_telemetry.TestTelemetryService | test_trace_span_context_manager | passed | - | - |

## Configuration & Modes (19 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_config_example | test_offline_specific | passed | - | - |
| tests.test_config_example.TestConfigurationExample | test_endpoint_configuration | passed | - | - |
| tests.test_config_example.TestConfigurationExample | test_integration_only | skipped | - | - |
| tests.test_config_example.TestConfigurationExample | test_live_api_call | - | passed | - |
| tests.test_config_example.TestConfigurationExample | test_mock_behavior | passed | - | - |
| tests.test_config_example.TestConfigurationExample | test_mode_detection | passed | - | - |
| tests.test_config_example.TestConfigurationExample | test_production_endpoint | skipped | - | - |
| tests.test_config_example.TestConfigurationExample | test_requiring_external_services | skipped | - | - |
| tests.test_config_example.TestMockConfiguration | test_mock_adapter_creation | passed | - | - |
| tests.test_config_example.TestMockConfiguration | test_mock_responses_available | passed | - | - |
| tests.test_config_example.TestMockConfiguration | test_timeout_configuration | passed | - | - |
| tests.test_configuration_system | test_pytest_working | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_configuration_loads | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_endpoints_configured | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_environment_variables | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_mock_configuration | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_mock_llm_adapter | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_skip_reasons | passed | - | - |
| tests.test_configuration_system.TestConfigurationSystem | test_timeout_configuration | passed | - | - |

## Demo Endpoints (2 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.live.test_demo_endpoints | test_demo_health_available_models | - | skipped | skipped |
| tests.live.test_demo_endpoints | test_demo_models_providers_summary | - | skipped | skipped |

## Docs & Data (3 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_quality_evaluation | test_compare_responses_returns_correct_keys | passed | - | - |
| tests.test_quality_evaluation | test_evaluate_response_defaults | passed | - | - |
| tests.test_quality_evaluation | test_generate_quality_report_selects_best | passed | - | - |

## LLM Adapters (44 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_adapter_authentication_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_adapter_initialization | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_adapter_model_not_found_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_adapter_successful_response | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestBaseAdapter | test_base_adapter_generate_not_implemented | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestBaseAdapter | test_base_adapter_requires_api_key | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestBaseAdapter | test_base_adapter_stores_config | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestGeminiAdapter | test_gemini_adapter_authentication_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestGeminiAdapter | test_gemini_adapter_bad_request_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestGeminiAdapter | test_gemini_adapter_initialization | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestGeminiAdapter | test_gemini_adapter_successful_response | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_huggingface_adapter_chat_model_formatting | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_huggingface_adapter_initialization | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_huggingface_adapter_model_loading_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_huggingface_adapter_successful_response | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_openai_adapter_authentication_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_openai_adapter_initialization | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_openai_adapter_model_not_found_error | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_openai_adapter_successful_response | passed | - | - |
| tests.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_openai_adapter_timeout_error | passed | - | - |
| tests.test_resilient_llm_adapter.TestCircuitBreaker | test_async_circuit_breaker | passed | - | - |
| tests.test_resilient_llm_adapter.TestCircuitBreaker | test_circuit_breaker_half_open_after_timeout | passed | - | - |
| tests.test_resilient_llm_adapter.TestCircuitBreaker | test_circuit_breaker_initialization | passed | - | - |
| tests.test_resilient_llm_adapter.TestCircuitBreaker | test_circuit_breaker_opens_after_failures | passed | - | - |
| tests.test_resilient_llm_adapter.TestProviderConfigurations | test_anthropic_config | passed | - | - |
| tests.test_resilient_llm_adapter.TestProviderConfigurations | test_google_config | passed | - | - |
| tests.test_resilient_llm_adapter.TestProviderConfigurations | test_openai_config | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_circuit_breaker_integration | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_cleanup | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_exponential_backoff_with_jitter | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_metrics_tracking | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_no_retry_on_client_error | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_provider_specific_timeouts | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_retry_on_timeout | passed | - | - |
| tests.test_resilient_llm_adapter.TestResilientLLMAdapter | test_successful_generation | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestErrorResponseModel | test_authentication_error_legacy_format | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestErrorResponseModel | test_error_response_to_legacy_format | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_authentication_error_anthropic | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_authentication_error_openai | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_huggingface_model_loading | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_model_not_found_error | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_rate_limit_error_all_providers | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_success_response_format | passed | - | - |
| tests.unit.test_standardized_llm_errors.TestStandardizedErrors | test_timeout_error | passed | - | - |

## Live Providers (4 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.live.test_live_providers | test_anthropic_smoke | - | passed | - |
| tests.live.test_live_providers | test_gemini_smoke | - | passed | - |
| tests.live.test_live_providers | test_huggingface_smoke | - | skipped | - |
| tests.live.test_live_providers | test_openai_smoke | - | passed | - |

## Model Registry & Selection (5 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_model_registry | test_errors_on_invalid_operations | passed | - | - |
| tests.test_model_registry | test_list_models_and_unregister | passed | - | - |
| tests.test_model_registry | test_register_and_create_instance | passed | - | - |
| tests.test_model_registry | test_update_config_and_record_usage | passed | - | - |
| tests.unit.test_model_selection_service | test_model_selection_ranks_models_by_score | passed | - | - |

## Orchestration & Streaming (14 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_orchestration_service | test_run_pipeline_completes_all_stages | passed | - | - |
| tests.test_orchestration_service | test_run_pipeline_stops_on_stage_error | passed | - | - |
| tests.test_orchestration_synthesis.TestUltraSynthesisOrchestrator | test_initial_response_stage_with_multiple_models | passed | - | - |
| tests.test_orchestration_synthesis.TestUltraSynthesisOrchestrator | test_initial_response_stage_with_single_model | passed | - | - |
| tests.test_orchestration_synthesis.TestUltraSynthesisOrchestrator | test_meta_analysis_stage_enhances_responses | passed | - | - |
| tests.test_orchestration_synthesis.TestUltraSynthesisOrchestrator | test_ultra_synthesis_stage_creates_comprehensive_synthesis | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingEndpoint | test_streaming_endpoint_headers | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_error_event_on_failure | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_model_response_streaming | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_sse_format | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_stage_events_emitted | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_stream_pipeline_start_event | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_streaming_config | passed | - | - |
| tests.unit.test_streaming_orchestration.TestStreamingOrchestrationService | test_synthesis_chunking | passed | - | - |

## Other (80 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_analysis_pipeline | test_process_text_default_layers | passed | - | - |
| tests.test_analysis_pipeline | test_process_text_with_unknown_layer_skipped | passed | - | - |
| tests.test_analysis_service | test_create_analysis_with_doc_check | passed | - | - |
| tests.test_analysis_service | test_get_analysis_by_id_and_permission | passed | - | - |
| tests.test_analysis_service | test_get_document_analyses_with_access | passed | - | - |
| tests.test_analysis_service | test_get_pattern_stats | passed | - | - |
| tests.test_analysis_service | test_get_user_analyses | passed | - | - |
| tests.test_analysis_service | test_update_analysis_status_and_permission | passed | - | - |
| tests.test_api_failure_handler | test_execute_api_call_cache_hit | passed | - | - |
| tests.test_api_failure_handler | test_execute_api_call_provider_success | passed | - | - |
| tests.test_api_failure_handler | test_get_statistics_initial | passed | - | - |
| tests.test_basic_orchestrator | test_orchestrate_basic_empty_prompt | passed | - | - |
| tests.test_basic_orchestrator | test_orchestrate_basic_no_models_defaults | passed | - | - |
| tests.test_basic_orchestrator | test_orchestrate_basic_success | passed | - | - |
| tests.test_example_modes.TestModeExamples | test_always_runs | passed | - | - |
| tests.test_example_modes.TestModeExamples | test_check_configuration | passed | - | - |
| tests.test_example_modes.TestModeExamples | test_environment_variables | passed | - | - |
| tests.test_example_modes.TestModeExamples | test_live_or_production | skipped | - | - |
| tests.test_example_modes.TestModeExamples | test_needs_some_services | skipped | - | - |
| tests.test_token_management_service | test_track_usage_and_get_user_usage_and_total_cost | passed | - | - |
| tests.test_token_management_service | test_track_usage_unknown_model_raises | passed | - | - |
| tests.test_token_management_service | test_update_cost_rates_affects_future_costs | passed | - | - |
| tests.test_transaction_service | test_add_funds_negative_amount_raises | passed | - | - |
| tests.test_transaction_service | test_add_funds_positive_amount | passed | - | - |
| tests.test_transaction_service | test_deduct_cost_insufficient_returns_none | passed | - | - |
| tests.test_transaction_service | test_deduct_cost_negative_amount_raises | passed | - | - |
| tests.test_transaction_service | test_deduct_cost_successful_after_credit | passed | - | - |
| tests.test_transaction_service | test_get_balance_default_zero | passed | - | - |
| tests.unit.orchestrator.test_orchestrator_features | test_cost_estimate_present | passed | - | - |
| tests.unit.orchestrator.test_orchestrator_features | test_encryption_support | passed | - | - |
| tests.unit.orchestrator.test_orchestrator_features | test_options_passed_to_stages | passed | - | - |
| tests.unit.orchestrator.test_orchestrator_features | test_plain_text_format | passed | - | - |
| tests.unit.test_auth_orchestrator_protection | test_orchestrator_requires_auth | passed | - | - |
| tests.unit.test_auth_service | test_create_and_verify_access_token | passed | - | - |
| tests.unit.test_auth_service | test_create_and_verify_refresh_token | passed | - | - |
| tests.unit.test_auth_service | test_verify_invalid_tokens | passed | - | - |
| tests.unit.test_document_processor | test_process_text_file | passed | - | - |
| tests.unit.test_document_processor | test_process_unknown_file_type | passed | - | - |
| tests.unit.test_document_service | test_delete_document | passed | - | - |
| tests.unit.test_document_service | test_get_document_by_id | passed | - | - |
| tests.unit.test_document_service | test_get_user_documents | passed | - | - |
| tests.unit.test_health_service | test_get_health_detailed | passed | - | - |
| tests.unit.test_health_service | test_get_health_simple | passed | - | - |
| tests.unit.test_jwt_secret_alias | test_jwt_missing_secret_raises_error | passed | - | - |
| tests.unit.test_jwt_secret_alias | test_jwt_refresh_secret_fallback | passed | - | - |
| tests.unit.test_jwt_secret_alias | test_jwt_secret_key_precedence | passed | - | - |
| tests.unit.test_llm_adapters | test_anthropic_adapter_error | passed | - | - |
| tests.unit.test_llm_adapters | test_base_adapter_missing_api_key | passed | - | - |
| tests.unit.test_llm_adapters | test_gemini_adapter_error | passed | - | - |
| tests.unit.test_llm_adapters | test_openai_adapter_error | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_connection_timeout[AnthropicAdapter-claude-3] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_connection_timeout[GeminiAdapter-gemini-pro] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_connection_timeout[HuggingFaceAdapter-mistral] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_connection_timeout[OpenAIAdapter-gpt-4] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_invalid_api_key[AnthropicAdapter-claude-3] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_invalid_api_key[GeminiAdapter-gemini-pro] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_invalid_api_key[HuggingFaceAdapter-mistral] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_invalid_api_key[OpenAIAdapter-gpt-4] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_json_decode_error[AnthropicAdapter-claude-3] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_json_decode_error[GeminiAdapter-gemini-pro] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_json_decode_error[HuggingFaceAdapter-mistral] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAdapterErrorScenarios | test_json_decode_error[OpenAIAdapter-gpt-4] | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_model_mapping | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestAnthropicAdapter | test_anthropic_specific_headers | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestBaseAdapter | test_base_adapter_not_implemented | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestBaseAdapter | test_base_adapter_properties | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestBaseAdapter | test_mask_api_key | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestGeminiAdapter | test_api_key_in_header | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestGeminiAdapter | test_api_key_not_in_url | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestGeminiAdapter | test_gemini_response_format_variations | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_huggingface_model_url_encoding | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_response_format_dict | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_response_format_list | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_response_format_string | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestHuggingFaceAdapter | test_response_format_unexpected | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_correlation_context_integration | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_generic_exception_handling | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestOpenAIAdapter | test_rate_limit_error_handling | passed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestSharedHttpClient | test_all_adapters_use_shared_client | failed | - | - |
| tests.unit.test_llm_adapters_comprehensive.TestSharedHttpClient | test_shared_client_timeout | passed | - | - |

## Pricing/Budget/Billing (mostly skipped) (47 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.unit.test_billing_service.TestBillingService | test_add_payment_method | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_billing_history | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_cancel_subscription | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_create_invoice | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_create_subscription | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_invoice_overdue_handling | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_list_payment_methods | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_payment_method_validation | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_payment_retry_logic | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_pci_compliance | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_process_payment_failure | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_process_payment_success | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_process_refund | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_remove_payment_method | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_send_invoice_email | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_subscription_trial_period | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_update_subscription | skipped | - | - |
| tests.unit.test_billing_service.TestBillingService | test_webhook_handling | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_admin_budget_reset | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_budget_history | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_budget_period_reset | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_budget_rollover | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_check_budget_insufficient | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_check_budget_sufficient | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_concurrent_budget_operations | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_configure_budget_alerts | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_deduct_from_budget_insufficient_funds | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_deduct_from_budget_success | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_get_budget_status | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_refund_to_budget | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_set_budget_limit | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_trigger_budget_alerts | skipped | - | - |
| tests.unit.test_budget_service.TestBudgetService | test_usage_forecast | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_calculate_cost_batch | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_calculate_cost_single_model | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_concurrent_cost_calculations | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_estimate_cost_from_prompt | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_export_usage_report | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_get_historical_pricing | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_get_model_pricing | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_list_all_model_pricing | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_multi_currency_support | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_pricing_cache_performance | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_pricing_not_found_error | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_token_counting_accuracy | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_update_pricing_admin | skipped | - | - |
| tests.unit.test_pricing_service.TestPricingService | test_usage_cost_summary | skipped | - | - |

## Production/External (skipped offline) (2 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.production.test_network_and_orchestrator | test_external_endpoints_reachable | skipped | - | - |
| tests.production.test_network_and_orchestrator | test_orchestrator_pipeline_openai | skipped | - | - |

## Prompting & Templates (17 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_prompt_service | test_default_templates_registered | passed | - | - |
| tests.test_prompt_service | test_format_output_html | passed | - | - |
| tests.test_prompt_service | test_format_output_json | passed | - | - |
| tests.test_prompt_service | test_format_output_plain | passed | - | - |
| tests.test_prompt_service | test_placeholder_prompt_service | passed | - | - |
| tests.test_prompt_service | test_register_and_get_template | passed | - | - |
| tests.test_prompt_service | test_register_duplicate_raises | passed | - | - |
| tests.test_prompt_service | test_render_template_invalid_var | passed | - | - |
| tests.test_prompt_service | test_render_template_missing_var | passed | - | - |
| tests.test_prompt_service | test_render_template_success | passed | - | - |
| tests.test_prompt_service | test_update_template | passed | - | - |
| tests.test_prompt_templates | test_list_templates_empty | passed | - | - |
| tests.test_prompt_templates | test_load_templates_from_file | passed | - | - |
| tests.test_prompt_templates | test_register_and_get_template | passed | - | - |
| tests.test_prompt_templates | test_render_template_missing_not_strict | passed | - | - |
| tests.test_prompt_templates | test_render_template_missing_strict | passed | - | - |
| tests.test_prompt_templates | test_render_template_success | passed | - | - |

## Recovery & Availability (15 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.unit.test_recovery_service | test_circuit_breaker_integration | failed | - | - |
| tests.unit.test_recovery_service | test_retry_on_timeout | failed | - | - |
| tests.unit.test_recovery_service_simple | test_circuit_breaker_integration | passed | - | - |
| tests.unit.test_recovery_service_simple | test_retry_on_timeout | passed | - | - |
| tests.unit.test_service_unavailable.TestServiceUnavailable | test_error_message_clarity | passed | - | - |
| tests.unit.test_service_unavailable.TestServiceUnavailable | test_service_available_with_multiple_models | passed | - | - |
| tests.unit.test_service_unavailable.TestServiceUnavailable | test_service_status_endpoint | passed | - | - |
| tests.unit.test_service_unavailable.TestServiceUnavailable | test_service_unavailable_with_one_model | passed | - | - |
| tests.unit.test_service_unavailable.TestServiceUnavailable | test_zero_models_available | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_default_models_with_single_fallback | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_minimum_models_configuration | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_peer_review_skipped_with_single_model | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_single_model_operation_disabled | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_single_model_operation_enabled | passed | - | - |
| tests.unit.test_single_model_fallback.TestSingleModelFallback | test_ultra_synthesis_with_single_model | passed | - | - |

## Security & Identity (3 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.unit.test_oauth_service | test_generate_oauth_url_google | passed | - | - |
| tests.unit.test_oauth_service | test_generate_oauth_url_unsupported | passed | - | - |
| tests.unit.test_oauth_service | test_validate_oauth_state | passed | - | - |

## Service Instantiation (140 tests)

| Module | Test | Offline | Live | Demo |
|---|---|---|---|---|
| tests.test_service_instantiation | test_instantiate_service_class[analysis_pipeline-AnalysisPipeline-AnalysisPipeline] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[analysis_pipeline-AnalysisResult-AnalysisResult] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[analysis_pipeline-ModelRegistry-ModelRegistry] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[analysis_service-AnalysisService-AnalysisService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[analysis_service-DocumentService-DocumentService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[api_failure_handler-APICallContext-APICallContext] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[api_failure_handler-APIFailureHandler-APIFailureHandler] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[api_failure_handler-APIProvider-APIProvider] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[auth_service-AuthService-AuthService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[auth_service_new-AuthService-AuthService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[base_llm_adapter-EnhancedBaseAdapter-EnhancedBaseAdapter] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[cache_service-CacheService-CacheService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[db_optimization_service-DatabaseOptimizationService-DatabaseOptimizationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[document_processor-UltraDocumentsOptimized-UltraDocumentsOptimized] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[document_service-DocumentService-DocumentService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[enhanced_llm_adapters-EnhancedAnthropicAdapter-EnhancedAnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[enhanced_llm_adapters-EnhancedBaseAdapter-EnhancedBaseAdapter] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[enhanced_llm_adapters-EnhancedGeminiAdapter-EnhancedGeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[enhanced_llm_adapters-EnhancedHuggingFaceAdapter-EnhancedHuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[enhanced_llm_adapters-EnhancedOpenAIAdapter-EnhancedOpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[health_service-HealthService-HealthService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[interfaces-BillingServiceInterface-BillingServiceInterface] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[interfaces-BudgetServiceInterface-BudgetServiceInterface] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[interfaces-PricingServiceInterface-PricingServiceInterface] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-AnthropicAdapter-AnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-EnhancedAnthropicAdapter-EnhancedAnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-EnhancedGeminiAdapter-EnhancedGeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-EnhancedHuggingFaceAdapter-EnhancedHuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-EnhancedOpenAIAdapter-EnhancedOpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-GeminiAdapter-GeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-HuggingFaceAdapter-HuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-LLMAdapterFactory-LLMAdapterFactory] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapter_factory-OpenAIAdapter-OpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-AnthropicAdapter-AnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-BaseAdapter-BaseAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-GeminiAdapter-GeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-HuggingFaceAdapter-HuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-OpenAIAdapter-OpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_adapters-correlation_context-correlation_context] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[llm_config_service-LLMConfigService-LLMConfigService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[manage_parameters-Colors-Colors] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-AnthropicAdapter-AnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-AvailabilityStatus-AvailabilityStatus] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-GeminiAdapter-GeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-HuggingFaceAdapter-HuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-ModelAvailability-ModelAvailability] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-ModelAvailabilityChecker-ModelAvailabilityChecker] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_availability-OpenAIAdapter-OpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_health_cache-ModelHealthCache-ModelHealthCache] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_registry-ModelConfig-ModelConfig] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_registry-ModelInstance-ModelInstance] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_registry-ModelRegistry-ModelRegistry] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection-ModelPerformanceMetrics-ModelPerformanceMetrics] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection-SmartModelSelector-SmartModelSelector] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection_service-AvailabilityStatus-AvailabilityStatus] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection_service-ModelAvailabilityChecker-ModelAvailabilityChecker] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection_service-PricingCalculator-PricingCalculator] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection_service-SmartModelSelectionService-SmartModelSelectionService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[model_selection_service-SmartModelSelector-SmartModelSelector] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[oauth_service-OAuthService-OAuthService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_retry_handler-OrchestrationRetryHandler-OrchestrationRetryHandler] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-AnthropicAdapter-AnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-GeminiAdapter-GeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-HuggingFaceAdapter-HuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-OpenAIAdapter-OpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-OrchestrationRetryHandler-OrchestrationRetryHandler] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-OrchestrationService-OrchestrationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-PipelineResult-PipelineResult] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-PipelineStage-PipelineStage] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-QualityEvaluationService-QualityEvaluationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-QueryType-QueryType] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-RateLimiter-RateLimiter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-ResponseQuality-ResponseQuality] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-SmartModelSelector-SmartModelSelector] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-StructuredSynthesisOutput-StructuredSynthesisOutput] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-SynthesisPromptManager-SynthesisPromptManager] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-TokenManagementService-TokenManagementService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[orchestration_service-TransactionService-TransactionService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[output_formatter-OutputFormatter-OutputFormatter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[parameter_editor-Colors-Colors] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[parameter_glossary_generator-ParameterExtractor-ParameterExtractor] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[parameter_glossary_generator-ParameterInfo-ParameterInfo] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[pricing_service-PricingCalculator-PricingCalculator] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[pricing_simulator-PricingSimulator-PricingSimulator] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_service-ModelRegistry-ModelRegistry] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_service-OrchestrationService-OrchestrationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_service-PromptRequest-PromptRequest] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_service-PromptService-PromptService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_service-Template-Template] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_templates-PromptTemplate-PromptTemplate] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[prompt_templates-PromptTemplateManager-PromptTemplateManager] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[provider_health_manager-ProviderHealth-ProviderHealth] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[provider_health_manager-ProviderHealthManager-ProviderHealthManager] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[quality_evaluation-QualityDimension-QualityDimension] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[quality_evaluation-QualityEvaluationService-QualityEvaluationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[quality_evaluation-QualityScore-QualityScore] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[quality_evaluation-ResponseQuality-ResponseQuality] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limit_service-RateLimitCategory-RateLimitCategory] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limit_service-RateLimitInterval-RateLimitInterval] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limit_service-RateLimitResult-RateLimitResult] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limit_service-RateLimitService-RateLimitService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limit_service-RateLimitTier-RateLimitTier] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limiter-RateLimit-RateLimit] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[rate_limiter-RateLimiter-RateLimiter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-BaseAdapter-BaseAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-CircuitBreaker-CircuitBreaker] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-CircuitBreakerConfig-CircuitBreakerConfig] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-CircuitState-CircuitState] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-ProviderConfig-ProviderConfig] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-ResilientLLMAdapter-ResilientLLMAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[resilient_llm_adapter-RetryConfig-RetryConfig] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[streaming_orchestration_service-OrchestrationService-OrchestrationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[streaming_orchestration_service-StreamingOrchestrationService-StreamingOrchestrationService] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[synthesis_output-ConfidenceLevel-ConfidenceLevel] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[synthesis_output-StructuredSynthesisOutput-StructuredSynthesisOutput] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[synthesis_output-SynthesisMetadata-SynthesisMetadata] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[synthesis_prompts-QueryType-QueryType] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[synthesis_prompts-SynthesisPromptManager-SynthesisPromptManager] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[telemetry_llm_wrapper-TelemetryLLMWrapper-TelemetryLLMWrapper] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[telemetry_service-TelemetryService-TelemetryService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[token_management_service-TokenCost-TokenCost] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[token_management_service-TokenManagementService-TokenManagementService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-AnthropicAdapter-AnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-GeminiAdapter-GeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-HuggingFaceAdapter-HuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-OpenAIAdapter-OpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedAnthropicAdapter-TrackedAnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedGeminiAdapter-TrackedGeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedHTTPClient-TrackedHTTPClient] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedHuggingFaceAdapter-TrackedHuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedLLMAdapter-TrackedLLMAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_llm_adapters-TrackedOpenAIAdapter-TrackedOpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-OrchestrationService-OrchestrationService] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-TrackedAnthropicAdapter-TrackedAnthropicAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-TrackedGeminiAdapter-TrackedGeminiAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-TrackedHuggingFaceAdapter-TrackedHuggingFaceAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-TrackedOpenAIAdapter-TrackedOpenAIAdapter] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[tracked_orchestration_service-TrackedOrchestrationService-TrackedOrchestrationService] | skipped | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[transaction_service-Transaction-Transaction] | passed | - | - |
| tests.test_service_instantiation | test_instantiate_service_class[transaction_service-TransactionService-TransactionService] | passed | - | - |

