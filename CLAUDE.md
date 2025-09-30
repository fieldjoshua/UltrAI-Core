# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 QUICK START (Get Running ASAP)

```bash
# 1. Activate virtual environment (CRITICAL!)
source venv/bin/activate

# 2. Start development server (minimal deps, fast)
make dev
# → http://localhost:8000 (frontend)
# → http://localhost:8000/docs (API docs)

# 3. Or start production server (full features)
make prod
```

**First time setup:**
```bash
make setup    # Install deps + build frontend (takes 5-10 min)
```

## 📋 Essential Commands

### Development
```bash
make dev              # Fast dev server (no DB/auth)
make prod             # Full production server
make run              # Clean ports + start dev
make clean-ports      # Kill port 8000-8001
```

### Testing (Fast)
```bash
# IMPORTANT: Tests timeout at 60s, some fail due to long operations
make test             # Offline tests (mocked, ~2 min)
pytest tests/unit/    # Unit tests only (faster)
pytest -k "test_name" # Run specific test
```

### Code Quality
```bash
ruff check .                    # Lint Python
cd frontend && npm run lint     # Lint frontend
```

## 🏗️ Project Structure (Critical Paths)

```
app/
├── routes/              # API endpoints - START HERE for endpoints
├── services/            # Business logic - orchestration lives here
│   ├── orchestration_service.py        # MAIN: Full synthesis
│   ├── minimal_orchestrator.py         # Faster, simpler synthesis
│   └── llm_adapters.py                 # LLM provider adapters
├── models/              # Pydantic + SQLAlchemy models
└── middleware/          # Auth, CORS, rate limiting

frontend/
├── src/components/      # React components
├── src/api/             # API client
└── src/stores/          # State management

tests/
├── unit/                # Fast unit tests
├── integration/         # Requires services
└── e2e/                 # End-to-end (slow)
```

## 🎯 Core System: Enhanced Synthesis™

**Three-stage process:**
1. **Initial Generation** - Multiple models respond concurrently
2. **Peer Review** - Models critique each other's outputs
3. **Ultra Synthesis** - Lead model synthesizes best response

**Key Files:**
- `app/services/orchestration_service.py` - Main orchestration
- `app/services/minimal_orchestrator.py` - Streamlined version
- `app/routes/orchestrator_minimal.py` - Minimal API endpoint
- `app/services/llm_adapters.py` - OpenAI, Anthropic, Google adapters

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

## 🔧 Quick Fixes

### Add a new endpoint
1. Create route in `app/routes/`
2. Add service logic in `app/services/`
3. Test: `curl http://localhost:8000/your-endpoint`

### Fix a failing test
1. Find test: `grep -r "test_name" tests/`
2. Run it: `pytest tests/path/to/test.py::test_name -v`
3. Debug with print or breakpoint()

### Update frontend
1. `cd frontend`
2. Edit files in `src/`
3. Dev mode auto-reloads: `npm run dev`
4. Production: `npm run build`

## 🚢 Deployment

**Production:** https://ultrai-core.onrender.com  
**Dashboard:** https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg

```bash
git push origin main    # Auto-deploys to Render
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
pytest tests/unit/ -v              # Unit tests (30s)
pytest -k "test_specific" -v       # One test (5s)
```

**Full testing:**
```bash
make test                          # Offline mode (2 min)
make test-integration              # With services (5 min)
```

**Skip slow tests:**
```bash
pytest -m "not e2e" -v             # Skip E2E
```

## 📖 Architecture Patterns

- **Adapter Pattern:** All LLM providers implement `BaseAdapter`
- **Dependency Injection:** Services passed via FastAPI `Depends()`
- **Feature Flags:** `RAG_ENABLED`, etc.
- **Graceful Degradation:** Falls back to SQLite, in-memory cache
- **Circuit Breaker:** Auto provider fallback on failures
- **Correlation IDs:** Track requests with `X-Correlation-ID`

## ⚡ Performance

- **HTTP timeout:** 45 seconds
- **Synthesis timeout:** 70 seconds (configurable)
- **Concurrent execution:** Capped per plan
- **Caching:** Redis (or in-memory fallback)
- **Metrics:** Available at `/api/metrics`

## 📚 More Info

- Full testing modes: See Makefile
- AICheck workflow: `.aicheck/rules.md`
- Frontend architecture: `frontend/README.md`
- Database migrations: `alembic upgrade head`

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