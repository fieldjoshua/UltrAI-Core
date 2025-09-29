# Render Services Remediation Actions

**Date**: December 21, 2024  
**Priority**: Critical fixes required immediately  

## 🚨 CRITICAL ACTIONS (Fix Now)

### 1. Fix ultrai-core Service Configuration

**Issue**: Using deprecated Poetry configuration instead of pip  
**Risk**: Service may fail to build or deploy  
**Action**: Update Render dashboard settings

**Steps**:
1. Go to Render dashboard → ultrai-core service
2. Settings → Build & Deploy
3. Update Build Command:
   ```
   FROM: poetry install --no-dev --no-interaction --no-ansi
   TO:   pip install -r requirements-production.txt
   ```
4. Update Start Command:
   ```
   FROM: poetry run uvicorn app_production:app --host 0.0.0.0 --port $PORT --workers 1 --loop uvloop --access-log --log-config monitoring/logging-config.yaml
   TO:   python app_production.py
   ```
5. Save changes and redeploy

### 2. Add Missing Environment Variables

**Issue**: Critical environment variables missing from all backend services  
**Risk**: Services may fail to start or function incorrectly  
**Action**: Add to each service's Environment tab

**Variables to Add**:
```bash
# Add to ALL backend services (ultrai-staging-api, ultrai-prod-api, ultrai-core)
RAG_ENABLED=false
MINIMUM_MODELS_REQUIRED=3
ENABLE_SINGLE_MODEL_FALLBACK=false
ALLOW_PUBLIC_ORCHESTRATION=false

# Add to ultrai-staging-api and ultrai-core (ultrai-prod-api already has these)
JWT_SECRET=<generate-secure-key>
JWT_REFRESH_SECRET=<generate-secure-key>
```

**Steps**:
1. Go to each service → Environment tab
2. Add each variable above
3. For JWT secrets, use: `openssl rand -base64 32`
4. Save changes

### 3. Configure Missing Services

**Issue**: ultrai-frontend and ultrai-demo-ui have no configuration  
**Risk**: Services may not exist or be misconfigured  
**Action**: Create or verify service existence

**Steps**:
1. Check if ultrai-frontend service exists in Render dashboard
2. If exists but misconfigured, update settings
3. If doesn't exist, create new static site service
4. Repeat for ultrai-demo-ui
5. If services are redundant, consider suspending them

---

## ⚠️ HIGH PRIORITY ACTIONS (Fix Within 24 Hours)

### 4. Add API Keys to All Backend Services

**Issue**: All backend services missing LLM API keys  
**Risk**: Services will fail to process requests  
**Action**: Add API keys to Environment tab

**API Keys to Add**:
```bash
# Add to ALL backend services
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
GOOGLE_API_KEY=<your-google-key>
HUGGINGFACE_API_KEY=<your-huggingface-key>
```

**Steps**:
1. Go to each backend service → Environment tab
2. Add each API key
3. Save changes
4. Restart services to apply changes

### 5. Fix Branch Consistency

**Issue**: ultrai-prod-ui uses `production` branch instead of `main`  
**Risk**: Deployment inconsistency  
**Action**: Update branch setting

**Steps**:
1. Go to ultrai-prod-ui service → Settings → Build & Deploy
2. Change Branch from `production` to `main`
3. Save changes

### 6. Verify AutoDeploy Settings

**Issue**: ultrai-core autoDeploy setting unknown  
**Risk**: Unintended deployments  
**Action**: Verify and set correctly

**Expected Settings**:
- **ultrai-staging-api**: `autoDeploy: true` (from main)
- **ultrai-prod-api**: `autoDeploy: false` (manual only)
- **ultrai-core**: `autoDeploy: false` (manual only)

**Steps**:
1. Go to each service → Settings → Build & Deploy
2. Verify Auto-Deploy setting matches expected value
3. Update if incorrect
4. Save changes

---

## 📋 MEDIUM PRIORITY ACTIONS (Fix Within 1 Week)

### 7. Consider Plan Upgrades

**Issue**: Production services on free plan  
**Risk**: Performance limitations  
**Action**: Evaluate upgrade to starter plan

**Services to Consider**:
- ultrai-prod-api
- ultrai-core
- ultrai-prod-ui

**Steps**:
1. Monitor service performance
2. If experiencing limitations, upgrade to starter plan
3. Update billing settings

### 8. Review Service Redundancy

**Issue**: Multiple similar services may be redundant  
**Risk**: Confusion and maintenance overhead  
**Action**: Consolidate or clarify service purposes

**Services to Review**:
- ultrai-frontend vs ultrai-prod-ui
- ultrai-demo vs ultrai-demo-ui
- ultrai-prod-api vs ultrai-core

**Steps**:
1. Document each service's purpose
2. Identify true redundancy
3. Consolidate or suspend redundant services
4. Update documentation

---

## 🔧 VERIFICATION STEPS

### After Each Fix

1. **Check Service Health**:
   ```bash
   # Test each service endpoint
   curl https://ultrai-staging-api.onrender.com/api/health
   curl https://ultrai-prod-api.onrender.com/api/health
   curl https://ultrai-core.onrender.com/health
   ```

2. **Verify Environment Variables**:
   - Check Render dashboard → Environment tab
   - Confirm all required variables are present
   - Verify values are correct

3. **Test Deployment**:
   - Make small change to main branch
   - Verify staging auto-deploys
   - Test manual production deployment

### Final Verification

1. **All Services Healthy**: All 9 services responding correctly
2. **Environment Variables**: All required variables present
3. **Deployment Flow**: Staging auto-deploys, production manual
4. **API Keys**: All backend services have LLM API keys
5. **Health Checks**: All services expose `/health` or `/api/health`

---

## 📊 SUCCESS METRICS

- **Critical Issues**: 0 remaining
- **High Priority Issues**: 0 remaining
- **Service Health**: All services returning 200 OK
- **Deployment Flow**: Working as expected
- **Environment Variables**: 100% compliance

---

## 🚨 ROLLBACK PLAN

If any changes cause issues:

1. **Immediate**: Revert environment variable changes
2. **Build Issues**: Revert build/start command changes
3. **Service Down**: Check Render logs and restore previous configuration
4. **API Issues**: Verify API keys are correct and accessible

**Emergency Contact**: Check Render dashboard logs and service status