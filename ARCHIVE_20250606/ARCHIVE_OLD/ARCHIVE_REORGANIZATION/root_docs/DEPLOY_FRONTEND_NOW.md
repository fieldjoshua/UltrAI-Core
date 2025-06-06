# Deploy Frontend Right Now

Since the Render CLI isn't suitable for creating services programmatically, here's the most efficient way:

## Option 1: Blueprint Sync (Fastest)

I've already updated your `render.yaml` to include the frontend service. 

1. Go to your Render Dashboard: https://dashboard.render.com
2. Look for any notification about your blueprint being out of sync
3. If you see a "Sync" button, click it
4. This will automatically create the frontend service

## Option 2: Direct Creation 

If blueprint sync doesn't work:

1. Go to: https://dashboard.render.com/new/static
2. Connect your repository: `fieldjoshua/UltrAI-Core`
3. Use these exact settings:

```
Name: ultrai-frontend
Branch: main
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

4. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: `https://ultrai-core.onrender.com`

5. Click "Create Static Site"

## Option 3: Use Render's Deploy Button

Add this to your README and click it:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/fieldjoshua/UltrAI-Core)

## What Happens Next

After deployment starts:
1. Frontend will build (3-5 minutes)
2. It will be available at: https://ultrai-frontend.onrender.com
3. You'll need to update backend CORS settings to allow this URL

## Quick CORS Update

Once frontend is deployed, update your backend:

```python
# In app_production.py, update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3009", 
        "https://ultrai-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend.