# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 QUICK START (Get Running ASAP)

```bash
# 1. Activate virtual environment (CRITICAL!)
source venv/bin/activate

# 2. Start development server (minimal deps, fast)
make dev
# → Uses app_development.py
# → http://localhost:8000 (frontend)
# → http://localhost:8000/docs (API docs)

# 3. Or start production server (full features)
make prod
# → Uses app_production.py
# → Includes database, auth, caching
```

**First time setup:**
```bash
make setup    # Install deps + build frontend (takes 5-10 min)
```

**Note:** This project uses TWO app entry points:
- `app_development.py` - Fast startup, minimal dependencies, no auth/DB required
- `app_production.py` - Full features, database, Redis cache, JWT auth

## 📋 Essential Commands

### Development
```bash
make dev              # Fast dev server (no DB/auth)
make prod             # Full production server
make run              # Clean ports + start dev
make clean-ports      # Kill port 8000-8001
```

### Testing
```bash
# IMPORTANT: Tests timeout at 60s, some fail due to long operations
make test                  # Offline tests (mocked, ~2 min)
make test-integration      # Integration tests (5 min)
make test-live             # Live provider tests (requires API keys)
pytest tests/unit/         # Unit tests only (faster)
pytest -k "test_name"      # Run specific test
pytest -m "not e2e" -v     # Skip E2E tests
```

**Test markers available:**
- `unit`, `integration`, `e2e`: Test categories
- `live`: Requires real API keys
- `offline`: No external dependencies
- `slow`, `quick`: Performance-based
- `requires_redis`, `requires_api_keys`: Dependency-based

### Code Quality
```bash
ruff check .                    # Lint Python
cd frontend && npm run lint     # Lint frontend
```

## 🏗️ Project Structure (Critical Paths)

```
app/
├── routes/              # API endpoints (30+ route files)
│   ├── orchestrator_minimal.py         # Main orchestration endpoint
│   ├── health_routes.py                # Health checks
│   ├── auth_routes.py                  # Authentication
│   └── user_routes.py                  # User management
├── services/            # Business logic (60+ service files)
│   ├── orchestration_service.py        # CORE: 3-stage synthesis pipeline
│   ├── llm_adapters.py                 # Provider adapters (OpenAI/Anthropic/Google)
│   ├── provider_health_manager.py      # Provider health checks
│   └── model_selection.py              # Model selection logic
├── models/              # Pydantic models (API contracts)
├── database/models/     # SQLAlchemy models (DB schema)
├── middleware/          # 10+ middleware layers (auth, rate limit, CORS, etc.)
└── utils/               # Utilities, error handling, logging

frontend/
├── src/components/      # 80+ React components
│   └── wizard/          # Multi-step wizard (main UI, currently being refactored)
├── src/api/             # API client + service methods
├── src/stores/          # Zustand stores (auth, documents, UI)
├── src/hooks/           # Custom React hooks (18+ hooks)
└── src/skins/           # 6 theme variants (night/morning/afternoon/sunset/minimalist/business)

tests/
├── unit/                # Fast unit tests (~30s)
├── integration/         # Service integration tests
├── e2e/                 # End-to-end tests
├── smoke/               # Smoke tests for quick validation
└── frontend/            # Frontend-specific tests (Jest + testing-library)
```

## 🎯 Core System: Enhanced Synthesis™

**Three-stage process:**
1. **Initial Generation** - Multiple models respond concurrently
2. **Peer Review** - Models critique each other's outputs
3. **Ultra Synthesis** - Lead model synthesizes best response

**Key Files:**
- `app/services/orchestration_service.py` - Main orchestration logic (patent implementation)
- `app/routes/orchestrator_minimal.py` - API endpoint `/api/orchestrator/analyze`
- `app/services/llm_adapters.py` - Provider adapters (OpenAI, Anthropic, Google, HuggingFace)
- `app/services/provider_health_manager.py` - Circuit breaker + fallback logic
- `app/services/model_selection.py` - Smart model selection (Premium/Speed/Budget)

## 🔑 Environment Variables (Copy to .env)

```bash
# Required for LLM functionality
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Optional (has defaults)
PORT=8000
ENVIRONMENT=development
TEST_MODE=offline

# Advanced (optional)
DATABASE_URL=postgresql://...       # Leave unset for SQLite
REDIS_URL=redis://localhost:6379   # Leave unset for in-memory
JWT_SECRET_KEY=...                  # Auto-generated if unset
RAG_ENABLED=false                   # Enable document endpoints
CONCURRENT_EXECUTION_TIMEOUT=70     # Synthesis timeout (seconds)
```

## 🚨 Common Issues & Fixes

### Issue: Tests timeout
**Cause:** 70-second synthesis operations exceed 60s test timeout  
**Fix:** Run specific fast tests: `pytest tests/unit/`

### Issue: Import errors
**Cause:** Virtual environment not activated  
**Fix:** `source venv/bin/activate`

### Issue: Port already in use
**Fix:** `make clean-ports`

### Issue: Frontend not loading
**Cause:** Frontend not built  
**Fix:** `cd frontend && npm run build`

### Issue: Database connection error
**Fix:** App falls back to in-memory SQLite automatically

### Issue: Redis connection refused
**Fix:** Rate limiting is disabled automatically, app still works

### Issue: Frontend shows black screen
**Cause:** Missing Redux Provider or incorrect build configuration  
**Fix:** Check `frontend/src/main.tsx` has Redux Provider wrapper, rebuild frontend

### Issue: Render deployment not updating
**Cause:** Changes not pushed to GitHub (Render deploys from GitHub, not local files)  
**Fix:** `git push origin main` - Render watches `main` branch for auto-deploy

## 📍 Key API Endpoints

**Public:**
- `GET /health` - Health check
- `GET /docs` - Swagger UI

**Requires Auth:**
- `POST /api/orchestrator/analyze` - Main synthesis endpoint
- `POST /api/orchestrator/minimal` - Faster minimal synthesis
- `GET /api/metrics` - Prometheus metrics
- `GET /api/user/balance` - User token balance

**Auth:**
- `POST /api/auth/login` - Get JWT token

## 🔧 Common Workflows

### Add a new API endpoint
1. Create route file in `app/routes/` (follow pattern from existing routes)
2. Add service logic in `app/services/`
3. Register route in `app_production.py` or `app_development.py`
4. Test locally: `curl http://localhost:8000/your-endpoint`
5. Add tests in `tests/unit/` or `tests/integration/`

### Fix a failing test
1. Find test: `grep -r "test_name" tests/`
2. Run it: `pytest tests/path/to/test.py::test_name -v`
3. Debug with print or `breakpoint()`
4. Check logs: test failures often include detailed error messages

### Update frontend component
1. `cd frontend`
2. Edit files in `src/components/`
3. Dev mode auto-reloads: `npm run dev`
4. Test changes: `npm test -- ComponentName`
5. Build for production: `npm run build`
6. Frontend is served by backend, so rebuild triggers full deploy

### Deploy to production
1. Commit changes: `git add . && git commit -m "description"`
2. **CRITICAL: Push to GitHub:** `git push origin main`
   - ⚠️ Render deploys from GitHub, NOT local files
   - Without pushing, your changes won't deploy
3. Monitor deploy: Check https://dashboard.render.com
4. Verify production: Visit https://ultrai-prod-api.onrender.com/api/health
5. Check logs if issues: Render dashboard → Service → Logs

**Important:** Use `git commit --no-verify` if pre-commit hooks fail and need to bypass

## 🚢 Deployment

**Production:** https://ultrai-prod-api.onrender.com (ACTIVE)  
**Staging:** https://ultrai-staging-api.onrender.com  
**Dashboard:** https://dashboard.render.com

**Note:** `ultrai-core.onrender.com` appears suspended - use `ultrai-prod-api` as primary

### Quick Deploy
```bash
./scripts/deploy.sh           # Push to main + verify all services
./scripts/render-check-deploys.sh  # Check deploy status only
```

### All Services
All services track `main` branch with auto-deploy enabled:
- **ultrai-prod-api** (https://ultrai-prod-api.onrender.com) - ✅ PRIMARY PRODUCTION
- **ultrai-staging-api** (https://ultrai-staging-api.onrender.com) - ✅ Staging environment
- ultrai-core (https://ultrai-core.onrender.com) - ⚠️ SUSPENDED (not in use)
- Plus 5 frontend static sites (demo, staging, production variants)

### Manual Deploy
```bash
git add . && git commit -m "msg" && git push origin main
# Then verify: curl https://ultrai-prod-api.onrender.com/api/health
```

### Quick Health Checks
```bash
# Production
curl https://ultrai-prod-api.onrender.com/api/health

# Staging
curl https://ultrai-staging-api.onrender.com/api/health

# Expected response (healthy):
# {"status":"ok","uptime":"...","services":{"database":"healthy","cache":"healthy","llm":"healthy"}}
```

## 💡 Development Tips

1. **Always activate venv first:** `source venv/bin/activate`
2. **Use make dev for speed:** No DB/Redis needed
3. **Check /docs for API:** Interactive Swagger UI
4. **Test endpoints with curl:**
   ```bash
   curl http://localhost:8000/health
   ```
5. **Watch logs:** Server logs show all requests in real-time

## 🧪 Testing Strategy

**Fast feedback loop:**
```bash
pytest tests/unit/ -v                        # Unit tests (30s)
pytest -k "test_specific" -v                 # One test (5s)
pytest tests/unit/test_model_registry.py -v  # Single file
pytest -vv --tb=short                        # Detailed output
```

**Full testing:**
```bash
make test                          # Offline mode (2 min)
make test-integration              # With services (5 min)
make test-live                     # Real LLM providers (requires API keys)
make e2e                           # End-to-end tests
```

**Frontend testing:**
```bash
cd frontend && npm test                    # Jest tests
cd frontend && npm run test:watch          # Watch mode
cd frontend && npm run test:coverage       # Coverage report
npm test -- --testNamePattern="renders"    # Run tests matching pattern
```

**Important test notes:**
- Default timeout: 60 seconds (configurable in pytest.ini)
- Synthesis operations take ~70 seconds (may timeout in tests)
- Tests run in `offline` mode by default (mocked external dependencies)
- Use `TEST_MODE=live` environment variable to test against real providers

## 📖 Architecture Patterns

**Backend (FastAPI + Python):**
- **Adapter Pattern:** All LLM providers implement `BaseAdapter` interface
- **Dependency Injection:** Services passed via FastAPI `Depends()`
- **Circuit Breaker:** Provider health manager auto-fails over on errors
- **Graceful Degradation:** Falls back to SQLite, in-memory cache, disables auth if needed
- **Correlation IDs:** Track requests with `X-Correlation-ID` header
- **Middleware Stack:** 10+ layers (auth, CORS, rate limit, telemetry, security headers)

**Frontend (React + TypeScript):**
- **Multi-Step Wizard:** JSON-driven wizard steps (`public/wizard_steps.json`)
- **Zustand + Redux:** Lightweight global state + complex state management
- **React Query:** Server state, caching, optimistic updates
- **Theme System:** Dynamic CSS loading with 6 variants
- **Error Boundaries:** Component-level error isolation
- **Lazy Loading:** Route-based code splitting + dynamic imports

## ⚡ Performance

- **HTTP timeout:** 45 seconds
- **Synthesis timeout:** 70 seconds (configurable)
- **Concurrent execution:** Capped per plan
- **Caching:** Redis (or in-memory fallback)
- **Metrics:** Available at `/api/metrics`

## 📚 More Info

- **Frontend deep dive:** `frontend/CLAUDE.md` (wizard architecture, theme system, testing)
- **Testing documentation:** `tests/README.md` and `tests/TEST_CONFIGURATION.md`
- **Testing modes:** See `Makefile` for all test variants
- **Database migrations:** `alembic upgrade head` (auto-runs in production)
- **API documentation:** `/docs` (Swagger UI) when server is running
- **Provider configuration:** All LLM adapters support API key rotation without restart

## 🔍 Important Context

**Current Work (Sep 2025):**
- CyberWizard component refactor in progress (24/50 tests passing)
- Wizard step markers and navigation improvements
- Frontend hook improvements (useKeyboardNavigation)
- Test stabilization effort

**Known Issues:**
- Some wizard tests unstable due to async timing
- Background image optimization needed (large file sizes)
- React error #310 related to minified production build

## 🎯 Priority Checklist for New Developers

- [ ] Clone repo
- [ ] `source venv/bin/activate`
- [ ] Create `.env` with API keys
- [ ] `make setup` (first time only)
- [ ] `make dev`
- [ ] Visit http://localhost:8000
- [ ] Check http://localhost:8000/docs
- [ ] Run `make test` to verify setup
- [ ] Start coding!

---

**Remember:** If something doesn't work, check:
1. Virtual environment activated? (`which python` should show venv)
2. API keys set in `.env`?
3. Ports clean? (`make clean-ports`)
4. Frontend built? (`cd frontend && npm run build`)