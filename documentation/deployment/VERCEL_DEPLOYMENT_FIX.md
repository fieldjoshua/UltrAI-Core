# Vercel Deployment Fix

## Issue
Vercel is trying to build the Python backend instead of the React frontend, causing build failures with errors like:
- `sh: line 1: vite: command not found`
- Installing Python packages instead of Node packages

## Solution
In your Vercel project settings:

1. Go to **Settings** → **General**
2. Find **Root Directory** setting
3. Change it to: `frontend`
4. Save changes
5. Trigger a new deployment

## Why This Works
- The repository has both backend (Python/FastAPI) and frontend (React/Vite) code
- Vercel needs to know which directory contains the frontend code
- Setting Root Directory to `frontend` tells Vercel to:
  - Run `npm install` in the frontend directory
  - Use the `frontend/package.json` and `frontend/vercel.json`
  - Build the React/Vite application correctly

## Verification
After updating the setting, the build logs should show:
- Installing Node.js packages (react, vite, etc.)
- Running `vite build`
- Creating `dist` directory with static files

## Frontend Configuration
The frontend is already configured correctly with:
- `frontend/vercel.json` - Vercel-specific settings
- `frontend/vite.config.production.ts` - Production build configuration
- API URL pointing to: `https://ultrai-core-4lut.onrender.com`