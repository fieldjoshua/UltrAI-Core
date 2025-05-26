# MVP Dependency Audit Report

Generated: 2025-05-17

## Summary

This audit analyzes all dependencies required to maintain ALL MVP functionality in a minimal deployment on Render.

## MVP Feature to Dependency Mapping

| MVP Feature             | Required Components         | Dependencies                                                       | Status      | Justification                   |
| ----------------------- | --------------------------- | ------------------------------------------------------------------ | ----------- | ------------------------------- |
| **API Framework**       | Web server, routing         | fastapi, uvicorn, gunicorn                                         | REQUIRED    | Core framework for API          |
| **Data Validation**     | Request/response validation | pydantic, python-multipart                                         | REQUIRED    | Essential for API functionality |
| **Database & ORM**      | Data persistence            | sqlalchemy, psycopg2-binary, alembic                               | REQUIRED    | User accounts, document storage |
| **Authentication**      | JWT, password hashing       | PyJWT, passlib, python-jose[cryptography], bcrypt, email-validator | REQUIRED    | User authentication system      |
| **LLM Orchestration**   | Provider APIs               | openai, anthropic, google-generativeai                             | REQUIRED    | Core MVP feature                |
| **HTTP Clients**        | API communication           | httpx, aiohttp                                                     | REQUIRED    | LLM API calls, SSE support      |
| **SSE Support**         | Real-time updates           | sse-starlette                                                      | REQUIRED    | Found as missing dependency     |
| **Retry Logic**         | Error resilience            | tenacity, backoff                                                  | REQUIRED    | LLM reliability                 |
| **Configuration**       | Environment setup           | python-dotenv, pyyaml                                              | REQUIRED    | Config management               |
| **Caching**             | Performance                 | redis, diskcache                                                   | RECOMMENDED | Can degrade gracefully          |
| **Document Processing** | File handling               | python-magic, chardet                                              | MINIMAL     | Basic file detection            |
| **PDF Processing**      | Document analysis           | pypdf2                                                             | OPTIONAL    | Can be optional for MVP         |
| **DOCX Processing**     | Document analysis           | python-docx                                                        | OPTIONAL    | Can be optional for MVP         |
| **HTML Processing**     | Document analysis           | beautifulsoup4, markdownify                                        | OPTIONAL    | Can be optional for MVP         |
| **Security**            | Encryption                  | cryptography                                                       | REQUIRED    | For auth/JWT                    |
| **Monitoring**          | Metrics                     | prometheus-client                                                  | OPTIONAL    | Not critical for MVP            |
| **Error Tracking**      | Debugging                   | sentry-sdk                                                         | OPTIONAL    | Not critical for MVP            |
| **Resource Monitoring** | System metrics              | psutil                                                             | OPTIONAL    | Internal endpoint only          |

## Analysis Results

### Core Required Dependencies (Must Have)

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==23.0.0
pydantic==2.5.3
python-multipart==0.0.6

# Database (Required for MVP)
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication (Required for MVP)
PyJWT==2.8.0
passlib==1.7.4
python-jose[cryptography]==3.3.0
bcrypt==4.1.2
email-validator==2.0.0

# LLM Providers (Required for MVP)
openai==1.6.1
anthropic==0.40.0
google-generativeai==0.3.2

# HTTP & Communication
httpx==0.25.2
aiohttp==3.9.1
sse-starlette==1.6.5

# Configuration
python-dotenv==1.0.0
pyyaml==6.0.1

# Retry/Resilience
tenacity==8.2.3
backoff==2.2.1

# Security
cryptography==44.0.2
```

### Recommended Dependencies (Graceful Degradation)

```txt
# Caching
redis==5.1.1
diskcache==5.6.3

# Basic Document Processing
python-magic==0.4.27
chardet==5.2.0
```

### Optional Dependencies (Not Required for MVP)

```txt
# Advanced Document Processing
pypdf2==3.0.1
python-docx==1.1.0
beautifulsoup4==4.12.2
markdownify==0.11.6

# Monitoring
prometheus-client==0.19.0
sentry-sdk==1.40.0
psutil==6.1.0

# Data Processing (NOT NEEDED)
numpy==1.26.3
pandas==2.1.4
matplotlib==3.8.2
```

## Import Analysis of app_minimal.py

The following dependencies are checked at startup:

- sqlalchemy (REQUIRED)
- redis (OPTIONAL - falls back to in-memory cache)
- sentry_sdk (OPTIONAL - monitoring)
- prometheus_client (OPTIONAL - metrics)

## Key Findings

1. **Heavy dependencies removed**: numpy, pandas, matplotlib are NOT required for MVP
2. **Document processing can be minimal**: Only basic file detection needed, not full PDF/DOCX processing
3. **Monitoring is optional**: Sentry, Prometheus can be skipped for minimal deployment
4. **Cache can degrade**: Redis can fall back to in-memory or disk cache
5. **SSE is required**: sse-starlette was the missing dependency causing deployment failure

## Recommendation

Use the "Core Required Dependencies" list for requirements-render.txt. This provides:

- All MVP functionality preserved
- Minimal resource footprint
- Graceful degradation for optional features
- Fast startup time

Total: 26 core dependencies vs 71 in the full requirements file.
