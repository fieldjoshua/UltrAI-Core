# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start
```bash
make setup                # Initial setup (install deps + build frontend)
make dev                  # Start development server (fast, minimal deps)
make prod                 # Start production server (full features)
source venv/bin/activate  # CRITICAL: Activate virtual environment before Python commands
```

### Testing Commands
```bash
# Run specific test categories
pytest tests/ -m "unit" -v              # Unit tests only
pytest tests/ -m "integration" -v       # Integration tests only
pytest tests/ -m "not live_online" -v   # All tests except live API tests
pytest tests/ -m "live_online" -v       # Live tests (requires API keys)

# Run specific tests
pytest tests/test_file.py::test_function -v  # Single test function
pytest tests/ -k "pattern" -v               # Tests matching pattern
pytest tests/ --lf                          # Only last failed tests

# Test reporting
make test-report          # Run with Allure and HTML reports
make test-demo            # Test against staging/production endpoints
```

### Database Commands
```bash
# Database migrations (when DATABASE_URL is configured)
alembic upgrade head      # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1      # Rollback one migration
alembic history           # View migration history
```

### Deployment & Verification
```bash
make deploy               # Commit, push, and trigger Render deployment
git push origin main      # Manual push (Render auto-deploys from GitHub)

# Verify deployment
curl https://ultrai-staging-api.onrender.com/api/health  # Staging
curl https://ultrai-prod-api.onrender.com/api/health     # Production

# Frontend deployment verification
curl https://staging-ultrai.onrender.com    # Staging frontend
curl https://ultrai.com                     # Production frontend
curl https://demo-ultrai.onrender.com       # Demo (mock API)
```

### AICheck Action Management
```bash
./aicheck status                         # Current action status
./aicheck action new ActionName          # Create new action
./aicheck action set ActionName          # Set active action
./aicheck action complete                # Complete current action
```

### Common Issues & Solutions
```bash
make clean-ports                         # Kill stuck processes on 8000-8001
poetry sync                              # Fix dependency issues
source venv/bin/activate                 # Fix import errors
./scripts/verify-render-config.sh        # Verify Render configuration
```

## High-Level Architecture

### Core System Design
The UltrAI project implements a **patented LLM orchestration system** using intelligence multiplication patterns:

1. **Multi-Stage Analysis Pipeline**
   - Initial Analysis: Multiple LLMs analyze independently
   - Meta Analysis: A meta-model reviews all responses
   - Ultra Synthesis: Final synthesis combining all insights
   - Implementation: `app/services/orchestration_service.py`

2. **Service Architecture**
   ```
   app/
   ├── routes/          # API endpoints (validate & delegate)
   ├── services/        # Core business logic
   │   ├── orchestration_service.py   # Multi-stage coordinator
   │   ├── llm_adapters.py            # Unified LLM interface
   │   ├── interfaces/                # Service abstractions
   │   └── synthesis_prompts.py       # Stage-specific prompts
   ├── middleware/      # Auth, CSRF, telemetry, rate limiting
   └── database/        # PostgreSQL + Alembic migrations
   ```

3. **Critical Design Decisions**
   - All LLM adapters share single `httpx.AsyncClient` (25s timeout)
   - Redis caching with local memory fallback
   - JWT + API key authentication on protected endpoints
   - Request ID tracking across all services
   - At least 2 LLM models must be functional for viability (configurable via `MINIMUM_MODELS_REQUIRED`)

### Frontend Architecture
- **Framework**: React + TypeScript + Vite
- **API Client**: Custom hooks with type-safe API integration
- **State Management**: Zustand stores
- **Styling**: Tailwind CSS + custom design tokens
- **Themes**: Multiple skins (night, morning, afternoon, sunset)
- **Key Components**: OrchestratorInterface, ModelMonitor, SSEPanel

### Deployment Architecture
- **Backend Services**:
  - Production: https://ultrai-prod-api.onrender.com (manual deploy)
  - Staging: https://ultrai-staging-api.onrender.com (auto-deploy from main)
- **Frontend Services**:
  - Production: https://ultrai.com (branch: production)
  - Staging: https://staging-ultrai.onrender.com (branch: main)
  - Demo: https://demo-ultrai.onrender.com (production branch + mock API)
- **Build**: Uses `pip` with `requirements-production.txt` (not Poetry in production)
- **Critical**: Never hardcode PORT - Render assigns dynamically

### API Endpoints
Key endpoints:
- `POST /api/orchestrate` - Main orchestration (multi-stage analysis)
- `GET /api/models` - Available LLM models
- `GET /api/model-health` - Model availability/performance
- `POST /api/auth/login` - Authentication
- `GET /api/metrics` - System metrics (cache hits, response times)
- `GET /api/orchestrator/events` - SSE for real-time monitoring
- `GET /docs` - Swagger UI documentation

## Project Rules & Conventions

### AICheck Deployment Requirements (CRITICAL)
**NO ACTION IS COMPLETE WITHOUT DEPLOYMENT VERIFICATION**
- Code must be deployed to production/staging
- Production URL must be tested and verified
- Document test results in `supporting_docs/deployment-verification.md`
- See `.aicheck/rules.md` for complete deployment checklist

### Git Workflow & Branches
- **main**: Staging branch (active development)
- **production**: Production branch (stable, curated features)
- **ultrai-play-***: Playground branches for experiments
- Never commit directly to production
- Promote staging → production via merge or cherry-pick

### Development Workflow
1. **One ActiveAction Rule** - Only one action active per contributor
2. **Documentation-First** - Plan in `.aicheck/actions/[action]/[action]-plan.md`
3. **Test-Driven Development** - Tests before implementation
4. **Deployment Verification** - Test production URL before marking complete

### Collaboration & Oversight (Required)
- Adhere to signals: `[PLAN]`, `[CLAUDE_DO]`, `[ULTRA_DO]`, `[STATUS]`, `[REVIEW]`, `[BLOCKER]`, `[COMPLETE]`
- Before push/merge you must provide evidence:
  - Local test outputs and commands
  - Security checks (dependency audit, secret/regex scan, injection/XSS basics)
  - Model availability policy satisfied (≥2 healthy models; single-model fallback disabled)
  - Endpoint verifications (`/api/available-models?healthy_only=true`, `/api/orchestrator/status`)
- Drift prevention: if off track, say "I'm getting off track. Returning to [ORIGINAL_TASK]" and realign
- No refactors/optimizations/features unless explicitly requested
- See `docs/OVERSIGHT_README.md` and `docs/cursor-rules.md` for full policies

#### Real-time Monitoring & Check-ins
- Subscribe to SSE when applicable: `GET /api/orchestrator/events?correlation_id=…`
- Events to expect: analysis_start, model_selected, initial_start, pipeline_complete, model_completed, analysis_complete, service_unavailable
- Post oversight check-ins as needed: `POST /api/oversight/checkin` with `{task_id, status, evidence?, notes?}`

### Multi-AI Coordination (if using worktrees)
1. Check `STATUS.md` for current AI assignment
2. Update with your identifier (e.g., Claude-1, Cursor-2)
3. Document decisions in communication log
4. Commit STATUS.md before switching context

## Environment Configuration

### Required Environment Variables
```bash
# Core
ENVIRONMENT=development|staging|production
PORT=8000  # Local only - Render assigns dynamically

# Database & Caching
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Authentication
JWT_SECRET=your-secret-key

# LLM Provider API Keys (set in Render dashboard)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...       # For Gemini
HUGGINGFACE_API_KEY=...  # Optional

# Frontend (for Vite builds)
VITE_APP_MODE=staging|production|playground
VITE_API_MODE=live|mock
```

### Feature Flags (app/config.py)
```python
FEATURE_FLAGS = {
    "billing_enabled": os.getenv("ENABLE_BILLING", "false") == "true",
    "new_ui": os.getenv("ENABLE_NEW_UI", "false") == "true",
    "advanced_recovery": os.getenv("ENABLE_RECOVERY", "false") == "true",
}
```

### Model Availability Policy
```python
MINIMUM_MODELS_REQUIRED = 2  # Configurable in app/config.py
ENABLE_SINGLE_MODEL_FALLBACK = False
```

## Testing Strategy

### Test Organization
- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Tests with local services
- `tests/e2e/` - End-to-end tests
- `tests/live/` - Tests against real APIs (marked with `@pytest.mark.live_online`)

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.live_online` - Requires real API keys
- `@pytest.mark.slow` - Long-running tests

## Security Notes
- `.env.staging` is excluded from git (contains secrets)
- All secrets must be in environment variables or Render dashboard
- GitHub push protection will block commits with exposed secrets
- Run security checks before pushing (see Collaboration section)

## Render Deployment Notes
- **Config Files**: `render.yaml` (main), `render-staging.yaml`, `render-production.yaml`
- **Build Command**: Includes frontend build (`npm ci && npm run build`)
- **Start Command**: `python app_production.py` (handles dynamic port)
- **Health Check**: `/api/health` endpoint
- **Auto-deploy**: Staging only; Production requires manual deploy
- **Verification Script**: Run `./scripts/verify-render-config.sh` to check setup