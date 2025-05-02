# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

- Backend: `pip3 install -r requirements.txt PyJWT passlib redis` (install Python dependencies)
- Frontend: `cd frontend && npm install` (install npm dependencies)
- Note: The backend requires Redis and PostgreSQL for full functionality but will run with warnings if these are not available

## Build & Development Commands

- Backend: `python3 -m uvicorn backend.app:app --reload` (development server on port 8000)
- Backend (mock mode): Create environment variable `export USE_MOCK=true` before running server
- Frontend: `cd frontend && npm run dev` (development server on port 3009)
- Build: `cd frontend && npm run build` (production build)
- Lint: `cd frontend && npm run lint` (frontend) or `flake8 backend/` (backend)
- Type check: `cd frontend && npm run type-check` (TypeScript)

## Testing Commands

- Run all backend tests: `python3 -m pytest backend/tests/ -v`
- Single backend test: `python3 -m pytest backend/tests/test_file.py::test_function -v`
- Frontend tests: `cd frontend && npm test -- -t "test name"`
- E2E tests: `cd frontend && npm run test:e2e`

## Code Style Guidelines

- Python: Max line length 88 chars, follow PEP 8
- TypeScript/React: Use ESLint with Prettier (singleQuote: true, semi: true, tabWidth: 2)
- Import order: standard library → third-party → local modules
- Typing: Use type annotations (Python), TypeScript interfaces/types (frontend)
- Error handling: Use explicit try/except with logger in Python, React error boundaries in frontend
- Naming: camelCase for JS/TS, snake_case for Python
