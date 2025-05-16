# Deployment Validation Guide

## Pre-Deployment Checks

### Environment Setup

```bash
# Check environment file exists
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"

# Validate required variables
for var in ENVIRONMENT API_PORT JWT_SECRET DATABASE_URL; do
  grep -q "^$var=" .env && echo "✅ $var set" || echo "❌ $var missing"
done
```

### Docker Validation

```bash
# Test Docker build
docker build -t ultra-mvp .

# Test Docker Compose
docker compose config

# Check service health
docker compose ps
```

### Database Setup

```bash
# Test database connection
python -c "from backend.database.connection import get_db; print('✅ DB connection OK')"

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

## Deployment Process

### 1. Start Services

```bash
# Start in detached mode
docker compose up -d

# Check logs
docker compose logs -f
```

### 2. Health Checks

```bash
# Backend health
curl -f http://localhost:8000/api/health || echo "Backend health check failed"

# Frontend health
curl -f http://localhost:3009 || echo "Frontend health check failed"

# Database health
docker compose exec postgres pg_isready || echo "Database health check failed"

# Redis health
docker compose exec redis redis-cli ping || echo "Redis health check failed"
```

### 3. Functional Tests

```bash
# Test API endpoints
python test_api.py --base-url http://localhost:8000

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Test LLM integration
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "models": ["gpt-4"]}'
```

### 4. Performance Validation

```bash
# Basic load test
ab -n 100 -c 10 http://localhost:8000/api/health

# Response time check
time curl http://localhost:8000/api/available-models
```

## Post-Deployment Verification

### Monitor Logs

```bash
# Application logs
docker compose logs -f backend

# Error logs
docker compose logs backend | grep ERROR

# Access logs
tail -f logs/access.log
```

### Check Metrics

```bash
# CPU usage
docker stats

# Memory usage
docker compose exec backend cat /proc/meminfo

# Disk usage
df -h
```

### Verify Backups

```bash
# Database backup
docker compose exec postgres pg_dump -U ultra ultra_prod > backup.sql

# Verify backup
wc -l backup.sql
```

## Rollback Procedure

### 1. Stop Current Deployment

```bash
docker compose down
```

### 2. Restore Previous Version

```bash
# Checkout previous version
git checkout <previous-tag>

# Restore database if needed
docker compose exec postgres psql -U ultra ultra_prod < backup.sql
```

### 3. Restart Services

```bash
docker compose up -d
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   # Find process using port
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **Database Connection Failed**

   ```bash
   # Check database logs
   docker compose logs postgres
   # Test connection
   docker compose exec postgres psql -U ultra -d ultra_prod
   ```

3. **Redis Connection Failed**

   ```bash
   # Check Redis logs
   docker compose logs redis
   # Test connection
   docker compose exec redis redis-cli ping
   ```

4. **Frontend Not Loading**
   ```bash
   # Check nginx logs
   docker compose logs frontend
   # Verify build
   docker compose exec frontend ls -la /usr/share/nginx/html
   ```

## Success Criteria

- [ ] All services running
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Frontend accessible
- [ ] Database migrations complete
- [ ] Redis cache working
- [ ] Logs show no errors
- [ ] Performance acceptable
- [ ] Monitoring active
- [ ] Backups configured

## Sign-Off

**DevOps Engineer**: ******\_\_\_****** Date: ****\_\_\_****
**Backend Lead**: ********\_******** Date: ****\_\_\_****
**Frontend Lead**: ******\_\_\_\_****** Date: ****\_\_\_****
**QA Engineer**: ********\_\_******** Date: ****\_\_\_****
