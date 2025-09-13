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

### Backend Testing
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

# Test with reports
make test-report          # Run with Allure and HTML reports
./scripts/run_all_with_cursor_tracking.sh  # Full test suite with tracking
```

### Worktree & Multi-AI Coordination
```bash
# Worktree management
./scripts/coordinate-ais.sh              # Check AI assignments across worktrees
./scripts/check-worktree-status.sh       # Git status for all worktrees
./scripts/update-status.sh billing-system Claude-1 45%  # Update worktree status

# Switch between worktrees
cd ../Ultra-worktrees/billing-system     # Feature development
cd ../Ultra-worktrees/test-unit-enhancement  # Test improvements
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
which python                             # Verify Python interpreter
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
   ├── middleware/      # Auth, CSRF, telemetry
   └── database/        # PostgreSQL + Alembic migrations
   ```

3. **Critical Design Decisions**
   - All LLM adapters share single `httpx.AsyncClient` (25s timeout)
   - Redis caching with local memory fallback
   - JWT + API key authentication on protected endpoints
   - Request ID tracking across all services
   - At least 2 LLM models must be functional for viability

### Worktree Development Model
The project uses **12 Git worktrees** for parallel development:

- **Main**: Config/auth consolidation
- **Testing** (5): unit, integration, e2e, live/performance
- **Features** (7): UI/UX, billing, services, docs, CI/CD, recovery, performance

Each worktree:
- Has specific file ownership boundaries
- Maintains STATUS.md for AI coordination
- Can be deployed independently
- Uses feature flags for isolation

### Deployment & Operations
- **Production**: Render.com (auto-deploy from GitHub)
- **URL**: https://ultrai-core.onrender.com/
- **Deploy Command**: `make deploy` (commits & pushes)
- **Verification**: No action is complete without deployment verification

### API Endpoints
Key endpoints:
- `POST /api/orchestrate` - Main orchestration (multi-stage analysis)
- `GET /api/models` - Available LLM models
- `GET /api/model-health` - Model availability/performance
- `POST /api/auth/login` - Authentication
- `GET /api/metrics` - System metrics (cache hits, response times)
- `GET /docs` - Swagger UI documentation

## Project Rules & Conventions

### From .cursorrc and AICheck
1. **One ActiveAction Rule** - Only one action active per contributor
2. **Documentation-First** - Plan in `.aicheck/actions/[action]/[action]-plan.md`
3. **Test-Driven Development** - Tests before implementation
4. **Worktree Awareness** - Check STATUS.md before starting work
5. **Feature Flags** - Use for worktree-specific features
6. **No Duplicate Names** - Files with same name in different directories forbidden

### Multi-AI Coordination Protocol
When working in a worktree:
1. Check `STATUS.md` for current AI assignment
2. Update with your identifier (e.g., Claude-1, Cursor-2)
3. Document decisions in communication log
4. Commit STATUS.md before switching context
5. Mock dependencies being developed in other worktrees

## Environment Configuration

### Required Environment Variables
```bash
# Core
ENVIRONMENT=development|production
PORT=8000

# Database & Caching
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Authentication
JWT_SECRET=your-secret-key

# LLM Provider API Keys
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

### Feature Flags (app/config.py)
```python
FEATURE_FLAGS = {
    "billing_enabled": os.getenv("ENABLE_BILLING", "false") == "true",
    "new_ui": os.getenv("ENABLE_NEW_UI", "false") == "true",
    "advanced_recovery": os.getenv("ENABLE_RECOVERY", "false") == "true",
}
```

## Frontend Architecture
- **Build**: Vite + React + TypeScript
- **State**: Zustand
- **Styling**: Tailwind CSS + Design tokens
- **Themes**: 6 skins (night, morning, afternoon, sunset, minimalist, business)
- **Icons**: Lucide React (no emojis in production)
- **Error Handling**: Sourcemaps enabled for React error #310

## Testing Best Practices
- **Reset/Kill Servers**: Always reset/kill all servers before attempting server-dependent testing and scripts