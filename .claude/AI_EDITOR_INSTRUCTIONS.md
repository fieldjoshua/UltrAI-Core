# 🤖 AI EDITOR INSTRUCTIONS
**For:** GPT-5 Local & Gemini Cloud  
**Project:** Ultra AI Recovery Sprint  
**Coordination File:** `.claude/COMMUNAL_TODO.md`

---

## 📍 YOUR ROLE

You are part of a **3-agent team** working in parallel to fix critical issues:
- **🔵 Claude** - Local codebase fixes (orchestrator, logging, Makefile)
- **🟢 GPT-5 Local** - Config & monitoring (Sentry, CORS, database)
- **🟠 Gemini Cloud** - Render deployment & frontend (health checks, React errors)

---

## 📂 KEY FILES TO MONITOR

### 1. Master Plan
**Location:** `.claude/MASTER_PLAN.md`  
**Purpose:** High-level strategy, task breakdown, timeline  
**Check:** Read this first to understand the full scope

### 2. Communal TODO (THIS IS YOUR COORDINATION HUB)
**Location:** `.claude/COMMUNAL_TODO.md`  
**Purpose:** Real-time task tracking, check-ins, blockers  
**Update:** After completing each task using the check-in template

### 3. Project Instructions
**Location:** `CLAUDE.md` (root)  
**Purpose:** How to run the project, test commands, architecture  
**Check:** Before making any changes

---

## 🎯 YOUR TASKS

### 🟢 If you are **GPT-5 Local Editor**:

#### **B1: Fix Sentry Configuration** (Priority: MED)
```bash
# Search for Sentry init
grep -r "Sentry.init\|sentry_sdk.init" app/ --include="*.py"

# Look for invalid 'tags' option
# Replace with 'environment' parameter
```

**Files likely affected:**
- `app/main.py`
- `app/app.py`
- `app/config.py`

**Fix:**
```python
# BEFORE (incorrect):
sentry_sdk.init(
    dsn="...",
    tags={"env": "production"}  # ❌
)

# AFTER (correct):
sentry_sdk.init(
    dsn="...",
    environment="production"  # ✅
)
```

#### **B2: Verify CORS Configuration** (Priority: HIGH)
```bash
# Search for CORS config
grep -r "CORS.*ORIGIN" app/ --include="*.py"
```

**Check:**
- Backend reads `CORS_ORIGINS` (not `CORS_ALLOWED_ORIGINS`)
- Value comes from `os.getenv("CORS_ORIGINS")`
- Properly split by comma: `.split(",")`

**Files to check:**
- `app/config.py`
- `app/main.py`
- `app_development.py`
- `app_production.py`

#### **B3: Database URL Check** (Priority: MED)
**File:** `app/database/session.py`

**Verify:**
- Reads `DATABASE_URL` from environment
- Has fallback to in-memory SQLite
- Document if production needs PostgreSQL

**Report in check-in:**
- Current behavior
- Recommendation for production

---

### 🟠 If you are **Gemini Cloud**:

#### **C1: Update Render YAML Files** (Priority: HIGH)
**Files:**
- `render-staging.yaml`
- `render-production.yaml`

**Add to both:**
```yaml
services:
  - type: web
    name: ultrai-staging-api  # (or ultrai-prod-api)
    healthCheckPath: /api/health  # ← ADD THIS LINE
    envVars:
      - key: CORS_ORIGINS  # ← CHANGE FROM CORS_ALLOWED_ORIGINS
        value: https://staging-ultrai.onrender.com,http://localhost:5173
```

#### **C2: Document Environment Variables** (Priority: MED)
**File:** `CLAUDE.md` (add new section)

**Add this section:**
```markdown
## 🔐 Required Render Environment Variables

### All API Services (staging + prod):
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
- `DATABASE_URL=<postgres-url>` (optional)

### All Frontend Services:
- `VITE_RAG_ENABLED=false`
```

#### **C3: Update Render Dashboard** (Priority: HIGH)
**Manual steps in Render dashboard:**

1. Go to `ultrai-staging-api` → Settings
   - Find "Health Check Path"
   - Set to: `/api/health`
   - Save changes

2. Go to `ultrai-prod-api` → Settings
   - Find "Health Check Path"
   - Set to: `/api/health`
   - Save changes

3. Verify both services:
   - Environment tab has `CORS_ORIGINS` (not `CORS_ALLOWED_ORIGINS`)
   - If wrong, rename the variable

#### **C4: Diagnose React Error #310** (Priority: HIGH)
**Steps:**
```bash
cd /Users/joshuafield/Documents/Ultra/frontend
npm run dev
# Open http://localhost:5173 in browser
# Check browser console for full error
```

**Files to investigate:**
- `frontend/src/main.tsx`
- `frontend/src/components/ErrorBoundary.tsx`
- `frontend/src/App.tsx`

**React Error 310 typically means:**
- Hydration mismatch (SSR/client difference)
- Missing component in lazy-loaded chunk
- Invalid React element type
- Circular dependency

**Report in check-in:**
- Full error message from console
- File/component where error occurs
- Proposed fix (code snippet if possible)

---

## ✅ HOW TO CHECK IN

**After completing each task:**

1. Open `.claude/COMMUNAL_TODO.md`
2. Find your agent section under "📬 AGENT CHECK-INS"
3. Update using this template:

```markdown
### 🟢 GPT-5 Local - 2025-09-30 03:15 UTC
**Completed:** B1, B2  
**Status:** Fixed Sentry config in app/main.py (line 45), verified CORS reads CORS_ORIGINS in app/config.py  
**Findings:** Sentry was using deprecated 'tags' option. CORS config was correct but needs env var rename in Render.  
**Next:** Starting B3 (database check)  
**Blockers:** None
```

4. Update task status in the task table from `⏳ TODO` to `✅ DONE`
5. Update progress tracker percentages

---

## 🚨 IF YOU GET BLOCKED

**STOP immediately and:**
1. Update your status to `🔴 BLOCKED`
2. Add blocker details in your check-in
3. Don't proceed if it could break production
4. Suggest alternative approach if possible

**Example:**
```markdown
### 🟠 Gemini Cloud - 2025-09-30 03:20 UTC
**Completed:** C1  
**Status:** 🔴 BLOCKED on C3  
**Findings:** Cannot access Render dashboard - credentials needed  
**Next:** Waiting for dashboard access  
**Blockers:** No Render account credentials provided
```

---

## 📊 VERIFICATION COMMANDS

**After you make changes, verify with these:**

### Local Development Checks
```bash
# Test dev server
curl http://localhost:8000/api/orchestrator/analyze -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# Run tests
make test-offline

# Check logs for errors
tail -f logs/errors.log
```

### Render Production Checks
```bash
# Staging health
curl https://ultrai-staging-api.onrender.com/api/health

# Production health
curl https://ultrai-prod-api.onrender.com/api/health

# Orchestrator status
curl https://ultrai-staging-api.onrender.com/api/orchestrator/status
```

---

## 🎯 SUCCESS CRITERIA

**Your tasks are complete when:**

### GPT-5 Local:
- [ ] No Sentry "Unknown option 'tags'" errors in logs
- [ ] All CORS config uses `CORS_ORIGINS` variable
- [ ] Database URL behavior documented

### Gemini Cloud:
- [ ] Both Render YAMLs have `healthCheckPath: /api/health`
- [ ] Render dashboard shows green health indicators
- [ ] React Error #310 diagnosed with fix recommendation
- [ ] Environment variables documented in CLAUDE.md

---

## 🤝 COORDINATION TIPS

1. **Check COMMUNAL_TODO.md before starting** - Someone else may have already done your task
2. **Update frequently** - Even partial progress is worth noting
3. **Flag dependencies** - If your task depends on another agent's work
4. **Share discoveries** - Found something unexpected? Document it!
5. **Ask questions** - Better to clarify than assume

---

## 📞 CONTACT

**If you need human intervention:**
- Tag Joshua in check-in
- Mark status as `🔴 BLOCKED`
- Be specific about what you need

---

**Good luck! Let's get Ultra AI functional! 🚀**