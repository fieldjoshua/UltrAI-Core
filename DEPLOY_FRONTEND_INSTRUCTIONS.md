# UltraAI Frontend Deployment Instructions

## Overview
This guide covers deploying the UltraAI React frontend to Render as a static site that connects to your production backend.

## Prerequisites
- Backend already deployed at `https://ultrai-core.onrender.com`
- Render account with access
- Repository pushed to GitHub

## Deployment Steps

### 1. Create Frontend Service in Render

1. Go to your Render dashboard
2. Click "New +" → "Static Site"
3. Connect to your GitHub repository
4. Configure the service:
   - **Name**: `ultrai-frontend`
   - **Branch**: `main`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

### 2. Environment Variables

Add the following environment variable in Render:
- `VITE_API_URL`: `https://ultrai-core.onrender.com`

### 3. Deploy

Click "Create Static Site" to start the deployment.

## Alternative: Use render-frontend.yaml

```bash
# In your repository root
render deploy -m render-frontend.yaml
```

## Verification

Once deployed, your frontend will be available at:
- `https://ultrai-frontend.onrender.com`

The frontend will automatically connect to your backend API at:
- `https://ultrai-core.onrender.com`

## Test the Connection

1. Visit your frontend URL
2. Open browser developer console
3. You should see successful API calls to your backend
4. Test login functionality
5. Try uploading a document and running an analysis

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure your backend has the correct CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ultrai-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Failed
1. Check the VITE_API_URL environment variable
2. Verify backend is running at the correct URL
3. Check browser console for specific errors

## Local Testing

To test production configuration locally:
```bash
cd frontend
npm run build
npm run preview
```

## Next Steps

1. Set up custom domain if desired
2. Configure CDN for better performance
3. Add monitoring and analytics
4. Set up continuous deployment from GitHub