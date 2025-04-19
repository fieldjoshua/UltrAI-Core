# Ultra AI Comprehensive Cloud Deployment Guide

This guide provides complete information about deploying the Ultra AI system to cloud services, along with testing, error handling, and monitoring capabilities.

## Table of Contents

1. [Overview and Benefits](#overview-and-benefits)
2. [Prerequisites](#prerequisites)
3. [Frontend Deployment](#frontend-deployment)
4. [Backend Deployment](#backend-deployment)
5. [Connecting Frontend to Backend](#connecting-frontend-to-backend)
6. [Testing Infrastructure](#testing-infrastructure)
7. [Error Handling](#error-handling)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Environment Configuration](#environment-configuration)
11. [Troubleshooting](#troubleshooting)
12. [Performance Considerations](#performance-considerations)

## Overview and Benefits

By deploying Ultra AI to the cloud:
- Port configuration issues are eliminated
- The application becomes globally accessible
- We gain better scalability and reliability
- Deployment and updates become streamlined
- We can leverage cloud-specific features

## Prerequisites

- Node.js and npm installed
- [Vercel CLI](https://vercel.com/docs/cli) (`npm install -g vercel`)
- A [Vercel account](https://vercel.com/signup) (free tier available)
- Git repository setup
- Python 3.9+ (for backend development and testing)

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

## Testing Infrastructure

We have implemented a comprehensive testing infrastructure to ensure code quality and reliability, especially after the cloud migration.

### Backend Tests

- **Framework**: pytest
- **Test Types**:
  - API Integration Tests: Test actual API endpoints
  - Unit Tests: Test specific functions and classes
  - Performance Tests: Test API performance under load
- **Running Tests**: `pytest backend/tests -v`

### Frontend Tests

- **Framework**: Jest with React Testing Library
- **Test Types**:
  - Component Tests: Test individual React components
  - Integration Tests: Test component interactions
  - Mocked API Tests: Test components with mocked API responses
- **Running Tests**: `npm test`

### End-to-End Testing

- **Pre-deployment Testing**: Run `./run_tests.sh` to perform all tests before deployment
- **Environment-specific Testing**: Tests have support for different environments (local, staging, production)

## Error Handling

We've implemented a standardized error handling system across the application to ensure consistent responses and robust error reporting.

### Backend Error Handling

- **Custom Exception Classes**: Defined in `backend/error_handler.py`
- **Standardized Response Format**:
  ```json
  {
    "status": "error",
    "message": "Detailed error message",
    "code": "error_code",
    "details": [...],
    "request_id": "unique-request-id"
  }
  ```
- **Integration with Sentry**: All server errors (5xx) are automatically reported to Sentry

### Frontend Error Handling

- **React Error Boundaries**: Global error boundary in `App.tsx`
- **API Error Handling**: Consistent error handling in API calls with user-friendly messages
- **Integration with Sentry**: Unhandled exceptions are captured and reported to Sentry

## Monitoring and Observability

We've set up comprehensive monitoring and observability tools to ensure the health and performance of the application in the cloud environment.

### Sentry Integration

- **Error Tracking**: Automatic capturing and reporting of errors
- **Performance Monitoring**: Tracking performance metrics with distributed tracing
- **Environment Separation**: Different environments (development, staging, production) are separate in Sentry

### Performance Monitoring

- **Dashboard**: Real-time metrics dashboard available at `/api/metrics`
- **Performance Tests**: Run performance tests with `python backend/performance_test.py`
- **Continuous Monitoring**: Performance metrics are tracked over time and alert on degradation

## CI/CD Pipeline

We've set up a GitHub Actions CI/CD pipeline for automated testing and deployment.

### CI Pipeline

- **Trigger**: Pull requests and pushes to main branch
- **Steps**:
  1. Lint: ESLint and Prettier
  2. Test Frontend: Jest tests
  3. Test Backend: pytest tests
  4. Build: Build the application

### CD Pipeline

- **Trigger**: Successful CI on main branch
- **Steps**:
  1. Create Sentry Release: Track code changes in Sentry
  2. Deploy Frontend: Deploy to Vercel
  3. Deploy Backend: Deploy to Vercel
  4. Notify: Send notification on success/failure

## Environment Configuration

Environment configuration is managed through environment variables for security and flexibility across different environments.

### Local Development

- **Frontend**: `.env.local` file
- **Backend**: `.env` file or environment variables

### Production Environment

- **Frontend**: Environment variables in Vercel
- **Backend**: Environment variables in Vercel

### Required Environment Variables

| Variable                 | Description                                 | Required In        |
|--------------------------|---------------------------------------------|-------------------|
| `REACT_APP_SENTRY_DSN`   | Sentry DSN for frontend                     | Frontend         |
| `SENTRY_DSN`             | Sentry DSN for backend                      | Backend          |
| `SENTRY_ENVIRONMENT`     | Environment name for Sentry                 | Both             |
| `SENTRY_TRACES_SAMPLE_RATE` | Sample rate for performance monitoring   | Both             |
| `VITE_API_URL`           | URL of the backend API                      | Frontend         |
| `API_KEY`                | API key for authentication                  | Backend          |
| `DOCUMENT_STORAGE_PATH`  | Path for document storage                   | Backend          |

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

### Common Issues

1. **Error Logs**: Check Sentry for detailed error logs
2. **Environment Variables**: Ensure all required environment variables are set
3. **Build Logs**: Check build logs in GitHub Actions and Vercel
4. **API Endpoints**: Test API endpoints directly to isolate issues
5. **Network Issues**: Check for CORS or network connectivity issues

## Performance Considerations

### Stateless Functions

Vercel Functions (which power your backend) are stateless, meaning:

- Local file storage is temporary and not persisted between function invocations
- For production use with documents, consider integrating with cloud storage services like AWS S3, Google Cloud Storage, or similar

### Cloud Limitations

Be aware of Vercel's free tier limitations:

- Function execution time: 10 seconds (Pro plan: 60 seconds)
- Payload size: 4.5MB (Pro plan: 50MB)
- Deployments per day: 100
- Bandwidth: Limited

For high-traffic or resource-intensive applications, consider upgrading to a paid plan.

### Document Handling

For document processing features:
- Consider using cloud storage services for document persistence
- Implement chunking for large document uploads
- Use background processing for document analysis tasks
- Consider caching analyzed document results

## Conclusion

By deploying to the cloud, you've eliminated port issues and created a globally accessible application. Your Ultra AI system can now be accessed from anywhere, and you have a solid foundation for scaling and enhancing the application.