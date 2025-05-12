# Docker Compose for Ultra Development

This directory contains Docker-related files for running Ultra in a containerized development environment.

## Structure

- `docker-compose.yml` - Main Docker Compose configuration for development
- `docker-compose.ci.yml` - Docker Compose configuration for CI environments
- `postgres/` - PostgreSQL initialization scripts and configuration
- `redis/` - Redis configuration (if needed)
- `.env` - Environment variables loaded by Docker Compose (create by copying .env.example)

## Quick Start

1. Make sure Docker and Docker Compose are installed on your system
2. Copy `.env.example` to `.env` in the root directory
3. Start the environment:

```bash
docker-compose up
```

Or in detached mode:

```bash
docker-compose up -d
```

4. Access the services:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3009
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

## Services

### Backend

The Ultra backend service, running the FastAPI application.

- Built from the Dockerfile in the root directory
- Automatically reloads when code changes
- Connects to PostgreSQL and Redis services

### PostgreSQL

Database service for Ultra.

- Persists data in a Docker volume
- Initializes with required tables
- Accessible on port 5432

### Redis

Cache and message broker for Ultra.

- Persists data in a Docker volume
- Accessible on port 6379

### Frontend (Optional)

The Ultra frontend service.

- React application served from a Node container
- Automatically rebuilds when code changes
- Connects to the backend service

## Useful Commands

### View running containers

```bash
docker-compose ps
```

### View logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
```

### Execute commands in containers

```bash
# Run pytest in backend container
docker-compose exec backend pytest

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d ultra
```

### Restart services

```bash
docker-compose restart backend
```

### Stop all services

```bash
docker-compose down
```

### Stop and remove all data

```bash
docker-compose down -v
```

## Development Workflow

1. Make changes to your code locally
2. The changes will be reflected immediately in the container (auto-reload)
3. Run tests inside the container:
   ```bash
   docker-compose exec backend pytest
   ```
4. When adding new Python dependencies:
   - Add them to requirements.txt
   - Rebuild the container: `docker-compose build backend`

## Troubleshooting

### Services Not Starting

Check the logs for errors:

```bash
docker-compose logs
```

### Database Connection Issues

Verify PostgreSQL is running:

```bash
docker-compose ps postgres
```

Check PostgreSQL logs:

```bash
docker-compose logs postgres
```

### Cache Connection Issues

Verify Redis is running:

```bash
docker-compose ps redis
```

Check Redis logs:

```bash
docker-compose logs redis
```

### Container Network Issues

Verify the network is properly set up:

```bash
docker network ls
docker network inspect ultra-network
```