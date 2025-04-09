# Ultra AI Cloud Deployment Guide

This guide explains how to deploy the Ultra AI application to the cloud using Vercel. By moving to cloud deployment, we eliminate port issues and provide a more reliable and accessible service.

## Prerequisites

- Node.js and npm installed
- [Vercel CLI](https://vercel.com/docs/cli) (`npm install -g vercel`)
- A [Vercel account](https://vercel.com/signup) (free tier available)
- Git

## Frontend Deployment

The frontend application is a React app that communicates with the backend API.

### Configuration

1. The frontend is configured to use the cloud backend API by default:
   ```javascript
   const API_URL = import.meta.env.VITE_API_URL || 'https://ultra-api.vercel.app';
   ```

2. The `vercel.json` file contains necessary configuration for deployment:
   - Routing rules to handle client-side navigation
   - CORS headers for API communication
   - Environment variables

### Deployment Steps

You can use the provided deployment script:

```bash
# Make the script executable
chmod +x deploy-to-cloud.sh

# Run the deployment script
./deploy-to-cloud.sh
```

Alternatively, follow these manual steps:

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy to Vercel:
   ```bash
   vercel --prod
   ```

3. The first time you deploy, you'll be prompted to:
   - Login to your Vercel account
   - Link to an existing project or create a new one
   - Set the project directory (usually the current directory)

4. After deployment, Vercel will provide a URL for your application.

## Backend Deployment

The backend is a FastAPI Python application that serves the AI analysis endpoints.

### Configuration

1. The `backend/vercel.json` file contains:
   - Build configuration for the Python app
   - Routing rules
   - CORS headers
   - Environment variables

2. The backend is configured to use cloud-friendly storage paths:
   ```python
   DOCUMENT_STORAGE_PATH = os.getenv("DOCUMENT_STORAGE_PATH", "document_storage")
   ```

### Backend Deployment Steps

You can use the provided backend deployment script:

```bash
# Navigate to the backend directory
cd backend

# Make the script executable
chmod +x deploy-backend.sh

# Run the deployment script
./deploy-backend.sh
```

Alternatively, follow these manual steps:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Ensure you have a `requirements.txt` file:
   ```bash
   pip freeze > requirements.txt
   ```

3. Deploy to Vercel:
   ```bash
   vercel --prod
   ```

4. The backend API will be available at the URL provided by Vercel.

## Connecting Frontend to Backend

After deploying both applications, you need to make sure the frontend knows the backend URL:

1. Go to your Vercel dashboard
2. Select your frontend project
3. Go to "Settings" → "Environment Variables"
4. Add a variable named `VITE_API_URL` with the value of your backend URL
5. Redeploy the frontend to apply the changes:
   ```bash
   vercel --prod
   ```

## Important Notes

### Stateless Functions

Vercel Functions (which power your backend) are stateless, meaning:

- Local file storage is temporary and not persisted between function invocations
- For production use with documents, consider integrating with cloud storage services like AWS S3, Google Cloud Storage, or similar

### Limits

Be aware of Vercel's free tier limitations:

- Function execution time: 10 seconds (Pro plan: 60 seconds)
- Payload size: 4.5MB (Pro plan: 50MB)
- Deployments per day: 100
- Bandwidth: Limited

For high-traffic or resource-intensive applications, consider upgrading to a paid plan.

## Troubleshooting

### CORS Issues

If you experience CORS issues, verify:

1. The `vercel.json` files have the correct CORS headers
2. Your frontend is making requests to the correct backend URL
3. Your backend is properly handling preflight OPTIONS requests

### Deployment Failures

If deployment fails:

1. Check that all required files are present
2. Verify the logs provided by Vercel
3. Test locally before deploying
4. Check for unsupported dependencies

### Function Timeout

If your API calls time out:

1. Optimize your code to reduce execution time
2. Consider breaking complex operations into smaller functions
3. Use background tasks for lengthy operations
4. Upgrade to a paid plan for longer execution times

## Conclusion

By deploying to Vercel, you've eliminated port issues and created a globally accessible application. Your Ultra AI system can now be accessed from anywhere, and you have a solid foundation for scaling and enhancing the application.