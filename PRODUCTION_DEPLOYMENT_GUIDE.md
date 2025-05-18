# Production Deployment Guide

## Overview

This guide covers deploying the production-ready UltraAI application with full database support and caching.

## Prerequisites

1. Render account
2. GitHub repository connected to Render
3. Access to create PostgreSQL and Redis instances

## Step 1: Create PostgreSQL Database

1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Choose configuration:
   - Name: `ultrai-db`
   - Plan: Free (or upgrade as needed)
   - Region: Same as your web service
4. Click "Create Database"
5. Note the connection string:
   - Internal Database URL (for services in same region)
   - External Database URL (for external connections)

## Step 2: Create Redis Instance

### Option A: Upstash (Recommended for free tier)
1. Go to [upstash.com](https://upstash.com)
2. Create free account
3. Create Redis database:
   - Name: `ultrai-cache`
   - Region: Closest to your Render region
4. Get Redis URL from dashboard

### Option B: Render Redis
1. Go to Render Dashboard
2. Click "New +" → "Redis"
3. Configure and create
4. Note connection details

## Step 3: Configure Environment Variables

In Render Dashboard for your web service:

1. Go to Environment section
2. Add variables:
   ```
   DATABASE_URL = [PostgreSQL Internal URL from Step 1]
   REDIS_URL = [Redis URL from Step 2]
   JWT_SECRET = [Leave blank - Render will auto-generate]
   ```

## Step 4: Deploy Application

1. Ensure these files are in your repository:
   - `app_production.py`
   - `requirements-production.txt`
   - `render.yaml`

2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Add production deployment configuration"
   git push origin main
   ```

3. Render will automatically deploy

## Step 5: Verify Deployment

1. Wait for deployment to complete (check logs)
2. Run verification script:
   ```bash
   ./scripts/verify-production-deployment.sh
   ```

## Step 6: Test All Features

1. **Health Check**:
   ```bash
   curl https://ultrai-core.onrender.com/health
   ```
   Should show all services "connected"

2. **Authentication**:
   - Register user
   - Login
   - Verify token

3. **Document Management**:
   - Create document
   - List documents
   - Retrieve document

4. **Analysis with Caching**:
   - Create analysis
   - Repeat same analysis (should be cached)

## Troubleshooting

### Database Connection Issues
- Check DATABASE_URL format (postgres:// vs postgresql://)
- Verify database is in same region as web service
- Check database logs in Render

### Redis Connection Issues
- Verify REDIS_URL format
- Check Redis service is running
- Test with Redis CLI if available

### Authentication Issues
- Ensure JWT_SECRET is set
- Check token expiration settings
- Verify password hashing works

### Performance Issues
- Monitor cache hit rates
- Check database query performance
- Review application logs

## Monitoring

1. **Render Dashboard**:
   - Service metrics
   - Deployment history
   - Environment variables

2. **Application Health**:
   - `/health` endpoint
   - Database connectivity
   - Cache status

3. **Logs**:
   - Application logs
   - Database logs
   - Redis logs

## Scaling Considerations

1. **Database**:
   - Upgrade to paid plan for production
   - Enable connection pooling
   - Add read replicas if needed

2. **Redis**:
   - Monitor memory usage
   - Implement eviction policies
   - Consider Redis Cluster for high availability

3. **Web Service**:
   - Increase instance count
   - Upgrade instance type
   - Enable auto-scaling

## Security Best Practices

1. **Environment Variables**:
   - Never commit secrets to repository
   - Use Render's auto-generated secrets
   - Rotate JWT_SECRET periodically

2. **Database**:
   - Use internal URLs when possible
   - Enable SSL/TLS
   - Regular backups

3. **API**:
   - Rate limiting (future enhancement)
   - Input validation
   - CORS configuration

## Next Steps

1. Integrate actual LLM providers
2. Add monitoring/alerting
3. Implement rate limiting
4. Create frontend application
5. Set up CI/CD pipeline

## Support

- Render Documentation: https://render.com/docs
- UltraAI Issues: [Your GitHub Issues URL]
- Contact: [Your Contact Info]