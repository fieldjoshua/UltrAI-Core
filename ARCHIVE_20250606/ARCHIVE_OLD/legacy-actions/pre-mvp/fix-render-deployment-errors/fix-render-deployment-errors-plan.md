# ACTION: fix-render-deployment-errors

Version: 1.1
Last Updated: 2025-05-17
Status: Phase 1 Complete
Progress: 60%

## Objective

Systematically fix all deployment errors on Render by creating a minimal working deployment and gradually adding complexity.

## Problem Statement

The current deployment is failing with multiple errors:

1. Missing dependencies (psutil)
2. Syntax errors in Python files
3. Import errors and module conflicts
4. Configuration issues

Playing "whack-a-mole" with individual errors is inefficient. We need a strategic approach.

## Success Criteria

1. A minimal app deploys successfully to Render
2. Health check endpoint responds with status 200
3. Gradually add features without breaking deployment
4. Document each working configuration
5. All MVP features eventually work in production

## Task Tracking

All tasks are tracked within this ACTION PLAN only. No external TODO lists are maintained.

### Current Tasks

- [x] Get ACTION plan approved by Joshua Field
- [x] Create ultra-minimal app.py with no backend dependencies (app_health_only.py created)
- [x] Test minimal app locally
- [x] Fix render.yaml to use Python runtime instead of Docker
- [x] Fix syntax error in base_orchestrator.py
- [x] Update render.yaml to use minimal configuration
- [x] Create scripts/start-render-minimal.sh for minimal deployment
- [x] Configure render.yaml to use minimal start script
- [x] Identify issue: Render dashboard overrides render.yaml
- [x] Update Render dashboard Build & Start commands
- [x] Monitor deployment status on Render
- [x] Verify health check endpoint responds with status 200
- [x] Document working minimal deployment configuration

### Phase 2 Tasks - Add Core Dependencies

- [x] Create requirements-phase2.txt with database dependencies
- [x] Create app_with_database.py with database health check
- [x] Test database connectivity locally (returns appropriate messages)
- [ ] Update Render dashboard to use new files
- [ ] Deploy and verify database connection
- [ ] Add Redis support
- [ ] Test Redis connectivity
- [ ] Deploy and verify Redis connection
- [ ] Document working configuration with database and Redis

## Approach

### Phase 1: Ultra-Minimal Deployment (Day 1) ✓ COMPLETE

1. Create `app_health_only.py` with just health endpoints ✓
2. Create `requirements-ultra-minimal.txt` with only FastAPI/Uvicorn ✓
3. Update render-prod.yaml to use minimal app ✓
4. Deploy and verify health check works ✓
5. Document working configuration ✓

### Phase 2: Add Core Dependencies (Day 1)

1. Add database support (SQLAlchemy, psycopg2)
2. Test locally with database
3. Deploy and verify
4. Add Redis support
5. Test and deploy again

### Phase 3: Add Authentication (Day 2)

1. Add auth dependencies (JWT, passlib)
2. Add minimal auth routes
3. Test authentication flow
4. Deploy and verify

### Phase 4: Add LLM Support (Day 2)

1. Add LLM provider libraries
2. Add minimal LLM routes
3. Test LLM integration
4. Deploy and verify

### Phase 5: Full MVP Integration (Day 3)

1. Gradually enable all routes
2. Test each major feature
3. Deploy incrementally
4. Document final configuration

## Dependencies

- mvp-minimal-deployment ACTION (provides dependency audit)
- Infrastructure access to Render
- Deployment logs for debugging

## Test Requirements

1. **Local Testing**

   - Test each configuration locally first
   - Use `uvicorn app_health_only:app --reload`
   - Verify all endpoints work

2. **Deployment Testing**

   - Monitor Render logs during deployment
   - Test health endpoint after each deployment
   - Document any errors and fixes

3. **Integration Testing**
   - Test database connectivity
   - Test Redis caching
   - Test authentication flow
   - Test LLM orchestration

## Implementation Details

### Key Files to Create/Modify

1. `app_health_only.py` - Ultra minimal app
2. `requirements-ultra-minimal.txt` - Minimal dependencies
3. `render-prod.yaml` - Update to use minimal app
4. `deployment_strategy.md` - Document each working state

### Deployment Strategy

1. Start with absolute minimum
2. Add one feature at a time
3. Test locally before deploying
4. Keep backup of each working state
5. Document configuration at each step

## Risk Mitigation

1. **Risk**: Breaking working deployment

   - Mitigation: Keep backups of working configurations
   - Solution: Use git branches for each phase

2. **Risk**: Hidden dependencies

   - Mitigation: Test imports thoroughly
   - Solution: Use dependency scanning tools

3. **Risk**: Configuration conflicts
   - Mitigation: Document all environment variables
   - Solution: Use separate configs for each phase

## Approval Required From

Joshua Field

## Current Status

**Phase 1 Update (2025-05-17)**

What I've done:

- ✓ Created app_health_only.py with minimal endpoints
- ✓ Created requirements-ultra-minimal.txt with only FastAPI/Uvicorn/Gunicorn
- ✓ Fixed render.yaml configuration to use Python runtime
- ✓ Created scripts/start-render-minimal.sh for deployment
- ✓ Tested minimal app locally - runs successfully
- ✓ Fixed syntax errors in base_orchestrator.py
- ✓ Committed and pushed changes to trigger deployment

What happened:

- Initial deployment was using wrong requirements file (requirements-render.txt)
- Discovered hardcoded backend.app:app in scripts/start-render.sh
- Created new minimal start script to use app_health_only:app
- Updated render.yaml to use new script

Next steps:

- Monitor deployment on Render dashboard
- Once deployed, verify health check endpoint responds
- If successful, proceed to Phase 2
- If fails, debug deployment logs and iterate

**Update: Found the issue!**

- Render dashboard settings override render.yaml
- Need to manually update Build & Start commands in dashboard
- See render_dashboard_configuration.md for detailed steps

Deployment URL: https://ultra-backend.onrender.com/health

## Phase 1 Resolution: Dashboard Configuration Required

**Discovery (2025-05-17):**

- Render dashboard settings override render.yaml configuration
- The deployment was using hardcoded settings in the dashboard
- Cache clearing didn't help because it's not a cache issue

**Solution:**

1. Login to Render dashboard
2. Navigate to ultra-backend service → Settings
3. Update Build & Deploy section:
   - Build Command: `pip install -r requirements-ultra-minimal.txt`
   - Start Command: `python -m gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app`
4. Save changes to trigger new deployment

**Documentation Created:**

- `render_dashboard_configuration.md` - Step-by-step guide for dashboard configuration
- `render_deployment_investigation.md` - Analysis of configuration precedence

**Key Learning:**
Dashboard settings take precedence over render.yaml until a Blueprint sync is performed. For quick fixes and testing, dashboard configuration is the fastest approach.

**Command Format Issue Found:**

- Render was interpreting `app_health_only` as a shell command
- Fixed by using proper gunicorn command format: `gunicorn app_health_only:app`
- Created `render_deployment_fix_startcommand.md` with troubleshooting guide

**Phase 1 Success (2025-05-17):**

- Deployment is working: https://ultra-backend.onrender.com/
- Root endpoint returns: `{"status":"alive"}`
- Health endpoint available at: /health
- Minimal app successfully deployed with working health checks

**Phase 2 Progress (2025-05-17):**

- Created requirements-phase2.txt with database dependencies
- Created app_with_database.py with database health check
- Tested locally - app loads and endpoints work
- Database health check returns appropriate messages
- Ready to deploy to Render
- Created render_deployment_phase2.md with deployment instructions

## Notes

- This systematic approach avoids the "whack-a-mole" problem
- Each phase builds on the previous one
- We maintain working deployments at each step
- Documentation is critical for troubleshooting
- Test locally first, deploy second
