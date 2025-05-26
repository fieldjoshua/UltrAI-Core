# Manual Frontend Deployment Instructions

Since the Render CLI doesn't support creating new services directly, here's how to deploy the frontend manually:

## Step 1: Login to Render Dashboard

1. Go to https://dashboard.render.com
2. Login with your account

## Step 2: Create New Static Site

1. Click the "New +" button
2. Select "Static Site"

## Step 3: Connect Your Repository

1. Choose "Build and deploy from a GitHub repository"
2. Connect your GitHub account if needed
3. Select the "Ultra" repository

## Step 4: Configure the Service

Use these exact settings:

- **Name**: `ultrai-frontend`
- **Region**: Same as your backend (e.g., Oregon USA West)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist`

## Step 5: Add Environment Variables

Click "Add Environment Variable" and add:
- **Key**: `VITE_API_URL`
- **Value**: `https://ultrai-core.onrender.com`

## Step 6: Create Static Site

Click "Create Static Site" at the bottom of the form.

## Step 7: Wait for Deployment

The deployment will take 3-5 minutes. You can watch the progress in the logs.

## Step 8: Access Your Frontend

Once deployed, your frontend will be available at:
- https://ultrai-frontend.onrender.com

## Next Steps

After deployment:

1. Update your backend CORS settings to allow the frontend URL
2. Test the full application
3. Consider setting up a custom domain

## Alternative: Using render.yaml

If you want to manage both services together, create a combined `render.yaml`:

```yaml
services:
  # Backend service
  - type: web
    name: ultrai-core
    runtime: python
    buildCommand: "pip install -r requirements-production.txt"
    startCommand: "uvicorn app_production:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: ultrai-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: ultrai-redis
          type: redis
          property: connectionString
      - key: JWT_SECRET_KEY
        generateValue: true
  
  # Frontend service
  - type: web
    name: ultrai-frontend
    runtime: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
    headers:
      - path: /*
        name: X-Frame-Options
        value: SAMEORIGIN
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_URL
        value: https://ultrai-core.onrender.com

databases:
  - name: ultrai-db
    engine: postgres
    ipAllowList: []

redis:
  - name: ultrai-redis
    type: redis
```

Then commit this file and Render will automatically manage both services.