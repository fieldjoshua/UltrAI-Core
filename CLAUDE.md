# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Rules

Claude should follow the rules specified in `.aicheck/RULES.md` with focus on documentation-first approach and adherence to language-specific best practices.

## Build & Development Commands

- Backend: `python3 -m uvicorn backend.app:app --reload` (port 8085)
- Frontend: `cd frontend && npm run dev` (port 3009)
- Build: `cd frontend && npm run build`
- Lint: `cd frontend && npm run lint` or `flake8 backend/`
- Type check: `cd frontend && npm run type-check`
- Mock mode: `export USE_MOCK=true && python3 -m uvicorn backend.app:app --reload`

## Testing Commands

- All backend tests: `python3 -m pytest backend/tests/ -v`
- Single test: `python3 -m pytest backend/tests/test_file.py::test_function -v`
- Coverage: `python3 -m pytest --cov=backend backend/tests/ -v`
- Frontend tests: `cd frontend && npm test -- -t "test name"`
- API test: `python3 test_api.py --base-url http://localhost:8085 --models gpt4o,claude3opus`

## Code Style Guidelines

- Python: Max line length 150 chars, follow PEP 8 with exceptions in setup.cfg
- TypeScript/React: ESLint + Prettier (singleQuote: true, semi: true, tabWidth: 2)
- Import order: standard library → third-party → local modules
- Typing: Type annotations (Python), TypeScript interfaces/types (frontend)
- Error handling: Use explicit try/except with logger in Python
- Naming: camelCase for JS/TS, snake_case for Python
- Documentation: Docstrings for all Python functions, JSDoc for complex JS/TS functions

## Environment Management

- Development: Use `.env.development` or set `ENVIRONMENT=development` and `USE_MOCK=true`
- Production: Use `.env.production` or set `ENVIRONMENT=production` and `USE_MOCK=false`
- Toggle: Use `scripts/toggle_environment.sh [development|production]` to switch environments
- Testing: Run `scripts/test_production.sh` to test in production mode
- Real LLM Testing: Add API keys to `.env.api_keys` for testing with real providers
- Documentation: See `documentation/production_readiness_implementation_report.md` for details
