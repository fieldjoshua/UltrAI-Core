# 🟠 GEMINI CLOUD - Render Dashboard Verification

**Status:** Ready to start  
**Priority:** 🔴 HIGH (D3) + 🟡 MEDIUM (C3, C4)  
**Estimated time:** 20-30 minutes  
**Risk level:** LOW (read-only verification, no changes unless approved)

---

## Task D3: Verify Render API Keys Configuration 🔴 HIGH

**Why this is critical:** Production still shows `"llm": "degraded"` after our fix. Most likely cause is missing/invalid API keys in Render.

### Steps:

1. **Log into Render dashboard**
   - URL: https://dashboard.render.com
   - Use Joshua's account

2. **Check `ultrai-staging-api` service**
   - Navigate to service → Environment tab
   - Verify these keys exist and look valid:
     - `OPENAI_API_KEY` - Should start with `sk-proj-` or `sk-`
     - `ANTHROPIC_API_KEY` - Should start with `sk-ant-`
     - `GOOGLE_API_KEY` - Should be alphanumeric Google AI key
     - `HUGGINGFACE_API_KEY` - Optional, check if present

3. **Check `ultrai-prod-api` service**
   - Repeat step 2 for production

4. **Test suspicious keys (if any look wrong)**
   ```bash
   # OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_KEY_HERE"
   # Should return JSON with model list
   
   # Anthropic
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: YOUR_KEY_HERE" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   # Should return JSON response (not 401/403)
   
   # Google
   curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_KEY_HERE"
   # Should return JSON with model list
   ```

### Report format:

```markdown
## D3: Render API Keys Verification Results

### Staging (`ultrai-staging-api`)
- ✅/❌ OPENAI_API_KEY: [configured/missing/invalid]
- ✅/❌ ANTHROPIC_API_KEY: [configured/missing/invalid]
- ✅/❌ GOOGLE_API_KEY: [configured/missing/invalid]
- ✅/❌ HUGGINGFACE_API_KEY: [configured/missing/not needed]

### Production (`ultrai-prod-api`)
- ✅/❌ OPENAI_API_KEY: [configured/missing/invalid]
- ✅/❌ ANTHROPIC_API_KEY: [configured/missing/invalid]
- ✅/❌ GOOGLE_API_KEY: [configured/missing/invalid]
- ✅/❌ HUGGINGFACE_API_KEY: [configured/missing/not needed]

### Issues Found:
[List any missing/invalid keys]

### API Test Results:
[If you tested keys, paste results here]

### Recommendation:
[What needs to be fixed]
```

---

## Task C3: Verify Health Check Paths 🟡 MEDIUM

### Steps:

1. In Render dashboard → `ultrai-staging-api` → Settings
2. Find "Health Check Path" field
3. Should be: `/api/health`
4. If wrong/missing: Update and save (triggers redeploy)
5. Repeat for `ultrai-prod-api`
6. Wait 5 minutes for redeploy
7. Verify green health indicators in service list

### Report format:

```markdown
## C3: Health Check Paths Verification

- **Staging:** `/api/health` [✅ correct / ❌ was wrong, fixed]
- **Production:** `/api/health` [✅ correct / ❌ was wrong, fixed]
- **Health indicators:** [Green/Yellow/Red]
```

---

## Task C4: Diagnose React Error #310 🟡 MEDIUM

**Error message:** "Minified React error #310"  
**Location:** Frontend production build

### Steps:

1. **Run dev build locally:**
   ```bash
   cd /path/to/Ultra/frontend
   npm run dev
   ```

2. **Open browser:** http://localhost:5173

3. **Open DevTools console** (F12)

4. **Reproduce error:**
   - Navigate through the app
   - Look for any error messages
   - Take screenshots

5. **Decode the error:**
   - Visit: https://reactjs.org/docs/error-decoder.html?invariant=310
   - Or check console for full error in dev mode

6. **Investigation checklist:**
   - Which component is failing?
   - Is it a hydration mismatch?
   - Missing lazy-loaded components?
   - Check `frontend/src/main.tsx` for issues
   - Check `frontend/src/App.tsx` for routing problems

### Report format:

```markdown
## C4: React Error #310 Diagnosis

### Full Error Message:
[Paste full error from dev console]

### Root Cause:
[What's causing the error]

### Affected Component:
[File path and component name]

### Proposed Fix:
[Code snippet or steps to fix]

### Files to Change:
- `frontend/src/...`
```

---

## Deliverables

When complete, create a single report file:

```bash
# Save as .claude/GEMINI_REPORT.md
```

---

## Priority Order

1. **D3 first** - Most critical, explains production degraded status
2. **C3 second** - Quick check, may already be correct
3. **C4 third** - Less critical, can defer if time-limited

---

## Notes

- All tasks are **read-only verification** except:
  - C3 health check path (safe to fix if wrong)
- **DO NOT** modify API keys without approval
- If you find issues, report them - don't fix yet
- Update `.claude/COMMUNAL_TODO.md` when done