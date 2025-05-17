# Production Deployment Checklist

This checklist must be completed before deploying Ultra to production.

## Pre-Deployment Requirements

### 1. Environment Configuration
- [ ] Copy `.env.production.template` to `.env.production`
- [ ] Generate JWT_SECRET using `python3 scripts/generate_jwt_secret.py`
- [ ] Set DATABASE_URL with production PostgreSQL credentials
- [ ] Set REDIS_URL with production Redis credentials
- [ ] Configure all required API keys:
  - [ ] OPENAI_API_KEY
  - [ ] ANTHROPIC_API_KEY
  - [ ] GOOGLE_API_KEY
- [ ] Set ALLOWED_HOSTS and CORS_ORIGINS for your domain
- [ ] Configure SMTP settings for email functionality
- [ ] Set up Sentry DSN for error tracking
- [ ] Review and adjust all security settings

### 2. Database Setup
- [ ] Run `python3 scripts/setup_production_database.py` to verify connection
- [ ] Apply all migrations: `alembic upgrade head`
- [ ] Verify database schema is correct
- [ ] Set up database backups
- [ ] Configure read replicas if needed

### 3. Redis Setup
- [ ] Run `python3 scripts/setup_production_redis.py` to verify connection
- [ ] Test cache operations
- [ ] Test rate limiting
- [ ] Configure Redis persistence
- [ ] Set up Redis monitoring

### 4. Security Configuration
- [ ] SSL/TLS certificates are installed
- [ ] Security headers are properly configured
- [ ] CSRF protection is enabled
- [ ] Rate limiting is configured
- [ ] API key authentication is working
- [ ] JWT authentication is tested
- [ ] All sensitive data is encrypted

### 5. Logging and Monitoring
- [ ] Production logging is configured
- [ ] Log rotation is set up
- [ ] Sentry error tracking is working
- [ ] Health check endpoints are accessible
- [ ] Metrics collection is enabled
- [ ] Monitoring alerts are configured

### 6. Infrastructure
- [ ] Docker images are built: `docker build -t ultra:latest .`
- [ ] Docker Compose production file is configured
- [ ] Load balancer is configured
- [ ] Auto-scaling is set up
- [ ] Backup strategy is implemented
- [ ] Disaster recovery plan is documented

### 7. Performance
- [ ] Database indexes are optimized
- [ ] Query performance is tested
- [ ] Cache hit rates are monitored
- [ ] Connection pooling is configured
- [ ] Static assets are served via CDN
- [ ] Compression is enabled

### 8. Testing
- [ ] All unit tests pass: `python3 -m pytest backend/tests/`
- [ ] Integration tests pass
- [ ] Load testing is completed
- [ ] Security audit is performed
- [ ] Penetration testing is done

## Deployment Steps

1. **Final Configuration Check**
   ```bash
   python3 scripts/verify_production_config.py
   ```

2. **Build Docker Images**
   ```bash
   docker build -t ultra:latest .
   docker build -t ultra-frontend:latest ./frontend
   ```

3. **Database Migration**
   ```bash
   alembic upgrade head
   ```

4. **Deploy Services**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

5. **Verify Health**
   ```bash
   curl https://api.yourdomain.com/api/health
   ```

6. **Run Smoke Tests**
   ```bash
   python3 scripts/production_smoke_tests.py
   ```

## Post-Deployment

- [ ] Monitor error rates for first 24 hours
- [ ] Check performance metrics
- [ ] Review security logs
- [ ] Verify backup system is working
- [ ] Update documentation
- [ ] Notify team of successful deployment

## Rollback Plan

If issues occur:

1. Check error logs: `docker logs ultra-backend`
2. Rollback database if needed: `alembic downgrade -1`
3. Restore previous Docker images
4. Switch load balancer to maintenance mode
5. Investigate and fix issues
6. Re-deploy with fixes

## Environment Variables Reference

Critical environment variables that must be set:

```bash
# Application
ENVIRONMENT=production
USE_MOCK=false
DEBUG=false

# Security
JWT_SECRET=<generated-secret>
ALLOWED_HOSTS=["yourdomain.com"]
CORS_ORIGINS=["https://yourdomain.com"]

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_SSL_MODE=require

# Redis
REDIS_URL=redis://user:pass@host:6379/0
CACHE_TTL=3600

# API Keys
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
GOOGLE_API_KEY=your-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# Email
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-password
```

## Support

For deployment support:
- Check logs: `/var/log/ultra/production.log`
- Monitor dashboard: `https://monitoring.yourdomain.com`
- Contact: devops@ultrai.app