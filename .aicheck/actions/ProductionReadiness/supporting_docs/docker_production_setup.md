# Docker Production Setup

This document outlines the Docker configuration for production deployment of Ultra.

## Production Docker Architecture

For a production-ready deployment, we recommend using the following architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  NGINX / Proxy  │◄───┤  Ultra Backend  │◄───┤  Redis Cache    │
│                 │    │                 │    │                 │
└────────┬────────┘    └────────┬────────┘    └─────────────────┘
         ▲                      │
         │                      ▼
┌────────┴────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Frontend       │    │  PostgreSQL DB  │    │  Monitoring     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Docker Compose for Production

The following `docker-compose.prod.yml` file can be used for production deployment:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend
    networks:
      - frontend-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env.production
    volumes:
      - document_storage:/app/document_storage
      - logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - frontend-network
      - backend-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env.db
    networks:
      - backend-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
    networks:
      - backend-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    env_file:
      - .env.monitoring
    ports:
      - "3000:3000"
    networks:
      - monitoring-network
    restart: unless-stopped

networks:
  frontend-network:
  backend-network:
  monitoring-network:

volumes:
  postgres_data:
  redis_data:
  document_storage:
  logs:
  prometheus_data:
  grafana_data:
```

## Nginx Configuration

For production, we recommend using Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name ultra.example.com;
    
    # Redirect to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ultra.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'" always;
    
    # Proxy Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }
    }
    
    # Proxy API Requests to Backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        limit_req_status 429;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health Check
    location /health {
        proxy_pass http://backend:8000/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Do not rate limit health checks
        limit_req_status 200;
    }
    
    # Error Pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
```

## Environment Files

### Production Environment (.env.production)

```bash
# Core
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://ultra.example.com
SECRET_KEY=${SECRET_KEY}

# Authentication
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
ENABLE_AUTH=true

# Database
DATABASE_URL=postgresql://ultrauser:${DB_PASSWORD}@postgres:5432/ultra
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# LLM Providers
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-opus-20240229

# Redis Cache
REDIS_URL=redis://redis:6379/0
ENABLE_CACHE=true
CACHE_TTL=3600

# Rate Limiting
ENABLE_RATE_LIMIT=true
RATE_LIMIT_STRATEGY=sliding
RATE_LIMIT_STORAGE=redis

# Storage
DOCUMENT_STORAGE_PATH=/app/document_storage
MAX_DOCUMENT_SIZE_MB=10

# Security
ENABLE_SECURITY_HEADERS=true
ENABLE_HTTPS_REDIRECT=true
API_KEY_ENCRYPTION_KEY=${API_KEY_ENCRYPTION_KEY}

# Features
USE_MOCK=false
MOCK_MODE=false
```

### Database Environment (.env.db)

```bash
POSTGRES_USER=ultrauser
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=ultra
```

### Monitoring Environment (.env.monitoring)

```bash
GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
GF_USERS_ALLOW_SIGN_UP=false
```

## Resource Requirements

For a production deployment, we recommend the following minimum resources:

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Backend   | 2   | 4GB    | 20GB |
| Database  | 2   | 4GB    | 50GB |
| Redis     | 1   | 2GB    | 10GB |
| Nginx     | 1   | 1GB    | 5GB  |

## Scaling Considerations

For higher load scenarios, consider:

1. Horizontal scaling of backend services
2. Database read replicas
3. Redis cluster
4. Load balancing across multiple nodes
5. Content delivery network (CDN) for static assets

## Monitoring and Logging

The setup includes Prometheus and Grafana for monitoring:

1. Backend service metrics (requests, response times, error rates)
2. Database performance metrics
3. System resource utilization
4. LLM API usage and costs

Logs are stored in a persistent volume for access and analysis.

## Security Considerations

1. All services run as non-root users
2. Secrets are injected via environment variables, not in images
3. Regular security updates for all components
4. TLS encryption for all communication
5. Network isolation through Docker networks
6. Rate limiting and DDoS protection

## Backup Strategy

1. Database backups at regular intervals
2. Document storage backups
3. Configuration backups
4. Automated backup verification

## Deployment Process

1. Build images with proper versioning
2. Run integration tests against staging environment
3. Deploy to production using blue-green deployment
4. Verify health checks and monitoring after deployment
5. Have rollback procedure ready in case of issues