# Routing Strategy: API vs Static Files

**Date**: 2025-05-22
**ACTION**: integrated-frontend-implementation

## FastAPI Route Priority

FastAPI processes routes in **definition order**, so API routes defined before static file mounting take precedence.

### Current Route Structure Analysis

#### Existing API Routes (from app_production.py)
```python
# Health endpoint
@app.get("/health")

# Authentication routes
@app.post("/auth/register")
@app.post("/auth/login") 
@app.get("/auth/verify")

# Document routes
@app.post("/documents/")
@app.get("/documents/")
@app.get("/documents/{document_id}")

# Analysis routes  
@app.post("/analyses/")
@app.get("/analyses/")
@app.get("/analyses/{analysis_id}")

# Current catch-all (to be replaced)
@app.get("/{path:path}")  # Returns basic HTML
```

### Proposed Static File Integration

#### Route Definition Order
```python
# 1. Health check (highest priority)
@app.get("/health")

# 2. API routes (protected from static file serving)
@app.post("/auth/register")
@app.post("/auth/login")
@app.get("/auth/verify")
@app.post("/documents/")
# ... all other API routes

# 3. Static file serving (catch-all, lowest priority)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

## URL Resolution Strategy

### API Endpoints (Protected Routes)
- `/health` → Health check endpoint
- `/auth/*` → Authentication endpoints
- `/documents/*` → Document management
- `/analyses/*` → Analysis operations

### Static File Routes (Fallback)
- `/` → `static/index.html`
- `/login.html` → `static/login.html`
- `/dashboard.html` → `static/dashboard.html`
- `/css/*` → `static/css/*`
- `/js/*` → `static/js/*`
- `/assets/*` → `static/assets/*`

### Special Considerations

#### SPA Routing with `html=True`
- Unknown routes fallback to `index.html`
- Client-side JavaScript handles route changes
- History API for navigation without page refresh

#### CORS Elimination
- Same-origin requests (no CORS issues)
- Simplified authentication (same domain cookies)
- No preflight requests needed

## Implementation Changes Required

### 1. Remove Existing Catch-All Route
```python
# REMOVE: Current catch-all route (line ~580)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    # This entire function needs to be removed
```

### 2. Remove Existing Static Mount
```python
# REMOVE: Current partial static mount (lines 595-606)
frontend_dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    try:
        app.mount("/assets", StaticFiles(...))
    # This entire section needs to be removed
```

### 3. Add New Static Mount
```python
# ADD: After all API route definitions
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

## File Resolution Examples

### Successful Resolution Flow
```
Request: GET /login.html
1. Check API routes: No match
2. Check static files: Found static/login.html
3. Serve: static/login.html

Request: GET /auth/login
1. Check API routes: Match found
2. Execute: POST /auth/login endpoint
3. Serve: JSON response

Request: GET /css/main.css  
1. Check API routes: No match
2. Check static files: Found static/css/main.css
3. Serve: static/css/main.css with text/css MIME type
```

### SPA Routing Flow
```
Request: GET /unknown-route
1. Check API routes: No match
2. Check static files: No static/unknown-route file
3. html=True fallback: Serve static/index.html
4. Client JS: Handle routing on index.html
```

## Development vs Production

### Development Environment
- FastAPI serves static files directly
- No caching (files reload automatically)
- Debug mode enabled
- CORS unnecessary (same origin)

### Production Environment (Render)
- FastAPI serves static files (same as dev)
- Static files cached by Render CDN
- Production mode optimizations
- HTTPS enabled by default

## Security Considerations

### Route Protection
- API routes require authentication headers
- Static files are public (by design)
- No sensitive data in static files
- Authentication handled by API layer

### Static File Security
- No server-side code in static files
- Client-side code is public
- API keys stored as environment variables (server-side only)
- JWT tokens managed by client JavaScript

## Performance Implications

### Benefits
- Single service reduces latency
- No CORS preflight requests
- Cached static assets
- Simplified deployment

### Optimizations
- Static file compression (gzip)
- Cache headers for assets
- Minimize JavaScript bundle size
- Optimize image assets

## Testing Strategy

### Route Testing
```python
# Test API routes still work
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200

# Test static file serving
def test_static_file_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Test route precedence
def test_api_route_precedence():
    # Ensure API routes take precedence over static files
    response = client.get("/auth/verify")
    assert response.status_code in [200, 401]  # API response, not 404
```

### Integration Testing
- Verify frontend can call API endpoints
- Test authentication flow end-to-end
- Validate file upload functionality
- Confirm static asset loading

## Migration Steps

1. **Backup current app_production.py**
2. **Remove existing static file logic**
3. **Create static/ directory structure**
4. **Add new static mount after API routes**
5. **Test route resolution**
6. **Deploy and verify production**