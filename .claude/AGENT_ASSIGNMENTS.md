# 🤖 Agent Task Assignments - Post-Deployment Sprint
**Created:** 2025-09-30 03:45 UTC  
**Coordinator:** Claude  
**Status:** Active - 3 agents working in parallel

---

## 🔵 CLAUDE (Primary - LLM Investigation)
**Status:** 🏃 Active  
**Priority:** 🔴 HIGH

### Assigned Tasks
- **D1:** Investigate LLM degraded status
  - Check codebase for API key configuration issues
  - Review LLM adapter initialization code
  - Analyze provider health check logic
  - Propose fixes for degraded status

**Working Files:**
- `app/services/llm_adapters.py`
- `app/services/provider_health_manager.py`
- `app/config.py`

**Deliverable:** Root cause analysis + proposed fix

---

## 🟢 GPT-5 LOCAL (Documentation Tasks)
**Status:** 📋 Ready for assignment  
**Priority:** 🟡 MEDIUM

### Assigned Tasks

#### **B3: Document DATABASE_URL Fallback Logic**
**File:** `CLAUDE.md` (add section around line 100)

**Content to add:**
```markdown
## 🗄️ Database Configuration

### Development
- **Default:** In-memory SQLite (no persistence)
- **Location:** Not persisted, recreates on restart
- **Use case:** Local development, fast iteration

### Staging/Production
- **Recommended:** PostgreSQL via DATABASE_URL
- **Configuration:** Set `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
- **Render setup:** Database service linked in render.yaml files
- **Connection pooling:** Configured in `app/database/session.py`
  - Free tier: Max 2 connections
  - Paid tier: Configurable pool size

### Fallback Behavior
- If `DATABASE_URL` not set → Falls back to SQLite
- SQLite location: `./ultra.db` (not recommended for production)
- Data persistence: SQLite data lost on container restart in cloud environments

### Checking Current Database
```bash
# In Python shell
from app.database.session import engine
print(engine.url)
```
```

#### **C2: Document Complete Environment Variables**
**File:** `CLAUDE.md` (expand existing env vars section ~line 85-104)

**Task:** Replace the current env vars section with the comprehensive reference from `.claude/POST_DEPLOYMENT_TODOS.md` (lines 75-118)

**Include sections:**
- Required for LLM Functionality
- Core Configuration  
- Feature Flags
- Database & Caching
- Security
- Orchestration
- Frontend

**Format:** Keep consistent with existing CLAUDE.md style (code blocks, emojis, clear headers)

---

## 🟠 GEMINI CLOUD (Render Dashboard + Frontend Debug)
**Status:** 📋 Ready for assignment  
**Priority:** 🟡 MEDIUM to 🔴 HIGH

### Assigned Tasks

#### **D3: Verify Render API Keys Configuration** 🔴 HIGH
**Task:** Manual verification in Render dashboard

**Steps:**
1. Log into https://dashboard.render.com
2. Navigate to `ultrai-staging-api` service
3. Go to Environment tab
4. Verify these keys are set and valid:
   - `OPENAI_API_KEY` - Should start with `sk-proj-` or `sk-`
   - `ANTHROPIC_API_KEY` - Should start with `sk-ant-`
   - `GOOGLE_API_KEY` - Valid Google AI key
   - `HUGGINGFACE_API_KEY` - Optional but check if present
5. Repeat for `ultrai-prod-api` service
6. **Test keys if suspicious:**
   ```bash
   # OpenAI
   curl https://api.openai.com/v1/models -H "Authorization: Bearer $KEY"
   # Anthropic  
   curl https://api.anthropic.com/v1/messages -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01"
   # Google
   curl "https://generativelanguage.googleapis.com/v1/models?key=$KEY"
   ```

**Report:**
- Which keys are missing/invalid?
- Any error messages from API tests?
- Are keys synced between staging and production?

---

#### **C3: Verify Health Check Paths** 🟡 MED
**Task:** Quick manual verification

**Steps:**
1. In Render dashboard → `ultrai-staging-api` → Settings
2. Find "Health Check Path" field
3. Should be: `/api/health`
4. If wrong/missing: Update and save (triggers redeploy)
5. Repeat for `ultrai-prod-api`
6. Wait 5 minutes for redeploy
7. Verify green health indicators in service list

---

#### **C4: Diagnose React Error #310** 🟡 MED
**Task:** Run dev build and capture full error

**Local steps:**
```bash
cd /Users/joshuafield/Documents/Ultra/frontend
npm run dev
# Open http://localhost:5173 in browser
# Open DevTools console
# Reproduce error if not immediately visible
# Screenshot or copy full error message
```

**Investigation checklist:**
- [ ] Full error stack trace captured
- [ ] Which component is failing?
- [ ] Is it hydration mismatch?
- [ ] Any missing lazy-loaded components?
- [ ] Check `frontend/src/main.tsx` for issues
- [ ] Check `frontend/src/App.tsx` for routing problems

**Files to review:**
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/ErrorBoundary.tsx`

**Deliverable:** 
- Full error message
- Root cause analysis
- Proposed fix with code snippet

---

## 🎯 BACKGROUND AGENT (Autonomous Tasks)
**Status:** 🤖 Autonomous - No human intervention needed  
**Priority:** 🟢 LOW to 🟡 MED

### Auto-Assigned Tasks

#### **Task 8: Run Test Suite Verification**
```bash
cd /Users/joshuafield/Documents/Ultra
source venv/bin/activate
make test-offline > .claude/test_results.log 2>&1
# Parse results
# Report: X passed, Y failed, Z skipped
```

#### **Task 10: Update COMMUNAL_TODO Final Stats**
- Count completed tasks: 10/14 original + 3 new = 13 tasks
- Calculate success rate: ~85%
- Document deployment outcome
- Archive completed tasks section
- Set status to "Sprint Complete - Follow-up in progress"

#### **Code Quality Scan**
```bash
ruff check . --output-format=json > .claude/ruff_report.json
cd frontend && npm run lint > ../.claude/eslint_report.txt 2>&1
```

#### **Generate Dependency Report**
```bash
pip list > .claude/python_deps.txt
cd frontend && npm list --depth=0 > ../.claude/npm_deps.txt
```

---

## 📊 COORDINATION PROTOCOL

### Check-In Format
Each agent updates their section when tasks complete:

```markdown
### ✅ [Agent Name] - [Timestamp]
**Completed:** [Task IDs]
**Status:** [What was done]
**Findings:** [Key discoveries]
**Blockers:** [Any issues]
**Next:** [What's next]
```

### Escalation Rules
- 🔴 **Blocker found?** Update status immediately, don't proceed
- ⚠️ **Uncertain about fix?** Propose solution, wait for review
- ✅ **Task complete?** Update COMMUNAL_TODO.md and move to next

### File Coordination
- **GPT-5** edits `CLAUDE.md` only
- **Gemini** provides reports (no code changes without approval)
- **Claude** edits code files in `app/` directory
- **Background Agent** only writes to `.claude/` reports

---

## 🎯 SUCCESS CRITERIA

### By End of Session
- [ ] D1 - Root cause of LLM degradation identified
- [ ] D3 - API keys verified/fixed in Render
- [ ] B3 + C2 - Documentation complete in CLAUDE.md
- [ ] C3 - Health checks verified in Render
- [ ] C4 - React error diagnosed with proposed fix
- [ ] Background tasks - Reports generated

### Quality Gates
- No merge conflicts in CLAUDE.md (GPT-5 + Claude coordination)
- All code changes linted and tested locally before commit
- Render changes verified to not break existing deployments
- Documentation changes reviewed for accuracy

---

## 📝 AGENT INSTRUCTIONS

### For GPT-5 Local:
Read `.claude/POST_DEPLOYMENT_TODOS.md` sections for B3 and C2. Edit `CLAUDE.md` with the content specified. Use the check-in format above when done.

### For Gemini Cloud:
Read `.claude/POST_DEPLOYMENT_TODOS.md` sections for D3, C3, and C4. Execute steps in order of priority (D3 first). Report findings using check-in format.

### For Background Agent:
Execute tasks 8 and 10 autonomously. Generate reports in `.claude/` directory. No human interaction needed unless errors occur.

---

**Coordinator (Claude) will:**
1. Start D1 investigation immediately
2. Monitor agent check-ins
3. Resolve conflicts if multiple agents edit same files
4. Merge all work and create summary PR when complete

**Estimated completion time:** 1-2 hours for all parallel tasks