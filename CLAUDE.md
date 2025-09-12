# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend Development
- `make dev` - Start development server (fast, minimal dependencies)
- `make prod` - Start production server (full features including database/auth)
- `make setup` - Initial setup (install dependencies + build frontend)
- `make test` - Run all tests
- `make e2e` - Run end-to-end tests with pre-checks
- `make deploy` - Deploy to production (commits and pushes to trigger Render deployment)
- `make clean-ports` - Kill processes on ports 8000-8001
- `make run` - Clean ports and start dev server

### Frontend Development
- `cd frontend && npm run dev` - Start frontend development server
- `cd frontend && npm run build` - Build frontend for production
- `cd frontend && npm run lint` - Run ESLint
- `cd frontend && npm run preview` - Preview production build locally
- `cd frontend && npm test` - Run Jest tests

### Test Running Commands
- `pytest tests/test_specific_file.py -v` - Run specific test file
- `pytest tests/test_file.py::test_function -v` - Run specific test function
- `pytest tests/ -k "test_pattern" -v` - Run tests matching pattern
- `pytest tests/ -m "unit" -v` - Run only unit tests
- `pytest tests/ -m "integration" -v` - Run only integration tests
- `pytest tests/ -m "e2e" -v` - Run only end-to-end tests
- `pytest tests/ -m "not live_online" -v` - Run all tests except live API tests
- `pytest tests/unit/ -v` - Run only unit tests directory
- `pytest tests/test_file.py -s` - Run with print output visible
- `./run_e2e.sh` - Run Playwright e2e tests using local Chrome browser
- `pytest tests/ -m "live_online" -v` - Run live tests against real LLM providers
- `pytest tests/test_file.py -vv` - Run with extra verbose output
- `pytest tests/ --lf` - Run only last failed tests

### Python Environment Setup (CRITICAL)
**Always activate the virtual environment before running any Python commands:**
- `source venv/bin/activate` - Activate the virtual environment (REQUIRED before running Python code)
- `poetry shell` - Alternative: activate Poetry environment if Poetry is installed
- `./venv/bin/python script.py` - Direct execution without activation
- `which python` - Verify correct Python interpreter is being used

### Poetry Commands (Python Dependency Management)
- `poetry install` - Install all dependencies from poetry.lock
- `poetry sync` - Synchronize environment with lock file
- `poetry run pytest` - Run tests in Poetry environment
- `poetry add package_name` - Add new dependency
- `poetry show --outdated` - Check for outdated packages

### Code Quality Commands
- `poetry run black .` - Format Python code with Black
- `poetry run isort .` - Sort Python imports with isort
- `poetry run flake8 .` - Run Python linting with Flake8
- `poetry run mypy app/` - Run type checking with MyPy
- `cd frontend && npm run lint` - Run ESLint for TypeScript/React

### Common Troubleshooting Commands
- `make clean-ports` - Kill stuck processes on ports 8000-8001
- `poetry sync` - Fix dependency issues
- `rm -rf frontend/dist && cd frontend && npm run build` - Rebuild frontend from scratch
- `poetry cache clear pypi --all` - Clear Poetry cache for dependency issues
- `source venv/bin/activate` - Fix import errors by activating virtual environment
- `which python` - Check which Python interpreter is being used
- `pip install -r requirements.txt` - Install dependencies if Poetry isn't available

## High-Level Architecture

### Core Application Structure
The Ultra project implements an LLM orchestration system with intelligence multiplication patterns:

**Backend Architecture (FastAPI):**
- `app/routes/` - API endpoint handlers (the "front door") - validate requests and delegate to services
- `app/services/` - Core business logic layer containing:
  - `orchestration_service.py` - Multi-stage analysis coordinator implementing the UltrLLMOrchestrator patent
  - `llm_adapters.py` - Unified interface for external LLM providers (OpenAI, Anthropic, Gemini, HuggingFace)
  - `auth_service.py` - JWT authentication and API key management
  - `model_registry.py` - Dynamic model discovery and management
  - `cache_service.py` - Redis caching with local memory fallback
  - `rate_limiter.py` - Rate limiting service per user/endpoint
- `app/models/` - Data shape definitions (Pydantic for API, SQLAlchemy for database)
- `app/middleware/` - Request/response interceptors (auth, CSRF, security headers, telemetry)
- `app/database/` - PostgreSQL connection management and Alembic migrations
- `app/utils/` - Shared utilities (logging, error handling, common functions)

**Frontend Architecture (React + Vite):**
- Vite-based build with React Router for SPA navigation
- Zustand for state management
- Tailwind CSS for styling
- TypeScript throughout
- Design token system in `frontend/src/styles/tokens.css`
- Skin system with 6 themes (night, morning, afternoon, sunset, minimalist, business)

**Key Architectural Patterns:**
- All LLM adapters share a single `httpx.AsyncClient` with 25-second timeout to prevent hanging requests
- Intelligence multiplication: Multiple LLMs analyze the same prompt in stages for enhanced outputs
- Redis caching with local memory fallback
- Environment-based configuration (development vs production)
- Frontend served by backend in production mode
- Three-stage orchestration flow: Initial Analysis → Meta Analysis → Ultra Synthesis

### Orchestration Flow
The orchestration implements a patented multi-stage analysis:
1. **Initial Analysis**: Multiple models analyze the query independently
2. **Meta Analysis**: A meta-model reviews all initial responses
3. **Ultra Synthesis**: Final synthesis combining all insights

Key files:
- `app/services/orchestration_service.py` - Main orchestration logic
- `app/routes/orchestrator_minimal.py` - API endpoint handling
- `app/services/synthesis_prompts.py` - Prompt templates for each stage

### AICheck Action Management System
The project uses AICheck for structured development workflow:

**AICheck Commands:**
- `./aicheck status` - Show current action status
- `./aicheck action new ActionName` - Create new action
- `./aicheck action set ActionName` - Set active action
- `./aicheck action complete [ActionName]` - Complete action with verification
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck exec` - Toggle exec mode for maintenance
- `./aicheck deps` - Show dependency information and links
- `./aicheck rules` - Display project rules and AICheck documentation
- `./aicheck reset` - Reset to no active action (use with caution)

**AICheck Principles:**
1. **One ActiveAction Rule** - Only one action can be active per contributor
2. **Documentation-First** - Plan thoroughly in `.aicheck/actions/[action]/[action]-plan.md` before coding
3. **Test-Driven** - Write tests before implementation
4. **Deployment Verification** - Actions aren't complete until verified in production
5. **Supporting Docs** - Process docs go in `.aicheck/actions/[action]/supporting_docs/`

**AICheck Directory Structure:**
```
.aicheck/
├── actions/                    # All project actions
│   └── [action-name]/         
│       ├── [action-name]-plan.md
│       ├── todo.md
│       └── supporting_docs/
├── current_action             # Current active action
├── actions_index.md           # Master list of actions
├── rules.md                   # AICheck system rules
└── templates/                 # Action templates
```

### Critical Operational Requirements
- At least two LLM models must be functioning for UltrAI to be viable
- All external API communications use shared httpx client with timeout protection
- Environment variables required for all sensitive configuration
- JWT + API key authentication on all protected endpoints
- Rate limiting enforced per user/endpoint
- Request ID tracking across all services for debugging
- React error #310 addressed via production sourcemaps in Vite config

### Deployment
- Production runs on Render.com with GitHub-based continuous deployment
- Service name: `ultrai-core`
- URL: `https://ultrai-core.onrender.com/`
- Frontend built and served by backend in production
- Use `make deploy` to commit and push changes for automatic deployment
- **CRITICAL**: No action is complete without deployment verification (see `.aicheck/rules.md`)

### Testing Strategy
- Unit tests: Test individual components in isolation
- Integration tests: Test service interactions
- E2E tests: Full user flow testing with Playwright
- Live tests: Tests against real LLM providers (marked with `live_online`)
- Test files organized by type in `tests/unit/`, `tests/integration/`, `tests/e2e/`

### Environment Configuration
- Development: Uses `.env` file with minimal configuration
- Production: Environment variables set in Render dashboard
- Key variables:
  - `ENVIRONMENT` - development/production
  - `PORT` - Server port (8000 default)
  - `DATABASE_URL` - PostgreSQL connection string
  - `REDIS_URL` - Redis connection for caching
  - `JWT_SECRET` - Secret for JWT tokens
  - API keys for LLM providers: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.

### Frontend Specific Notes
- Sourcemaps enabled in production builds to debug minified React errors
- Skin system loads CSS dynamically based on user selection
- Design tokens provide consistent spacing, typography, and colors
- All UI components in `frontend/src/components/ui/` use design tokens
- Lucide React icons used throughout (no emojis in production UI)

### Documentation-First Development Approach
The project follows a strict documentation-first approach. Key documentation files to review:
- `app/services/synthesis_prompts.py` - Prompts for orchestration stages
- `documentation/architecture/*.md` - System architecture docs
- `documentation/development/*.md` - Development guides
- `documentation/deployment/*.md` - Deployment procedures
- `documentation/testing/*.md` - Testing strategies
- `.aicheck/rules.md` - Project rules and AICheck system
- `.aicheck/actions_index.md` - Master list of all actions

**Project Rules (from .cursorrc):**
1. One ActiveAction rule - Only one action active per contributor
2. Documentation is source of truth - Always read docs first
3. Test-Driven Development - Write tests before implementation
4. No action is complete without deployment verification
5. Git discipline - Meaningful commits, no pre-existing changes
6. Dependency management - All dependencies must be documented
7. Explicit action naming - Clear, descriptive action names
8. Supporting docs requirement - Process docs in action folders

### API Documentation
Main API endpoints:
- `GET /` - Health check and application info
- `POST /api/orchestrate` - Main orchestration endpoint for multi-stage analysis
- `GET /api/models` - List available LLM models
- `GET /api/model-health` - Check model availability and performance
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info
- `GET /api/analysis/{analysis_id}` - Get analysis details by ID
- `GET /api/users/{user_id}/analyses` - Get user's analysis history
- `GET /api/metrics` - Get system metrics (cache hits, response times)
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)