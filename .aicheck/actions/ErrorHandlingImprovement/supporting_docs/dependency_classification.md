# Dependency Classification for Ultra Project

## Overview

This document classifies the dependencies used in the Ultra project, categorizing them as required or optional, and documenting which features are affected by each dependency.

## Required Dependencies

These dependencies are essential for the core functionality of the application:

| Dependency | Purpose | Affected Components |
|------------|---------|---------------------|
| fastapi | Core API framework | All API endpoints |
| uvicorn | ASGI server | Application server |
| pydantic | Data validation | All models and request/response validation |
| SQLAlchemy | Database ORM | All database operations |
| python-dotenv | Environment variable loading | Configuration |

## Optional Dependencies

These dependencies enhance functionality but are not required for the core application to run:

| Dependency | Purpose | Affected Features | Graceful Degradation Path |
|------------|---------|------------------|-----------------------------|
| PyJWT | JWT token handling | Authentication | Disable auth features, use development tokens |
| passlib | Password hashing | User authentication | Use simplified auth in development |
| redis | Caching, rate limiting | Performance optimization, Rate limiting | Disable caching, use in-memory rate limiting |
| sentry_sdk | Error tracking | Production monitoring | Disable Sentry integration |
| anthropic, openai, google-generativeai | LLM integrations | Multi-model analysis | Use mock LLM service |

## Import Handling Strategy

For each optional dependency, we should:

1. Wrap the import in a try-except block
2. Set a feature flag based on availability
3. Provide clear error messages
4. Implement a fallback behavior

Example pattern:

```python
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning(
        "PyJWT not installed - authentication features will be limited. "
        "Install with: pip install PyJWT"
    )
```

## Configuration Options

We should add configuration options to:

1. Explicitly disable features requiring missing dependencies
2. Override the automatic detection of dependencies
3. Configure mock/fallback behavior

Example:

```python
# In config.py
ENABLE_JWT_AUTH = os.getenv("ENABLE_JWT_AUTH", "true").lower() == "true" and JWT_AVAILABLE
```

## Installation Groups

We recommend creating the following installation groups:

1. `requirements-core.txt` - Only essential dependencies
2. `requirements-auth.txt` - Authentication-related dependencies
3. `requirements-cache.txt` - Caching-related dependencies
4. `requirements-llm.txt` - LLM integration dependencies
5. `requirements-dev.txt` - Development-only dependencies
6. `requirements.txt` - All production dependencies (includes 1-4)

This will allow targeted installation based on deployment needs.