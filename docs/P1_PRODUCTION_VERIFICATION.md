# P1 Production Verification Checklist

## Pre-Deployment Verification

### 1. Authentication & Rate Limiting (Issue #33)
- [ ] Set `ENABLE_AUTH=true` in production environment
- [ ] Configure `JWT_SECRET` environment variable
- [ ] Test JWT token generation and validation
- [ ] Test API key authentication
- [ ] Verify `/api/admin/*` endpoints require authentication
- [ ] Verify `/api/debug/*` endpoints require authentication
- [ ] Test rate limiting for different user tiers
- [ ] Confirm Redis is available for rate limit storage

### 2. Secret Scanning (Issue #34)
- [ ] Run `./scripts/rotate_secrets.py --check` to verify no hardcoded secrets
- [ ] Ensure GitHub Actions secret scanning workflow is enabled
- [ ] Test pre-commit hooks are installed: `pre-commit run --all-files`
- [ ] Verify all API keys are loaded from environment variables

### 3. Circuit Breakers & Resilience (Issue #35)
- [ ] Test with invalid API keys to verify circuit breaker activates
- [ ] Monitor logs for retry attempts with backoff
- [ ] Verify provider-specific timeouts are working
- [ ] Test graceful degradation when LLM providers are unavailable

### 4. Smart Model Selection (Issue #36)
- [ ] Verify SmartModelSelectionService is initialized
- [ ] Test model selection based on query complexity
- [ ] Confirm fallback models are configured

### 5. OpenTelemetry & Metrics (Issue #37)
- [ ] Set `OTEL_ENABLED=true` in production
- [ ] Configure `OTEL_EXPORTER_OTLP_ENDPOINT`
- [ ] Access metrics at `/api/metrics`
- [ ] Verify traces are being exported
- [ ] Check token usage and cost tracking

## Production Testing Commands

```bash
# 1. Test health endpoint
curl https://ultrai-core.onrender.com/health

# 2. Test authentication required
curl -X GET https://ultrai-core.onrender.com/api/admin/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Test rate limiting
for i in {1..15}; do
  curl -X GET https://ultrai-core.onrender.com/api/orchestrator/health
  sleep 0.1
done

# 4. Test orchestration with telemetry
curl -X POST https://ultrai-core.onrender.com/api/orchestrator/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "What is machine learning?",
    "selected_models": ["gpt-4", "claude-3-5-sonnet-20241022"],
    "options": {
      "include_pipeline_details": true
    }
  }'

# 5. Check metrics
curl https://ultrai-core.onrender.com/api/metrics | grep ultrai_
```

## Monitoring After Deployment

### Key Metrics to Monitor
1. **Request Rate**: `ultrai_request_total`
2. **Error Rate**: `ultrai_error_total`
3. **LLM Latency**: `ultrai_llm_duration_seconds`
4. **Token Usage**: `ultrai_tokens_total`
5. **Circuit Breaker State**: `ultrai_circuit_breaker_state`

### Log Patterns to Watch
```
# Successful auth
INFO: Authentication successful for user: ...

# Rate limiting
WARNING: Rate limit exceeded for user: ...

# Circuit breaker activation
ERROR: Circuit breaker OPEN for provider: ...

# Telemetry tracking
INFO: LLM request completed: openai/gpt-4
```

## Rollback Plan

If issues are detected:

1. **Quick Disable Features**:
   ```bash
   ENABLE_AUTH=false
   ENABLE_RATE_LIMIT=false
   OTEL_ENABLED=false
   ```

2. **Revert to Previous Version**:
   - Render will automatically keep previous deployment
   - Use Render dashboard to rollback

3. **Emergency Contacts**:
   - Monitor: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg
   - Logs: Check Render dashboard for real-time logs

## Success Criteria

- [ ] All health checks passing
- [ ] Authentication working for protected endpoints
- [ ] Rate limiting active without blocking legitimate traffic
- [ ] Circuit breakers protecting against provider failures
- [ ] Metrics being collected and exported
- [ ] No increase in error rates
- [ ] Response times remain stable
- [ ] Cost tracking operational