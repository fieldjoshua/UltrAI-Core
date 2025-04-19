# UltraAI Cloud System Setup Guide

This guide provides instructions for setting up and deploying the UltraAI cloud system, which consists of a FastAPI backend and a JavaScript frontend.

## Local Setup & Testing

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Node.js and npm (for Vercel CLI)

### Steps for Local Development

1. **Clone or download the code**

   Make sure you have the following directory structure:

   ```
   ├── cloud_backend/
   │   ├── main.py
   │   ├── requirements.txt
   │   ├── vercel.json
   │   └── run_local.sh
   ├── cloud_frontend/
   │   ├── index.html
   │   ├── vercel.json
   │   └── run_local.sh
   ├── run_cloud_system.sh
   └── cloud_deployment.md
   ```

2. **Install backend dependencies**

   ```bash
   cd cloud_backend
   pip install -r requirements.txt
   ```

3. **Make scripts executable**

   ```bash
   chmod +x cloud_backend/run_local.sh
   chmod +x cloud_frontend/run_local.sh
   chmod +x run_cloud_system.sh
   ```

4. **Run the system locally**

   You can run both the backend and frontend together:

   ```bash
   ./run_cloud_system.sh
   ```

   Or run them separately:

   ```bash
   # In one terminal
   cd cloud_backend
   ./run_local.sh

   # In another terminal
   cd cloud_frontend
   ./run_local.sh
   ```

5. **Access the application**

   - Backend API: <http://localhost:8000>
   - Frontend interface: <http://localhost:8080>

### Testing the Local Setup

1. Visit <http://localhost:8080> in your browser
2. You should see the UltraAI interface with a green "LOCAL" indicator
3. Try submitting a prompt and selecting different models
4. Test the a la carte options and detailed analysis features

## Cloud Deployment with Vercel

### Prerequisites

- A Vercel account (<https://vercel.com>)
- Vercel CLI installed (`npm install -g vercel`)

### Backend Deployment

1. **Login to Vercel CLI**

   ```bash
   vercel login
   ```

2. **Deploy the backend**

   ```bash
   cd cloud_backend
   vercel
   ```

   Follow the prompts to complete the deployment. Key settings:
   - Set the framework preset to "Other"
   - Set the output directory to "."
   - Set the build command to `pip install -r requirements.txt`
   - Set the development command to `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Note the deployment URL**

   After deployment, Vercel will provide a URL like `https://ultraai-backend.vercel.app`. Save this URL for the frontend configuration.

### Frontend Deployment

1. **Update the API URL in the frontend code**

   Edit `cloud_frontend/index.html` and update the `PROD_API_URL` variable with your backend URL:

   ```javascript
   const PROD_API_URL = 'https://your-backend-url.vercel.app';
   ```

2. **Deploy the frontend**

   ```bash
   cd cloud_frontend
   vercel
   ```

   Follow the prompts to complete the deployment.

3. **Testing the deployment**

   Visit your frontend URL to ensure everything is working correctly.

## Configuration

### CORS Settings

If you encounter CORS issues, update the backend CORS configuration in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

For production, you might want to set environment variables in Vercel:

1. Go to your Vercel project dashboard
2. Click on "Settings" > "Environment Variables"
3. Add variables like API keys or other configuration

## Troubleshooting

### Backend Connection Issues

- Check the browser console for errors
- Verify the API URL is correctly set in the frontend
- Test the backend API directly: `curl https://your-backend-url.vercel.app/api/health`

### Deployment Failures

- Check the Vercel deployment logs
- Ensure requirements.txt has all dependencies
- Verify Python version compatibility (Vercel supports Python 3.9)

## Updating the Deployment

To update your deployment after making changes:

1. Make your code changes
2. Re-deploy using the same commands:

   ```bash
   vercel
   ```

## Advanced: Custom Domain

To use a custom domain:

1. Go to your Vercel project
2. Click "Settings" > "Domains"
3. Add your domain and follow the verification steps
