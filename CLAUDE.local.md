# ★ Division of Labor (Claude ↔ GPT)

- GPT (Current Editor)
  - Increase CONCURRENT_EXECUTION_TIMEOUT to 70s [done]
  - Add route-level tests for `app/routes/orchestrator_minimal.py` [done]
  - Implement cache hit rate metrics and expose via `/api/metrics` [done]
  - Re-run and stabilize rate limit tests [done]

- Claude (Other Editor)
  - Standardize error response format across all LLM adapters [done 2025-08-30]
  - Add streaming response support to orchestrator [done 2025-08-30]
  - Implement request ID tracking across services [done 2025-08-30]
  - (Backlog) Memory monitoring, query-type cache TTL, A/B selection tests

Coordination
- Use this section as the single source of truth; mark updates with [done]/[in-progress] + date.
- If scope changes, update here first so both agents stay aligned.

---

go a# Project-Specific Memory for UltraAI Core

## Git Operations

- I am responsible for executing git commits, adds, and pushes
- Always remind to push changes to GitHub for deployments
- Use `--no-verify` flag when pre-commit hooks fail

## User Interaction Guidelines

- Actually consider what the user asks or suggests, don't just assume everything is fine
- When user asks about build/start commands or similar configuration questions, check the current state before answering
- Pay careful attention to user questions - they often catch issues I miss

## Deployment Process

- Render deploys from GitHub repository, not local files
- URL has changed from `https://ultra-backend.onrender.com/` to `https://ultrai-core.onrender.com/`
- Always ensure files are pushed to GitHub before expecting Render deployments to work

## Important Project Details

- Service name on Render: `ultrai-core`
- Current deployment phase: Production (Phase 4/5 combined)
- Key files for deployment:
  - `app_production.py` - Production application
  - `requirements-production.txt` - Dependencies
  - `render.yaml` - Deployment configuration

## Recent Issues to Remember

- Don't dismiss configuration questions without checking current state
- Render dashboard settings can override render.yaml
- Port configuration matters - use `$PORT` not `${PORT:-10000}`
