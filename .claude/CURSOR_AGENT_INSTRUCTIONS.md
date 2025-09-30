# 🤖 Cursor Multi-Agent Setup Instructions

## Background Agent Support in Cursor

Cursor supports running multiple Composer instances simultaneously in different tabs.

---

## Setup Instructions

### Option 1: Multiple Composer Tabs (Recommended)

1. **Open Cursor** on this project: `/Users/joshuafield/Documents/Ultra`

2. **Create GPT-5 Agent (Documentation)**
   - Press `Cmd+I` to open Composer
   - In the Composer input, paste:
   ```
   Read the file `.claude/GPT5_TASKS.md` and complete both tasks (B3 and C2).
   
   When done, create a report file at `.claude/GPT5_REPORT.md` with:
   - What you changed
   - Line numbers
   - Verification that formatting matches existing style
   
   Update `.claude/COMMUNAL_TODO.md` to mark B3 and C2 as completed.
   ```
   - Click "Start" or press Enter
   - **Keep this tab open**

3. **Create Gemini Agent (Render Verification)**
   - Open a **new Composer tab** (Click + next to existing Composer tab, or `Cmd+Shift+I`)
   - In the new Composer input, paste:
   ```
   Read the file `.claude/GEMINI_TASKS.md` and complete tasks in this order:
   1. D3 (HIGH priority - Render API keys verification)
   2. C3 (Health check paths)
   3. C4 (React error diagnosis) - if time permits
   
   For D3: You'll need to manually check Render dashboard at https://dashboard.render.com
   - I cannot access external dashboards, so report what steps the user should take
   - Create a checklist for manual verification
   
   When done, create a report file at `.claude/GEMINI_REPORT.md` with your findings.
   
   Update `.claude/COMMUNAL_TODO.md` to mark D3, C3, and C4 as completed (or note blockers).
   ```
   - Click "Start" or press Enter
   - **Keep this tab open**

4. **Monitor Progress**
   - Both agents will run in parallel
   - Watch for file changes in `.claude/` directory
   - Check for completion reports

---

### Option 2: Cursor Rules (Automatic Background Tasks)

If your Cursor version supports `.cursorrules` automation:

1. **Create background task file:**
   ```bash
   cat > .cursorrules << 'EOF'
   # Background Documentation Agent
   - Auto-update CLAUDE.md with database and env var documentation
   - Monitor .claude/GPT5_TASKS.md for new documentation tasks
   - Report completion in .claude/GPT5_REPORT.md
   EOF
   ```

2. This is experimental - most Cursor versions don't support true background agents yet.

---

### Option 3: Manual Coordination (No Agent Mode)

If Cursor doesn't support parallel agents:

1. **Do GPT-5 tasks first (Documentation):**
   - Open Composer
   - Point to `.claude/GPT5_TASKS.md`
   - Let it complete B3 + C2
   - Wait for completion

2. **Then do Gemini tasks (Verification):**
   - Same Composer or new tab
   - Point to `.claude/GEMINI_TASKS.md`
   - Note: D3 requires manual Render dashboard access
   - Complete what's automatable (C4 React error)

---

## Current Cursor Composer Capabilities

**Confirmed to work:**
- ✅ Multiple Composer tabs open simultaneously
- ✅ Each tab runs independently
- ✅ Can edit files in parallel (as long as no conflicts)
- ✅ File watching and auto-refresh

**Limitations:**
- ❌ No true "background" execution (needs tabs open)
- ❌ Can't access external services (Render dashboard)
- ❌ Manual coordination needed to prevent file conflicts

---

## Recommended Approach for This Project

**Use Multiple Composer Tabs:**

1. **Tab 1 (GPT-5):** Documentation tasks - low conflict risk
2. **Tab 2 (Gemini):** Read-only verification + React debugging
3. **Claude Code (you/me):** Monitor Render deployment, coordinate results

**Conflict prevention:**
- GPT-5 only edits `CLAUDE.md`
- Gemini only edits `.claude/GEMINI_REPORT.md`
- No file overlap = no conflicts

---

## What to do now

1. Open Cursor on this project
2. Open 2 Composer tabs with the instructions above
3. Let me know when both agents have started
4. I'll monitor for completion and coordinate the results

---

## Alternative: I can do it sequentially

If Cursor multi-agent doesn't work well, I can:
- Handle GPT-5 tasks myself (documentation)
- You manually verify Render dashboard (D3)
- I'll do C4 (React error debugging)

Just let me know which approach you prefer!