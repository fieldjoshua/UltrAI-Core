# UltraAI Deploy Readiness Checklist

## Pre-Deployment Verification

### 🔑 API Keys & Environment
- [ ] `OPENAI_API_KEY` set and valid
- [ ] `ANTHROPIC_API_KEY` set and valid  
- [ ] `GOOGLE_API_KEY` set and valid
- [ ] `JWT_SECRET` configured (production value, not default)
- [ ] `DATABASE_URL` pointing to production database
- [ ] `REDIS_URL` configured (optional but recommended)

### 🏥 Health Checks
- [ ] Run `GET /api/orchestrator/status` - verify "ready": true
- [ ] Confirm all 3 providers show in `providers_present`
- [ ] Check startup logs show "✅ Service READY" with 3+ models

### 🧪 Smoke Tests
```bash
# Status check
curl https://your-domain/api/orchestrator/status

# Should see:
# - "status": "healthy"
# - "service_available": true
# - "providers_present": ["openai", "anthropic", "google"]
```

### 🚀 Service Configuration
- [ ] `MINIMUM_MODELS_REQUIRED=3` (or your requirement)
- [ ] `ENABLE_SINGLE_MODEL_FALLBACK=false` for production
- [ ] Rate limiting configured appropriately
- [ ] CORS origins set for production domains only

### 🔒 Security
- [ ] No hardcoded API keys in code
- [ ] Response sanitizer active (no cost fields exposed)
- [ ] Authentication enabled (`ENABLE_AUTH=true`)
- [ ] HTTPS enforced on all endpoints

### 📊 Monitoring
- [ ] Startup readiness logs visible
- [ ] Error tracking configured (Sentry if enabled)
- [ ] Health endpoint monitoring set up
- [ ] 503 alerts configured for provider failures

### ✅ Final Verification
1. Deploy to staging first
2. Run E2E test suite against staging
3. Verify all 3 providers respond within 5s
4. Check no cost/pricing data in responses
5. Confirm 503 responses include provider details

## Quick Verification Script
```bash
# Check service readiness
STATUS=$(curl -s https://your-domain/api/orchestrator/status)
echo $STATUS | jq '.ready'  # Should be true
echo $STATUS | jq '.models.providers_present'  # Should show ["openai", "anthropic", "google"]
```

## Common Issues
- **503 Service Unavailable**: Check API keys are valid
- **Missing providers**: Verify environment variables are set
- **Slow responses**: Check 5s health probe timeouts
- **Authentication errors**: Ensure JWT_SECRET is configured