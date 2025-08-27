# UltraAI Core Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Deployment Platforms](#deployment-platforms)
4. [Monitoring Setup](#monitoring-setup)
5. [Security Considerations](#security-considerations)
6. [Troubleshooting](#troubleshooting)

## Overview

UltraAI Core is a production-ready FastAPI application with React frontend, designed for multi-model LLM orchestration. This guide covers deployment to Render.com and general deployment best practices.

## Environment Variables

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | Yes |
| `DEBUG` | Enable debug mode | `false` | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `PORT` | Application port | `8000` | No |

### Feature Flags

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_AUTH` | Enable JWT authentication | `true` | Yes |
| `ENABLE_RATE_LIMIT` | Enable rate limiting | `true` | Yes |
| `ENABLE_CACHE` | Enable Redis caching | `true` | Yes |
| `ENABLE_TELEMETRY` | Enable OpenTelemetry | `true` | No |
| `MOCK_MODE` | Use mock LLM responses | `false` | Yes |

### LLM Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEFAULT_PROVIDER` | Default LLM provider | `openai` | No |
| `DEFAULT_MODEL` | Default LLM model | `gpt-4o` | No |
| `MODEL_TIMEOUT_SECONDS` | LLM request timeout | `45` | No |
| `MAX_RETRIES` | Max retry attempts | `3` | No |

### API Keys

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Conditional |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Conditional |
| `GOOGLE_API_KEY` | Google AI API key | - | Conditional |
| `HUGGINGFACE_API_KEY` | HuggingFace API key | - | Conditional |

**Note**: At least one LLM API key is required unless `MOCK_MODE=true`.

### Security

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET` | JWT signing secret | - | Yes (prod) |
| `ENCRYPTION_KEY` | Data encryption key | - | Yes (prod) |
| `ALLOWED_ORIGINS` | CORS allowed origins | - | Yes |
| `CSP_POLICY` | Content Security Policy | See render.yaml | No |

### Database & Cache

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Conditional |
| `REDIS_URL` | Redis connection string | - | Conditional |

### Rate Limiting

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Requests per minute | `60` | No |
| `RATE_LIMIT_BURST` | Burst allowance | `10` | No |

### Monitoring

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | `true` | No |
| `LOKI_URL` | Loki log aggregation URL | - | No |
| `SENTRY_DSN` | Sentry error tracking DSN | - | No |

## Deployment Platforms

### Render.com Deployment

1. **Prerequisites**:
   - GitHub repository connected to Render
   - Render account with appropriate plan

2. **Setup Steps**:
   ```bash
   # Ensure render.yaml is in repository root
   git add render.yaml
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

3. **Configure via Dashboard**:
   - Navigate to [Render Dashboard](https://dashboard.render.com)
   - Create new Web Service from GitHub repo
   - Select branch (usually `main`)
   - Render will detect `render.yaml` automatically

4. **Set Secret Environment Variables**:
   In Render dashboard, add:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY` 
   - `GOOGLE_API_KEY`
   - Any other sensitive values

5. **Deploy**:
   - Click "Create Web Service"
   - Monitor build logs
   - Access at `https://your-service.onrender.com`

### Manual Deployment (VPS/Docker)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-org/ultrai-core.git
   cd ultrai-core
   ```

2. **Install Dependencies**:
   ```bash
   # Python dependencies
   pip install poetry
   poetry install --no-dev
   
   # Frontend build
   cd frontend
   npm ci
   npm run build
   cd ..
   ```

3. **Set Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

4. **Run with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Monitoring Setup

### Local Monitoring Stack

1. **Start Monitoring Services**:
   ```bash
   cd monitoring
   docker-compose up -d
   ```

2. **Access Services**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (admin/admin)
   - Alertmanager: http://localhost:9093

3. **Import Dashboard**:
   - Login to Grafana
   - Go to Dashboards → Import
   - Upload `monitoring/grafana/dashboards/ultrai-core-dashboard.json`

### Production Monitoring

1. **Prometheus Metrics**:
   - Endpoint: `/api/metrics`
   - Scrape interval: 15s recommended

2. **Custom Metrics Available**:
   - `http_requests_total` - Total HTTP requests
   - `http_request_duration_seconds` - Request latency
   - `llm_requests_total` - LLM API calls by provider
   - `llm_cost_total` - Cumulative LLM costs
   - `pipeline_stage_duration_seconds` - Pipeline stage timing
   - `rate_limit_exceeded_total` - Rate limit violations

3. **Log Aggregation**:
   - Configure `LOKI_URL` for centralized logging
   - Logs follow structured JSON format
   - Includes correlation IDs for request tracing

## Security Considerations

### Production Checklist

- [ ] Set strong `JWT_SECRET` (min 32 chars)
- [ ] Set unique `ENCRYPTION_KEY` 
- [ ] Configure `ALLOWED_ORIGINS` restrictively
- [ ] Enable all security middleware
- [ ] Use HTTPS only (handled by Render)
- [ ] Rotate API keys regularly
- [ ] Monitor rate limit violations
- [ ] Review CSP policy for your needs

### API Key Management

1. **Never commit API keys to git**
2. **Use environment variables only**
3. **Rotate keys quarterly**
4. **Monitor usage for anomalies**

## Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check Poetry lock file
   poetry lock --no-update
   
   # Clear caches
   poetry cache clear pypi --all
   ```

2. **Frontend Build Issues**:
   ```bash
   # Clean install
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

3. **Database Connection**:
   - Verify `DATABASE_URL` format
   - Check network connectivity
   - Ensure database is initialized

4. **Redis Connection**:
   - Verify `REDIS_URL` format
   - Check Redis memory policy
   - Monitor eviction rates

### Health Checks

- Main health endpoint: `/health`
- Detailed health: `/api/health/services`
- Prometheus metrics: `/api/metrics`

### Performance Tuning

1. **Worker Configuration**:
   - Increase workers for high traffic
   - Use `--loop uvloop` for better performance
   - Monitor memory usage per worker

2. **Database Optimization**:
   - Enable connection pooling
   - Configure appropriate pool size
   - Add indexes for common queries

3. **Caching Strategy**:
   - Use Redis for session storage
   - Cache LLM responses when appropriate
   - Set reasonable TTLs

## Continuous Deployment

### GitHub Actions Setup

See `.github/workflows/deploy.yml` for automated deployment pipeline that:
1. Runs tests on push
2. Builds Docker images
3. Deploys to Render on main branch
4. Sends deployment notifications

### Rollback Strategy

1. **Via Render Dashboard**:
   - Navigate to service
   - Click "Events" tab
   - Select previous successful deploy
   - Click "Rollback"

2. **Via Git**:
   ```bash
   git revert HEAD
   git push origin main
   ```