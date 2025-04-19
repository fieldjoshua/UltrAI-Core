# UltraAI Developer Guide

This guide provides development guidelines and documentation for the UltraAI Framework.

## IMPORTANT: Documentation First Approach

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review the consolidated documentation in `documentation/`**

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- Docker and Docker Compose (for containerized development)
- PostgreSQL 14+ (for local database)

### Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/ultra.git
cd ultra
```

2. **Set up Python environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Set up Node.js environment**

```bash
cd frontend
npm install
```

4. **Environment Variables**

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file to add your API keys and configuration.

### Running the Application

#### Development Mode

1. **Start the backend**

```bash
cd backend
python -m api.main
```

2. **Start the frontend**

```bash
cd frontend
npm run dev
```

#### Using Docker

```bash
docker-compose up -d
```

### Testing

- **Run backend tests**

```bash
pytest tests/
```

- **Run frontend tests**

```bash
cd frontend
npm test
```

## Code Structure

Refer to [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) for the detailed project structure.

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions and classes
- Test coverage should be at least 80%

### JavaScript/TypeScript

- Use ESLint with the project configuration
- Follow the React best practices
- Write unit tests for all components
- Use TypeScript for type safety

## Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure tests pass
4. Submit a pull request to `develop`
5. Code review by at least one team member

## Documentation

- Update documentation for any new features
- Include both code docstrings and user-facing docs
- Examples should be included for all public APIs
- All documentation should be placed in the `documentation/` directory

## Analysis Patterns

When working with analysis patterns:

1. Consult the existing patterns in `src/patterns/ultra_analysis_patterns.py`
2. Review the technical documentation in [instructions/PATTERNS.md](../instructions/PATTERNS.md)
3. DO NOT create duplicate pattern implementations
4. Maintain consistency with the existing pattern structure

## Need Help?

- Check the documentation in `documentation/`
- Review the [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) for specific topics
- Create an issue on GitHub
- Contact the development team
