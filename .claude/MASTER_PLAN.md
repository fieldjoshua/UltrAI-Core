# 🎯 ULTRA AI - MASTER RECOVERY PLAN
**Generated:** 2025-09-30 02:45 UTC  
**Status:** CRITICAL - Multiple blocking issues identified  
**Goal:** Get system fully functional ASAP with parallel workstreams

---

## 📊 CURRENT STATE ASSESSMENT

### ✅ WORKING
- **Production/Staging APIs:** Health endpoints responding (degraded LLM services)
- **Frontend Build:** Successfully builds to `dist/`
- **Environment Variables:** API keys configured in .env
- **Basic Infrastructure:** FastAPI, React, Vite all functional

### 🔴 BROKEN
- **Local Development:** `/api/orchestrator/analyze` returns 404
- **Frontend:** React Error #310 (minified, need dev build to diagnose)
- **Testing:** venv activation fails in Makefile
- **Render Health Checks:** Missing `/api/health` path in configs
- **Logging:** NoneType crash in `app/utils/logging.py:86`
- **Sentry:** Invalid 'tags' config option causing errors

### ⚠️ DEGRADED
- **LLM Services:** Staging/Prod showing "llm: degraded" status
- **CORS Config:** Using wrong env var name (`CORS_ALLOWED_ORIGINS` vs `CORS_ORIGINS`)
- **Database:** In-memory fallback (no persistence)

---

## 🚀 PARALLEL WORKSTREAM PLAN

### **WORKSTREAM A: Claude (Codebase Fixes)**
*Priority: Critical blocking issues*

#### **A1. Fix Development Server** ⏱️ 15 min
**File:** `app_development.py:211-225`
- Add orchestrator_minimal router import and mount at `/api`
- Test endpoint: `curl http://localhost:8000/api/orchestrator/analyze -X POST -d '{"query":"test"}'`
- **Blocker for:** Local development, testing

#### **A2. Fix Logging NoneType Bug** ⏱️ 5 min  
**File:** `app/utils/logging.py:84-89`
```python
# Current (line 84-89):
if record.exc_info:
    log_data["exception"] = {
        "type": str(record.exc_info[0].__name__),  # ❌ Crashes if exc_info[0] is None
        ...
    }

# Fix:
if record.exc_info and record.exc_info[0]:
    log_data["exception"] = {
        "type": record.exc_info[0].__name__,  # ✅ Safe
        ...
    }
```

#### **A3. Fix Makefile venv Paths** ⏱️ 5 min
**File:** `Makefile:93-116`
- Replace `. venv/bin/activate &&` with `./venv/bin/python -m`
- Test: `make test-offline`

---

### **WORKSTREAM B: GPT-5 Local (Sentry + Config)**
*Priority: Error monitoring and config cleanup*

#### **B1. Find and Fix Sentry Config** ⏱️ 10 min
**Search for:** `Sentry.init` or `sentry_sdk.init`
```bash
grep -r "Sentry.init\|sentry_sdk.init" app/ --include="*.py"
```

**Remove invalid option:**
```python
# Current (causing "Unknown option 'tags'"):
sentry_sdk.init(
    dsn="...",
    tags={"env": "production"},  # ❌ Invalid
    ...
)

# Fixed:
sentry_sdk.init(
    dsn="...",
    environment="production",  # ✅ Correct
    ...
)
```

#### **B2. Verify CORS Configuration** ⏱️ 5 min
**Search for:** `CORS_ALLOWED_ORIGINS` or `CORS_ORIGINS`
```bash
grep -r "CORS.*ORIGIN" app/ --include="*.py"
```

Ensure backend reads `CORS_ORIGINS`:
```python
# app/config.py or app/main.py
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
```

#### **B3. Database URL Check** ⏱️ 5 min
**File:** `app/database/session.py`
- Verify it's reading `DATABASE_URL` from environment
- Confirm in-memory fallback is intentional for dev/staging
- Document if production needs PostgreSQL setup

---

### **WORKSTREAM C: Gemini Cloud (Render Configuration)**
*Priority: Production health and monitoring*

#### **C1. Update Render YAML Files** ⏱️ 10 min
**Files to update:**
- `render-staging.yaml`
- `render-production.yaml`

**Add to both:**
```yaml
services:
  - type: web
    name: ultrai-staging-api  # or ultrai-prod-api
    healthCheckPath: /api/health  # ← ADD THIS
    envVars:
      # Fix CORS var name:
      - key: CORS_ORIGINS  # ← WAS: CORS_ALLOWED_ORIGINS
        value: https://staging-ultrai.onrender.com,http://localhost:5173
```

#### **C2. Document Required Environment Variables** ⏱️ 10 min
**File:** `CLAUDE.md` (add new section)
```markdown
## 🔐 Required Render Environment Variables

### All Services (staging + prod APIs):
- `RAG_ENABLED=false`
- `MINIMUM_MODELS_REQUIRED=3`
- `ENABLE_SINGLE_MODEL_FALLBACK=false`
- `CORS_ORIGINS=<comma-separated-urls>`

### Staging API Only:
- `ALLOW_PUBLIC_ORCHESTRATION=true`
- `JWT_SECRET=<generate-32-char>`
- `JWT_REFRESH_SECRET=<generate-32-char>`

### Production API Only:
- `ALLOW_PUBLIC_ORCHESTRATION=false`
- `DATABASE_URL=<postgres-url>` (if persistence needed)

### All Frontend Services:
- `VITE_RAG_ENABLED=false`
```

#### **C3. Check Render Dashboard Settings** ⏱️ 5 min
Verify in Render Dashboard:
1. `ultrai-staging-api` → Settings → Health Check Path = `/api/health`
2. `ultrai-prod-api` → Settings → Health Check Path = `/api/health`
3. Both APIs have `CORS_ORIGINS` (not `CORS_ALLOWED_ORIGINS`)

#### **C4. Frontend Diagnostics** ⏱️ 10 min
**Run dev build to see full React Error #310:**
```bash
cd /Users/joshuafield/Documents/Ultra/frontend
npm run dev
# Visit http://localhost:5173 and check console
```

**Files to check:**
- `frontend/src/main.tsx` - Root component setup
- `frontend/src/components/ErrorBoundary.tsx` - Error boundary config
- `frontend/src/App.tsx` - Routing and lazy loading

**Report:** Full error message, component/file location, proposed fix

---

## 🔍 POST-FIX VERIFICATION CHECKLIST

### Local Development (Claude + GPT-5 Local)
- [ ] `curl http://localhost:8000/api/orchestrator/analyze -X POST -d '{"query":"test"}'` returns valid response
- [ ] `make test-offline` runs without venv errors
- [ ] Frontend dev build shows no React errors
- [ ] No logging NoneType crashes in `logs/errors.log`

### Render Staging (Gemini Cloud)
- [ ] `curl https://ultrai-staging-api.onrender.com/api/health` returns 200
- [ ] `curl https://ultrai-staging-api.onrender.com/api/orchestrator/status` shows ready status
- [ ] Render dashboard shows green health check indicator
- [ ] No CORS errors when accessing from frontend

### Render Production (Gemini Cloud)
- [ ] `curl https://ultrai-prod-api.onrender.com/api/health` returns 200
- [ ] `curl https://ultrai-prod-api.onrender.com/api/orchestrator/status` shows ready status
- [ ] LLM degraded status resolved (check logs for provider errors)

### Configuration (GPT-5 Local)
- [ ] Sentry errors gone from logs
- [ ] CORS_ORIGINS env var correctly named in all configs
- [ ] DATABASE_URL decision documented

---

## 🎯 CRITICAL PATH DEPENDENCIES

```
┌─────────────────────────────────────────────────────┐
│ PHASE 1: LOCAL FIXES (Claude + GPT-5 Local)        │
│ • Dev server routes (A1)                            │
│ • Logging bug (A2)                                  │
│ • Sentry/CORS fixes (B1-B2)                         │
└─────────────────────────────────────────────────────┘
                    ↓ Enables local testing
┌─────────────────────────────────────────────────────┐
│ PHASE 2: CONFIG UPDATES (Gemini Cloud)             │
│ • Render YAML health checks (C1)                    │
│ • React error diagnosis (C4)                        │
│ • Makefile fixes (A3)                               │
└─────────────────────────────────────────────────────┘
                    ↓ Enables production deploy
┌─────────────────────────────────────────────────────┐
│ PHASE 3: PRODUCTION DEPLOY (Gemini Cloud)           │
│ • Push to GitHub                                    │
│ • Render auto-deploys                               │
│ • Verify health checks                              │
└─────────────────────────────────────────────────────┘
                    ↓ Final validation
┌─────────────────────────────────────────────────────┐
│ PHASE 4: LLM DEGRADATION INVESTIGATION (All)        │
│ • Check Render logs for API key errors              │
│ • Verify provider rate limits                       │
│ • Test orchestrator end-to-end                      │
└─────────────────────────────────────────────────────┘
```

---

## 📝 AGENT TASK ASSIGNMENTS

### 🔵 Claude (YOU) - Start Now:
```
1. Fix app_development.py orchestrator routes (A1)
2. Fix logging.py NoneType guard (A2)
3. Fix Makefile venv paths (A3)
4. Test local endpoints
```

### 🟢 GPT-5 Local Editor - Assign:
```
1. Find and fix Sentry config (B1)
2. Verify CORS config reads CORS_ORIGINS (B2)
3. Check DATABASE_URL fallback logic (B3)
```

### 🟠 Gemini Cloud - Assign:
```
1. Update render-staging.yaml + render-production.yaml (C1)
2. Document required env vars in CLAUDE.md (C2)
3. Add health check paths to Render dashboard (C3)
4. Run frontend dev build and diagnose React Error #310 (C4)
5. Verify CORS_ORIGINS in all Render services (C3)
```

---

## 🚨 KNOWN BLOCKERS

1. **LLM Degraded Status**
   - **Impact:** Orchestrator may fail or timeout
   - **Investigation Needed:** Check Render logs for:
     - `OpenAI API key invalid/missing`
     - `Rate limit exceeded`
     - `Network timeout to provider`

2. **React Error #310**
   - **Impact:** Frontend may crash on certain interactions
   - **Blocker:** Need dev build to see full error (Gemini workstream C4)

3. **No Database Persistence**
   - **Impact:** User data lost on service restart
   - **Decision Needed:** Add PostgreSQL to Render or accept in-memory?

---

## 📞 COORDINATION PROTOCOL

1. **Each agent reports back when task complete:**
   - Post findings in shared space
   - Include any blockers discovered
   - Suggest next steps if applicable

2. **Claude (you) coordinates:**
   - Reviews all agent outputs
   - Resolves conflicts
   - Makes final commit decisions

3. **Critical failures escalate immediately:**
   - If any fix causes new errors, STOP and report
   - Don't push broken code to production

---

## ⏰ ESTIMATED TIMELINE

- **Phase 1 (Local):** 30 minutes (parallel)
- **Phase 2 (Config):** 20 minutes (parallel)
- **Phase 3 (Deploy):** 10 minutes (sequential)
- **Phase 4 (LLM Debug):** 20 minutes (as needed)

**Total:** ~1 hour to functional state (if no unexpected blockers)

---

## 🎉 SUCCESS CRITERIA

System is considered **FUNCTIONAL** when:
- ✅ Local dev server responds to orchestrator requests
- ✅ Frontend loads without React errors
- ✅ All tests pass (`make test-offline`)
- ✅ Staging API health check = 200
- ✅ Production API health check = 200
- ✅ No critical errors in logs (Sentry, logging, CORS)
- ✅ LLM status = healthy (or degradation root cause identified)

---

**Next Action:** Claude starts Workstream A (tasks A1-A3) immediately.