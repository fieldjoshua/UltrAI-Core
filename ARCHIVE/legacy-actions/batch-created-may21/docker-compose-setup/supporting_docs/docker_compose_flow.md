# Docker Compose Development Workflow

## Overview

This document describes the development workflow using Docker Compose for the Ultra project. It covers how to set up, run, and manage the containerized development environment.

## Prerequisites

Before starting, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/) (20.10.0 or newer)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0.0 or newer)
- Git

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ultra.git
cd ultra
```

### 2. Configure Environment Variables

Copy the example environment file and adjust as needed:

```bash
cp env.example .env
```

At minimum, you should configure:

- Database credentials
- Redis configuration
- JWT secret (for authentication)
- API keys (if needed for development)

### 3. Start the Development Environment

Launch all services using Docker Compose:

```bash
docker-compose up
```

Or to run in detached mode:

```bash
docker-compose up -d
```

The first time you run this command, Docker will:

1. Build the backend image
2. Pull the Redis and PostgreSQL images
3. Create volumes for data persistence
4. Start all services

### 4. Access Services

Once the environment is running, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432 (from host) or db:5432 (from other containers)
- **Redis**: localhost:6379 (from host) or redis:6379 (from other containers)

## Development Workflow

### Code Changes

When working on the backend, any changes to the code will be reflected immediately thanks to volume mounting and the development server's hot reload capability.

The workflow is:

1. Edit code on your local machine
2. Save changes
3. The backend container will automatically reload

### Database Management

#### Connecting to the Database

To connect to the PostgreSQL database:

```bash
docker-compose exec db psql -U ultra -d ultra_dev
```

#### Running Migrations

Migrations are run automatically when the container starts, but you can also run them manually:

```bash
docker-compose exec backend alembic upgrade head
```

To create a new migration:

```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Redis Commands

To interact with Redis:

```bash
docker-compose exec redis redis-cli
```

### Viewing Logs

To view logs for all services:

```bash
docker-compose logs
```

For a specific service:

```bash
docker-compose logs backend
```

To follow logs:

```bash
docker-compose logs -f
```

### Environment Management

#### Stopping the Environment

To stop all services:

```bash
docker-compose down
```

To stop and remove volumes (this will delete all data):

```bash
docker-compose down -v
```

#### Rebuilding Services

If you make changes to the Dockerfile or dependencies:

```bash
docker-compose build
```

Or for a specific service:

```bash
docker-compose build backend
```

Then restart:

```bash
docker-compose up -d
```

## Advanced Usage

### Running Tests

To run the test suite:

```bash
docker-compose exec backend pytest
```

For a specific test file:

```bash
docker-compose exec backend pytest backend/tests/test_file.py
```

### Using Mock Mode

To enable mock mode for development without real LLM services:

1. Set `USE_MOCK=true` in your `.env` file
2. Restart the backend service:
   ```bash
   docker-compose restart backend
   ```

### Shell Access

To get a shell inside a container:

```bash
docker-compose exec backend bash
```

### Running One-off Commands

To run a single command:

```bash
docker-compose run --rm backend python -c "print('Hello from container')"
```

## Troubleshooting

### Common Issues

#### Services Won't Start

Check for port conflicts:

```bash
docker-compose ps
netstat -tuln | grep 8000
```

#### Database Connection Issues

Verify environment variables:

```bash
docker-compose config
```

Check database logs:

```bash
docker-compose logs db
```

#### Container Exits Immediately

Check startup logs:

```bash
docker-compose logs backend
```

### Resetting the Environment

For a clean slate:

```bash
docker-compose down -v
docker-compose up --build
```

## Best Practices

1. **Don't run as root**: The Dockerfile is configured to run as a non-root user
2. **Persist important data**: Use volumes for any data you need to keep
3. **Keep environment variables secure**: Don't commit `.env` files to git
4. **Use descriptive container names**: Makes debugging easier
5. **Regularly prune Docker resources**: Use `docker system prune` to free space
