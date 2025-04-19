# UltraAI Cloud Deployment

This document provides instructions for deploying the UltraAI system to cloud services. We'll use Vercel for both the backend and frontend components.

## Backend Deployment

The backend is a FastAPI application that provides API endpoints for the frontend to interact with.

### Files

- `cloud_backend/main.py`: The main FastAPI application
- `cloud_backend/requirements.txt`: Python dependencies
- `cloud_backend/vercel.json`: Vercel configuration

### Deployment Steps

1. Create a Vercel account if you don't have one already (<https://vercel.com>)

2. Install the Vercel CLI:

   ```
   npm install -g vercel
   ```

3. Navigate to the `cloud_backend` directory:

   ```
   cd cloud_backend
   ```

4. Deploy to Vercel:

   ```
   vercel
   ```

5. Follow the prompts to complete the deployment. When asked about the project settings:
   - Set the output directory to `.`
   - Set the build command to `pip install -r requirements.txt`

6. After deployment, Vercel will provide a URL for your backend API (e.g., `https://ultra-cloud-backend.vercel.app`)

## Frontend Deployment

The frontend is a simple HTML/JavaScript application that connects to the backend API.

### Files

- `cloud_frontend/index.html`: The main HTML file with embedded JavaScript
- `cloud_frontend/vercel.json`: Vercel configuration

### Deployment Steps

1. Before deploying, update the API URL in the frontend code:
   - Open `cloud_frontend/index.html`
   - Find the line: `const API_URL = 'https://ultra-cloud-backend.vercel.app';`
   - Replace it with your actual backend URL

2. Navigate to the `cloud_frontend` directory:

   ```
   cd cloud_frontend
   ```

3. Deploy to Vercel:

   ```
   vercel
   ```

4. Follow the prompts to complete the deployment.

5. After deployment, Vercel will provide a URL for your frontend (e.g., `https://ultra-cloud-frontend.vercel.app`)

## Testing the Deployment

1. Open the frontend URL in your browser
2. The application should connect to the backend automatically
3. Try submitting a prompt with different models and options
4. Check for any error messages in the browser console

## Troubleshooting

### CORS Issues

If you see CORS-related errors in the browser console:

1. Make sure the backend CORS settings allow requests from your frontend domain:

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Redeploy the backend with the updated CORS settings

### API Connection Issues

If the frontend can't connect to the backend:

1. Check that you've updated the API_URL in the frontend code
2. Verify that both the frontend and backend are deployed correctly
3. Test the backend API directly using a tool like curl or Postman:

   ```
   curl https://your-backend-domain.vercel.app/api/health
   ```

## Updating the Deployment

To update the deployment after making changes:

1. Make your changes to the code
2. Deploy again using the same commands:

   ```
   vercel
   ```

3. Vercel will create a new deployment and update your project

## Environment Variables

If you need to add API keys or other secrets:

1. Add them as environment variables in the Vercel dashboard
2. Access them in your code using `os.environ.get("VARIABLE_NAME")`
