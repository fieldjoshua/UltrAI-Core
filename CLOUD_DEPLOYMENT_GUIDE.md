# Ultra Framework Cloud Deployment Guide

This guide provides comprehensive information about the Ultra Framework's cloud deployment, testing, error handling, and monitoring systems.

## Table of Contents

1. [Cloud Deployment](#cloud-deployment)
2. [Testing Infrastructure](#testing-infrastructure)
3. [Error Handling](#error-handling)
4. [Monitoring and Observability](#monitoring-and-observability)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Environment Configuration](#environment-configuration)

## Cloud Deployment

The Ultra Framework is deployed to the cloud using Vercel for the frontend and Render for the backend. This setup provides scalability, reliability, and ease of deployment.

### Frontend (Vercel)

- **Deployment URL**: [https://your-app-name.vercel.app](https://your-app-name.vercel.app)
- **Configuration**: Managed via `vercel.json` in the project root
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Backend (Render)

- **Deployment URL**: [https://your-backend-name.onrender.com](https://your-backend-name.onrender.com)
- **Service Type**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --worker-class uvicorn.workers.UvicornWorker backend.main:app`

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
  3. Deploy Backend: Deploy to Render
  4. Notify: Send notification on success/failure

## Environment Configuration

Environment configuration is managed through environment variables for security and flexibility across different environments.

### Local Development

- **Frontend**: `.env.local` file
- **Backend**: `.env` file or environment variables

### Production Environment

- **Frontend**: Environment variables in Vercel
- **Backend**: Environment variables in Render

### Required Environment Variables

| Variable                 | Description                                 | Required In        |
|--------------------------|---------------------------------------------|-------------------|
| `REACT_APP_SENTRY_DSN`   | Sentry DSN for frontend                     | Frontend         |
| `SENTRY_DSN`             | Sentry DSN for backend                      | Backend          |
| `SENTRY_ENVIRONMENT`     | Environment name for Sentry                 | Both             |
| `SENTRY_TRACES_SAMPLE_RATE` | Sample rate for performance monitoring   | Both             |
| `VITE_API_URL`           | URL of the backend API                      | Frontend         |
| `API_KEY`                | API key for authentication                  | Backend          |

## Troubleshooting

If you encounter issues with the cloud deployment, check the following:

1. **Error Logs**: Check Sentry for detailed error logs
2. **Environment Variables**: Ensure all required environment variables are set
3. **Build Logs**: Check build logs in GitHub Actions, Vercel, and Render
4. **API Endpoints**: Test API endpoints directly to isolate issues
5. **Network Issues**: Check for CORS or network connectivity issues 