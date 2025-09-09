# Middleware Stack Order Documentation

## Current Middleware Stack (in execution order)

1. **CORS Middleware** (FastAPI built-in)
   - Must be first to handle preflight requests
   - Configures allowed origins, methods, headers

2. **Security Headers Middleware**
   - Adds security headers (CSP, HSTS, X-Frame-Options, etc.)
   - Runs early to ensure all responses have security headers

3. **Request ID Middleware**
   - Generates/propagates correlation IDs
   - Must run before logging middleware

4. **Performance Middleware**
   - Compression (gzip)
   - Cache headers
   - Must run before response is sent

5. **Structured Logging Middleware**
   - Request/response logging with correlation IDs
   - Samples requests to avoid log spam

6. **Telemetry Middleware**
   - OpenTelemetry traces and metrics
   - Tracks request duration and status

7. **Rate Limit Middleware**
   - Per-user/endpoint rate limiting
   - Runs before auth to prevent auth bypass attempts

8. **Authentication Middleware**
   - Combined JWT + API key authentication
   - Runs after rate limiting to prevent abuse

## Middleware Dependencies

- Request ID must run before any logging middleware
- Rate limiting must run before authentication
- Security headers should run early to ensure all responses are protected
- CORS must be first to handle OPTIONS requests

## Unused Middleware (to be removed)

- `api_key_middleware.py` - Replaced by combined auth
- `csrf_middleware.py` - Not needed for API-only backend
- `locale_middleware.py` - No localization requirements
- `validation_middleware.py` - Validation handled by FastAPI/Pydantic