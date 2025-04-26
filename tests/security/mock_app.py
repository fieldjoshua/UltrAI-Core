from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Add security middleware
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security dependencies
security = HTTPBearer()

# Rate limiting
from fastapi import Request
from fastapi.responses import JSONResponse
import time

# Simple in-memory rate limiter
request_counts = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    # Clean up old entries
    request_counts[client_ip] = [
        t for t in request_counts.get(client_ip, []) if current_time - t < 60
    ]

    # Check rate limit
    if len(request_counts.get(client_ip, [])) >= 100:
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    # Add current request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)

    return await call_next(request)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Search endpoint with input validation
@app.get("/api/search")
async def search(q: str):
    # Simple input validation
    if "'" in q or "<script>" in q:
        raise HTTPException(status_code=400, detail="Invalid input")
    return {"results": []}


# Authentication endpoints
@app.post("/api/auth/register")
async def register(username: str, password: str):
    # Simple password validation
    weak_passwords = ["password", "123456", "qwerty", "admin123"]
    if password in weak_passwords:
        raise HTTPException(status_code=400, detail="Weak password")
    return {"status": "ok"}


@app.post("/api/auth/login")
async def login(username: str, password: str):
    return {"token": "mock_token"}


# Protected endpoints
@app.get("/api/protected")
async def protected(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"data": "protected_data"}


# Admin endpoints
@app.get("/api/admin/users")
async def admin_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    raise HTTPException(status_code=403, detail="Admin access required")


# User-specific endpoints
@app.get("/api/users/{username}/profile")
async def user_profile(
    username: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if username != "current_user":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"profile": "user_profile"}


@app.get("/api/users/{username}/documents")
async def user_documents(
    username: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if username != "current_user":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"documents": []}
