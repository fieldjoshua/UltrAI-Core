# Backend Modularization Documentation

## Overview

This document provides an overview of the refactored backend architecture, which has been modularized to improve maintainability, scalability, and code organization. The monolithic design has been transformed into a well-structured, component-based system with clear separation of concerns.

## Architecture Components

The backend has been reorganized into the following components:

### 1. Models

Located in `backend/models/`, this directory contains Pydantic models for data validation and serialization:

- `document.py` - Models for document handling
- `pricing.py` - Models for pricing and token estimation
- `user.py` - Models for user management and authentication

### 2. Routes

Located in `backend/routes/`, this directory contains FastAPI routers organized by functionality:

- `analyze_routes.py` - Endpoints for text analysis
- `document_routes.py` - Endpoints for document management
- `health.py` - Health check endpoints
- `metrics.py` - Metrics and monitoring endpoints
- `pricing_routes.py` - Endpoints for pricing operations
- `user_routes.py` - Endpoints for user management and authentication

### 3. Services

Located in `backend/services/`, this directory contains business logic and service implementations:

- `auth_service.py` - User authentication and management
- `document_processor.py` - Document handling and processing
- `mock_llm_service.py` - Mock implementation for testing
- `pricing_calculator.py` - Calculation of usage costs
- `pricing_integration.py` - Integration with pricing systems
- `pricing_simulator.py` - Simulation of pricing scenarios
- `pricing_updater.py` - Updating pricing configurations

### 4. Utils

Located in `backend/utils/`, this directory contains utility functions and helpers:

- `cache.py` - Caching utilities
- `metrics.py` - Metrics collection and reporting
- `server.py` - Server configuration utilities

## Authentication System

The new authentication system provides:

- JWT-based authentication
- Secure password hashing with bcrypt
- User registration and login
- Profile management
- Token validation and renewal

### Authentication Flow

1. **Registration**: Users register via `/api/register` with email, password, and profile information
2. **Login**: Users authenticate via `/api/login` and receive a JWT token
3. **Authorization**: Protected endpoints require a valid token in the Authorization header
4. **Profile Management**: Authenticated users can view and update their profiles

### User Data Model

The user data model includes:

- `user_id` - Unique identifier
- `email` - Email address (unique)
- `name` - User's display name
- `password_hash` - Securely hashed password
- `tier` - Pricing tier (basic, premium, etc.)
- `created_at` - Account creation timestamp
- `last_login` - Last login timestamp
- `balance` - Account balance for paid services
- `settings` - User preferences and settings

## Pricing System

The pricing system provides:

- Token usage estimation
- Cost calculation based on model and tier
- User account balance management
- Usage tracking and reporting

### Pricing Flow

1. **Estimation**: Before processing, estimate token usage and costs
2. **Authorization**: Check if user has sufficient balance for the operation
3. **Processing**: Execute the requested operation
4. **Tracking**: Record actual token usage and costs
5. **Reporting**: Provide usage summaries and balance information

## API Endpoints

### User Management

- `POST /api/register` - Register a new user
- `POST /api/login` - Authenticate and receive a token
- `GET /api/user/me` - Get current user profile
- `PUT /api/user/me` - Update current user profile
- `GET /api/user/{user_id}` - Get user profile by ID

### Pricing and Billing

- `POST /api/estimate-tokens` - Estimate token usage and cost
- `POST /api/admin/pricing/toggle` - Toggle pricing functionality
- `POST /api/user/create` - Create a user account
- `POST /api/user/add-funds` - Add funds to user account
- `GET /api/user/{user_id}/balance` - Check user balance
- `GET /api/user/{user_id}/usage` - Get usage summary
- `GET /api/session/{session_id}` - Get session details

### Analysis

- `POST /api/analyze` - Analyze text with multiple models
- `POST /api/analyze-with-docs` - Analyze text with document context

### Documents

- `POST /api/upload-document` - Upload a document
- `GET /api/documents/{document_id}` - Get document details
- `GET /api/documents` - List all documents
- `POST /api/create-document-session` - Create document upload session
- `POST /api/upload-document-chunk` - Upload document chunk
- `POST /api/finalize-document-upload` - Finalize chunked upload
- `POST /api/process-documents-with-pricing` - Process documents with pricing

### Monitoring

- `GET /api/health` - Health check
- `GET /api/metrics` - Get performance metrics
- `GET /api/status` - Get system status

## Testing

Tests for the new modular structure are located in the `tests/` directory:

- `test_backend_api.py` - Integration tests for API endpoints
- `test_document_upload.py` - Tests for document upload functionality
- `test_cache.py` - Tests for caching functionality

## Dependencies and Requirements

The refactored backend relies on the following key dependencies:

- FastAPI - Web framework
- Pydantic - Data validation and settings management
- PyJWT - JWT token handling
- Passlib - Password hashing and verification
- Pytest - Testing framework

## Running the Application

To run the application with the new structure:

```bash
# Start the server
python -m backend.app
```

Server options:

- `--host` - Host to bind to (default: 127.0.0.1)
- `--port` - Port to bind to (default: 8085)
- `--reload` - Enable auto-reload for development
- `--find-port` - Find available port if specified port is in use
- `--mock` - Run in mock mode with simulated responses
