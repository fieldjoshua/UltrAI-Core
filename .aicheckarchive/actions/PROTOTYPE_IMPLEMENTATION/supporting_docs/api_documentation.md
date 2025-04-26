# UltraAI API Documentation

## Overview

The UltraAI API provides a RESTful interface for interacting with the UltraAI system. This documentation covers all available endpoints, request/response formats, and authentication requirements.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. To access protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

#### Register User

```http
POST /auth/register
```

Request Body:

```json
{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
}
```

Response:

```json
{
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-04-25T12:00:00Z"
}
```

#### Login

```http
POST /auth/login
```

Request Body:

```json
{
    "email": "user@example.com",
    "password": "securepassword"
}
```

Response:

```json
{
    "access_token": "jwt_token",
    "token_type": "bearer"
}
```

#### Get Current User

```http
GET /auth/me
```

Response:

```json
{
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-04-25T12:00:00Z"
}
```

## User Management

### Get User

```http
GET /users/{user_id}
```

Response:

```json
{
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-04-25T12:00:00Z"
}
```

### Update User

```http
PUT /users/{user_id}
```

Request Body:

```json
{
    "email": "newemail@example.com",
    "full_name": "New Name"
}
```

Response:

```json
{
    "id": "user_id",
    "email": "newemail@example.com",
    "full_name": "New Name",
    "created_at": "2025-04-25T12:00:00Z"
}
```

### Delete User

```http
DELETE /users/{user_id}
```

Response:

```json
{
    "message": "User deleted successfully"
}
```

## Error Responses

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
    "detail": "Error message",
    "code": "ERROR_CODE",
    "status_code": 400
}
```

Common error codes:

- `INVALID_CREDENTIALS`: Authentication failed
- `USER_NOT_FOUND`: User does not exist
- `EMAIL_ALREADY_EXISTS`: Email is already registered
- `INVALID_REQUEST`: Request validation failed
- `UNAUTHORIZED`: Missing or invalid authentication token
- `FORBIDDEN`: Insufficient permissions

## Rate Limiting

The API implements rate limiting to prevent abuse. Current limits:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Security

- All endpoints use HTTPS
- Passwords are hashed using bcrypt
- JWT tokens expire after 24 hours
- CORS is configured to allow specific origins
- Input validation is performed on all requests

## Models

### User Model

```python
class User(Base):
    id: str
    email: str
    full_name: str
    hashed_password: str
    created_at: datetime
    is_active: bool
```

### API Response Models

```python
class APIResponse(BaseModel):
    data: Optional[Any]
    message: Optional[str]
    status_code: int = 200

class ErrorResponse(BaseModel):
    detail: str
    code: str
    status_code: int
```

## Development

### Local Development

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Run the development server: `uvicorn main:app --reload`

### Environment Variables

```
DATABASE_URL=sqlite:///./ultra.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Testing

Run tests using pytest:

```bash
pytest
```

## Support

For API support or to report issues, please contact the development team or create an issue in the repository.
