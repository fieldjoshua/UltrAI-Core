# Service Requirements for Docker Compose Setup

## Overview

This document outlines the requirements for services to be included in the Docker Compose configuration for the Ultra project. It covers configuration parameters, networking requirements, volume needs, and initialization scripts.

## Service Requirements

### PostgreSQL

| Parameter             | Value                                             | Notes                                        |
| --------------------- | ------------------------------------------------- | -------------------------------------------- |
| Version               | 15                                                | Latest stable version with long-term support |
| Port                  | 5432                                              | Standard PostgreSQL port                     |
| Environment Variables | POSTGRES_USER<br>POSTGRES_PASSWORD<br>POSTGRES_DB | Will be stored in .env file                  |
| Volume                | postgres-data                                     | For data persistence                         |
| Network               | ultra-network                                     | For internal service communication           |
| Init Scripts          | init-db.sql                                       | Creates default schema and tables            |
| Health Check          | pg_isready                                        | For readiness checking                       |

### Redis

| Parameter    | Value                         | Notes                              |
| ------------ | ----------------------------- | ---------------------------------- |
| Version      | 7                             | Latest stable version              |
| Port         | 6379                          | Standard Redis port                |
| Command      | redis-server --appendonly yes | Enable AOF persistence             |
| Volume       | redis-data                    | For data persistence               |
| Network      | ultra-network                 | For internal service communication |
| Health Check | redis-cli ping                | For readiness checking             |

### Backend Service

| Parameter             | Value                                             | Notes                              |
| --------------------- | ------------------------------------------------- | ---------------------------------- |
| Base Image            | python:3.12-slim                                  | Lightweight Python image           |
| Working Directory     | /app                                              | Standard container directory       |
| Volumes               | .:/app                                            | Mount local code for development   |
| Network               | ultra-network                                     | For internal service communication |
| Environment Variables | DATABASE_URL<br>REDIS_URL<br>USE_MOCK<br>API_KEYS | Will be stored in .env file        |
| Dependencies          | Depends on PostgreSQL and Redis                   | Wait for dependencies to be ready  |
| Command               | python -m uvicorn backend.app:app --host 0.0.0.0  | Run the API server                 |
| Health Check          | curl -f http://localhost:8000/health              | For readiness checking             |
| Build Context         | .                                                 | Current directory                  |
| Dockerfile            | Dockerfile                                        | Custom Dockerfile for backend      |

## Network Configuration

We'll create a dedicated bridge network named `ultra-network` for internal service communication. This will provide:

1. DNS resolution between containers
2. Isolated network segment
3. Consistent naming for services

## Volume Management

Data volumes will be managed through named volumes for persistence between container restarts:

1. `postgres-data`: PostgreSQL data files
2. `redis-data`: Redis data files

## Environment Variables

Environment variables will be managed through a `.env` file with the following structure:

```
# PostgreSQL
POSTGRES_USER=ultra
POSTGRES_PASSWORD=ultra_dev_password
POSTGRES_DB=ultra_dev

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
DATABASE_URL=postgresql://ultra:ultra_dev_password@postgres:5432/ultra_dev
USE_MOCK=true
LOG_LEVEL=debug
```

## Initialization Scripts

### PostgreSQL Initialization

We'll create an initialization script `init-db.sql` to set up the database schema:

```sql
-- Create necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema
CREATE SCHEMA IF NOT EXISTS ultra;

-- Set search path
SET search_path TO ultra,public;

-- Create basic tables
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add some test data
INSERT INTO users (username, email)
VALUES ('testuser', 'test@example.com')
ON CONFLICT DO NOTHING;
```

## Docker Compose File Structure

The docker-compose.yml file will follow this structure:

```yaml
version: '3.8'

services:
  postgres:
    # PostgreSQL service configuration

  redis:
    # Redis service configuration

  backend:
    # Backend service configuration

networks:
  ultra-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
```

## Development Workflow

The proposed development workflow will be:

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Run `docker-compose up`
4. Access the API at http://localhost:8000
5. For code changes, containers will reload automatically

## CI Integration Considerations

For CI integration, we'll need to:

1. Create a separate `docker-compose.ci.yml` file
2. Use fixed environment variables for CI
3. Run all tests in containerized environment
4. Add container cleanup steps
