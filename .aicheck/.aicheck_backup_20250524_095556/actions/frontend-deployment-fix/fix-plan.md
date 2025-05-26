# Frontend Deployment Fix Plan

## Problem Identified

The frontend IS being served from the backend, but the root API route (`@app.get("/")`) is intercepting all requests before they reach the static file handler.

## Current Setup

1. Line 214: `@app.get("/")` returns API status JSON
2. Line 532: `app.mount("/", StaticFiles(...))` tries to serve frontend
3. Result: API route wins, frontend never served

## Solution Options

### Option 1: Remove Root API Route (Simplest)
- Delete the `@app.get("/")` handler
- Let static files handle the root
- API endpoints remain at `/auth/*`, `/documents/*`, etc.

### Option 2: Move API Under `/api` Prefix
- Add `/api` prefix to all endpoints
- Keep root for frontend
- Requires updating all API calls

### Option 3: Serve Frontend from `/app`
- Mount frontend at `/app` instead of `/`
- Keep API at root
- Users access UI at `https://ultrai-core.onrender.com/app`

## Recommended Solution: Option 1

Remove the root API route. It's not essential and blocking the frontend.

## Implementation

1. Comment out or remove lines 214-221 (root route handler)
2. Test locally that frontend loads
3. Commit and push
4. Frontend should work immediately at https://ultrai-core.onrender.com/

## Alternative Quick Fix

If we can't modify code immediately, we could:
- Document that the frontend is at `/docs` (FastAPI's built-in UI)
- Users can still access all functionality through Swagger UI