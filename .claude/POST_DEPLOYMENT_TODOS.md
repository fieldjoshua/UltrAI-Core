# 📋 Post-Deployment TODO List
**Created:** 2025-09-30 03:40 UTC  
**Status:** 10 tasks pending  
**Context:** Follow-up from Multi-Agent Recovery Sprint (PR #47)

---

## 🔴 HIGH PRIORITY (Urgent)

### D1: Investigate LLM Degraded Status
**Status:** ⏳ TODO  
**Owner:** Unassigned  
**Context:** Both staging and production showing `"llm": "degraded"`

**Steps:**
1. Check Render logs for `ultrai-staging-api`:
   ```bash
   # Via Render dashboard → ultrai-staging-api → Logs
   # Look for errors containing: "API key", "rate limit", "provider"
   ```
2. Check Render logs for `ultrai-prod-api`
3. Common causes:
   - Invalid/expired API keys
   - Rate limiting from providers
   - Network/firewall issues
   - Provider service outages

**Expected Fix:**
- Verify API keys in Render dashboard
- Update expired keys if needed
- Check provider status pages (OpenAI, Anthropic, Google)

---

### D2: Fix Staging Orchestrator Timeout
**Status:** ⏳ TODO  
**Owner:** Unassigned  
**Context:** `GET /api/orchestrator/status` times out after 60+ seconds on staging

**Steps:**
1. Check staging logs for timeout errors
2. Compare staging vs production configuration differences
3. Possible causes:
   - Database connection pooling issues
   - Synchronous health checks blocking
   - LLM provider health checks timing out
   - Insufficient resources (free tier)

**Potential Fixes:**
- Make health checks async with timeout
- Increase orchestrator initialization timeout
- Cache provider health status
- Add circuit breaker for slow providers

**File to check:** `app/services/orchestration_service.py`

---

### D3: Verify Render API Keys Configuration
**Status:** ⏳ TODO  
**Owner:** Unassigned  

**Steps:**
1. Go to Render dashboard
2. Check `ultrai-staging-api` → Environment:
   - `OPENAI_API_KEY` (should start with `sk-proj-` or `sk-`)
   - `ANTHROPIC_API_KEY` (should start with `sk-ant-`)
   - `GOOGLE_API_KEY` (should be valid)
   - `HUGGINGFACE_API_KEY` (optional)
3. Check `ultrai-prod-api` → Environment (same keys)
4. Test each key manually if needed:
   ```bash
   curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

---

## 🟡 MEDIUM PRIORITY (Finish Original Tasks)

### B3: Document DATABASE_URL Fallback Logic
**Status:** ⏳ TODO  
**Owner:** GPT-5 Local (original assignment)  

**Task:** Add to `CLAUDE.md`:
```markdown
## 🗄️ Database Configuration

### Development
- **Default:** In-memory SQLite (no persistence)
- **Location:** Not persisted, recreates on restart
- **Use case:** Local development, fast iteration

### Production
- **Recommended:** PostgreSQL via DATABASE_URL
- **Configuration:** Set `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
- **Render setup:** Database service linked in render.yaml
- **Fallback:** If DATABASE_URL not set, falls back to SQLite (not recommended for production)

### Connection Pool Settings
- Free tier: Max 2 connections
- Paid tier: Adjust in `app/database/session.py`
```

**File to edit:** `CLAUDE.md` (add section around line 100)

---

### C2: Document Required Environment Variables
**Status:** ⏳ TODO  
**Owner:** Gemini Cloud (original assignment)  

**Task:** Expand env vars section in `CLAUDE.md` to include all variables from render YAMLs:

```markdown
## 🔐 Complete Environment Variable Reference

### Required for LLM Functionality
- `OPENAI_API_KEY` - OpenAI API key (get from platform.openai.com)
- `ANTHROPIC_API_KEY` - Anthropic API key (get from console.anthropic.com)
- `GOOGLE_API_KEY` - Google AI API key (get from ai.google.dev)

### Core Configuration
- `ENVIRONMENT` - Environment name (development|staging|production)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Enable debug mode (true|false)

### Feature Flags
- `RAG_ENABLED` - Enable document endpoints (default: false)
- `ENABLE_AUTH` - Enable JWT authentication (default: false)
- `ENABLE_RATE_LIMIT` - Enable rate limiting (default: false)
- `ENABLE_BILLING` - Enable billing features (default: false)
- `ENABLE_PRICING` - Enable pricing features (default: false)

### Database & Caching
- `DATABASE_URL` - PostgreSQL connection string (optional, falls back to SQLite)
- `REDIS_URL` - Redis connection string (optional, falls back to in-memory)

### Security
- `JWT_SECRET_KEY` - JWT signing secret (auto-generated if not set)
- `JWT_REFRESH_SECRET` - JWT refresh token secret (auto-generated if not set)
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins

### Orchestration
- `CONCURRENT_EXECUTION_TIMEOUT` - Max synthesis time in seconds (default: 70)
- `MINIMUM_MODELS_REQUIRED` - Minimum models for orchestration (default: 3)
- `ENABLE_SINGLE_MODEL_FALLBACK` - Fallback to single model if min not met (default: false)

### Frontend
- `VITE_API_URL` - Backend API URL for frontend
- `VITE_API_MODE` - API mode (live|mock)
- `VITE_RAG_ENABLED` - Show document features in UI (default: false)
- `VITE_DEFAULT_SKIN` - Default theme (night|morning|afternoon|sunset|minimalist|business)
```

**File to edit:** `CLAUDE.md` (replace existing env vars section)

---

### C3: Verify Health Check Paths in Render Dashboard
**Status:** ⏳ TODO  
**Owner:** Gemini Cloud / Manual verification  

**Task:** Manual verification via Render dashboard

**Steps:**
1. Log into https://dashboard.render.com
2. Check `ultrai-staging-api` service:
   - Settings → Health Check Path
   - Should be: `/api/health`
   - If missing/wrong: Update and save
3. Check `ultrai-prod-api` service:
   - Settings → Health Check Path
   - Should be: `/api/health`
   - If missing/wrong: Update and save
4. After saving, services will redeploy
5. Verify green health indicator appears in dashboard

**Expected Result:** Both services show green health indicator

---

### C4: Diagnose React Error #310
**Status:** ⏳ TODO  
**Owner:** Gemini Cloud (original assignment)  

**Task:** Run dev build to see full error message

**Steps:**
```bash
cd /Users/joshuafield/Documents/Ultra/frontend
npm run dev
# Open http://localhost:5173
# Check browser console for full React Error #310 message
```

**Error #310 typically means:**
- Hydration mismatch (SSR vs client rendering)
- Invalid React element type
- Missing component in lazy load
- Circular dependency

**Files to investigate:**
- `frontend/src/main.tsx` - Root setup
- `frontend/src/App.tsx` - Routing
- `frontend/src/components/ErrorBoundary.tsx` - Error handling

**Report:**
- Full error message from console
- Component/file where error occurs
- Proposed fix with code snippet

---

## 🟢 LOW PRIORITY (Polish & Monitoring)

### Task 8: Run Full Test Suite Locally
**Status:** ⏳ TODO  

**Command:**
```bash
cd /Users/joshuafield/Documents/Ultra
source venv/bin/activate
make test-offline
```

**Expected:** All tests pass or only known failures

**If tests fail:**
- Document which tests are failing
- Determine if failures are due to our changes
- Create follow-up tasks for test fixes

---

### Task 9: Set Up LLM Health Monitoring
**Status:** ⏳ TODO  

**Suggestions:**
1. Add Sentry alert for repeated LLM degradation
2. Create Render cron job to check `/api/health` every 5 minutes
3. Set up UptimeRobot or similar service
4. Add Slack webhook for critical health changes

**Future Enhancement:** Implement in `app/services/provider_health_manager.py`

---

### Task 10: Update COMMUNAL_TODO.md
**Status:** ⏳ TODO  

**Task:** Update the communal TODO with post-deployment findings

**Already done partially** - just needs final completion stats:
- Mark all original tasks as verified
- Add deployment verification results
- Document new issues discovered (D1, D2, D3)
- Close out the sprint with final metrics

---

## 📊 Progress Tracking

**Total Tasks:** 10  
**Completed:** 0  
**In Progress:** 0  
**Pending:** 10  

**By Priority:**
- 🔴 HIGH: 3 tasks (D1, D2, D3)
- 🟡 MED: 4 tasks (B3, C2, C3, C4)
- 🟢 LOW: 3 tasks (8, 9, 10)

---

## 🎯 Suggested Assignment

**For immediate attention (next 1-2 hours):**
1. **D1 + D3** - Investigate LLM degradation (can be done together)
2. **D2** - Fix staging timeout (debugging required)

**For completion (next day):**
3. **B3, C2** - Documentation tasks (straightforward)
4. **C3** - Manual Render verification (5 minutes)
5. **C4** - React error diagnosis (requires local dev environment)

**For polish (when time permits):**
6. **Tasks 8-10** - Testing, monitoring, cleanup

---

**Next Action:** Start with D1 (LLM investigation) since it affects both staging and production.