# Installation Guide for Ultra

This document provides detailed instructions for installing and configuring the Ultra backend and its dependencies.

## Prerequisites

- Python 3.8 or higher
- Node.js 14.x or higher (for frontend)
- PostgreSQL 12.x or higher (optional, with fallback)
- Redis 6.x or higher (optional, with fallback)

## Installation Options

Ultra supports various installation configurations depending on your needs:

### Full Installation (Development)

For development with all features enabled:

```bash
# Clone the repository
git clone https://github.com/your-org/ultra.git
cd ultra

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Minimal Installation (Production)

For production with only essential dependencies:

```bash
# Clone the repository
git clone https://github.com/your-org/ultra.git
cd ultra

# Install core backend dependencies
pip install -r requirements-core.txt

# Install selected optional dependencies
pip install redis PyJWT passlib
```

### Containerized Installation (Docker)

For containerized deployment:

```bash
# Clone the repository
git clone https://github.com/your-org/ultra.git
cd ultra

# Build and run with Docker Compose
docker-compose up --build
```

## Optional Dependencies

Ultra uses a graceful degradation approach, allowing it to run with reduced functionality when certain dependencies are not available.

### Database (PostgreSQL)

PostgreSQL is recommended for production but is optional with fallback to an in-memory database:

```bash
# Install PostgreSQL client library
pip install psycopg2-binary

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ultra
export DB_USER=ultrauser
export DB_PASSWORD=ultrapassword

# Toggle fallback behavior
export ENABLE_DB_FALLBACK=true  # Set to false to require PostgreSQL
```

### Caching and Rate Limiting (Redis)

Redis is used for caching and rate limiting but has an in-memory fallback:

```bash
# Install Redis client
pip install redis

# Set environment variables
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_password  # Optional

# Configure caching
export CACHE_ENABLED=true
export MAX_MEMORY_ITEMS=1000  # For in-memory fallback
```

### Authentication (PyJWT)

PyJWT is used for token authentication but has a simplified fallback:

```bash
# Install JWT libraries
pip install PyJWT passlib

# Set environment variables
export JWT_SECRET_KEY=your_secret_key
export JWT_REFRESH_SECRET_KEY=your_refresh_secret
export ACCESS_TOKEN_EXPIRE_MINUTES=15
export REFRESH_TOKEN_EXPIRE_DAYS=7
```

### LLM Services

Ultra supports multiple LLM providers that can be configured via environment variables:

```bash
# Install LLM client libraries
pip install anthropic openai google-generativeai

# Set API keys
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
export GOOGLE_API_KEY=your_google_key

# Use mock mode during development
export USE_MOCK=true
```

### Monitoring (Sentry)

Sentry for error tracking is optional:

```bash
# Install Sentry SDK
pip install sentry-sdk

# Configure Sentry
export SENTRY_DSN=your_sentry_dsn
export ENVIRONMENT=production
```

## Environment Configuration

Create a `.env` file in the project root by copying `env.example`:

```bash
cp env.example .env
```

Edit the `.env` file to configure your environment. See the example file for all available options.

## Dependency Check

To verify your installation and check the status of dependencies:

1. Start the application
2. Access the dependency status endpoint:

```bash
# Start the application
python -m uvicorn backend.app:app --reload

# Check dependency status
curl http://localhost:8000/api/dependencies
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing dependencies:

1. Check the API logs for specific error messages
2. Look for warnings about fallback implementations being used
3. Install the specific dependency mentioned in the error message
4. Restart the application

### Database Connection Issues

If you have issues connecting to PostgreSQL:

```bash
# Verify PostgreSQL is running
pg_isready -h $DB_HOST -p $DB_PORT

# Check connection parameters
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# To use fallback instead
export ENABLE_DB_FALLBACK=true
```

### Redis Connection Issues

If you have issues connecting to Redis:

```bash
# Verify Redis is running
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# In-memory fallback is used automatically
# No additional configuration required
```

## Advanced Configuration

See the [Dependencies Documentation](dependencies.md) for more detailed information about dependency management and configuration options.