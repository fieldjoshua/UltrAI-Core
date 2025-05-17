"""Minimal FastAPI app for Render deployment"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal app
app = FastAPI(title="Ultra API", version="1.0.0")

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ultra-api"}


# Basic test endpoint
@app.get("/api/test")
async def test():
    return {"message": "Ultra API is running"}


# Import main app routes if they work
try:
    from backend.routes import auth_routes, llm_routes

    app.include_router(auth_routes.auth_router)
    app.include_router(llm_routes.router)
except ImportError as e:
    print(f"Could not import routes: {e}")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Ultra API v1.0.0", "docs": "/docs"}
