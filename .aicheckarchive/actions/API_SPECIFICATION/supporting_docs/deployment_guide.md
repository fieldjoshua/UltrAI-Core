# API Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the UltraAI API, including environment setup, configuration management, scaling considerations, and monitoring setup.

## Environment Setup

### Prerequisites

- Node.js 18.x or later
- Python 3.9 or later
- Docker 20.x or later
- Kubernetes 1.24 or later (for production)
- PostgreSQL 14.x or later
- Redis 6.x or later

### Development Environment

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ultraai/api.git
   cd api
   ```

2. **Install Dependencies**

   ```bash
   # Install Node.js dependencies
   npm install

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Server**

   ```bash
   npm run dev
   ```

### Production Environment

1. **Build Docker Images**

   ```bash
   docker build -t ultraai/api:latest .
   ```

2. **Deploy with Docker Compose**

   ```bash
   docker-compose up -d
   ```

3. **Deploy with Kubernetes**

   ```bash
   kubectl apply -f k8s/
   ```

## Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Environment (development/production) | development | Yes |
| `PORT` | API server port | 3000 | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `JWT_SECRET` | JWT signing secret | - | Yes |
| `API_KEY_SECRET` | API key encryption secret | - | Yes |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | 60 | No |
| `RATE_LIMIT_MAX` | Maximum requests per window | 60 | No |

### Configuration Files

1. **API Configuration**

   ```javascript
   // config/api.js
   module.exports = {
     port: process.env.PORT || 3000,
     rateLimit: {
       window: process.env.RATE_LIMIT_WINDOW || 60,
       max: process.env.RATE_LIMIT_MAX || 60
     },
     cors: {
       origin: process.env.CORS_ORIGIN || '*',
       methods: ['GET', 'POST', 'PUT', 'DELETE']
     }
   };
   ```

2. **Database Configuration**

   ```javascript
   // config/database.js
   module.exports = {
     url: process.env.DATABASE_URL,
     pool: {
       min: 2,
       max: 10
     },
     migrations: {
       directory: './migrations'
     }
   };
   ```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration**

   ```nginx
   # nginx.conf
   upstream api_servers {
     server api1:3000;
     server api2:3000;
     server api3:3000;
   }

   server {
     listen 80;
     server_name api.ultra.ai;

     location / {
       proxy_pass http://api_servers;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
     }
   }
   ```

2. **Kubernetes Deployment**

   ```yaml
   # k8s/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: api
     template:
       metadata:
         labels:
           app: api
       spec:
         containers:
         - name: api
           image: ultraai/api:latest
           ports:
           - containerPort: 3000
           resources:
             limits:
               cpu: "1"
               memory: "1Gi"
             requests:
               cpu: "500m"
               memory: "512Mi"
   ```

### Vertical Scaling

1. **Resource Limits**

   ```yaml
   # k8s/resource-limits.yaml
   resources:
     limits:
       cpu: "2"
       memory: "2Gi"
     requests:
       cpu: "1"
       memory: "1Gi"
   ```

2. **Database Scaling**

   ```yaml
   # k8s/database.yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: postgres-data
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 100Gi
   ```

## Monitoring Setup

### Prometheus Configuration

1. **Metrics Endpoint**

   ```javascript
   // metrics.js
   const prometheus = require('prom-client');
   const collectDefaultMetrics = prometheus.collectDefaultMetrics;
   collectDefaultMetrics();

   const httpRequestDuration = new prometheus.Histogram({
     name: 'http_request_duration_seconds',
     help: 'Duration of HTTP requests in seconds',
     labelNames: ['method', 'route', 'status_code']
   });

   module.exports = {
     metrics: prometheus,
     httpRequestDuration
   };
   ```

2. **Prometheus Configuration**

   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   scrape_configs:
     - job_name: 'api'
       static_configs:
         - targets: ['api:3000']
   ```

### Grafana Dashboards

1. **API Performance Dashboard**
   - Request rate
   - Response time
   - Error rate
   - Resource usage

2. **Business Metrics Dashboard**
   - Active users
   - API usage by endpoint
   - Rate limit hits
   - Authentication failures

## Deployment Checklist

### Pre-deployment

- [ ] Run all tests
- [ ] Check security vulnerabilities
- [ ] Verify environment variables
- [ ] Backup database
- [ ] Check resource availability

### Deployment

- [ ] Deploy database migrations
- [ ] Deploy API servers
- [ ] Update load balancer
- [ ] Verify health checks
- [ ] Monitor error rates

### Post-deployment

- [ ] Verify API functionality
- [ ] Check monitoring systems
- [ ] Test rate limiting
- [ ] Verify authentication
- [ ] Monitor performance

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   ```bash
   # Check database connection
   psql $DATABASE_URL -c "SELECT 1"
   ```

2. **Redis Connection Issues**

   ```bash
   # Check Redis connection
   redis-cli -u $REDIS_URL ping
   ```

3. **API Server Issues**

   ```bash
   # Check API server logs
   kubectl logs -f deployment/api
   ```

### Debugging Tools

1. **API Debug Mode**

   ```bash
   # Enable debug logging
   export DEBUG=api:*
   npm start
   ```

2. **Database Debugging**

   ```bash
   # Enable query logging
   export PGDEBUG=1
   ```

## Related Documentation

- [API Specification Plan](../API_SPECIFICATION-PLAN.md)
- [Authentication Guide](./authentication_guide.md)
- [Rate Limiting Guide](./rate_limiting_guide.md)

## Last Updated

2024-03-26
