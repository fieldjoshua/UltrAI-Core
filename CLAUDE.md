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

## Architectural Memories

- At least two models have to be functioning for UltrAI to be viable 

## Remaining file content continues as in the original...