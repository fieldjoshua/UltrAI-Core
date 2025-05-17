# External Dependencies in Route Files

## Core MVP Route Files Dependencies

### 1. FastAPI Framework Dependencies

- **fastapi**: Core web framework
  - APIRouter
  - HTTPException
  - Depends
  - Header
  - status
  - Body
  - Query
  - File
  - Form
  - UploadFile
  - Request
  - BackgroundTasks
- **fastapi.responses**: JSONResponse
- **fastapi.security**: OAuth2PasswordBearer
- **pydantic**: BaseModel, Field (for request/response models)

### 2. Database Dependencies

- **sqlalchemy.orm**: Session

### 3. Authentication Dependencies

- **jwt** (PyJWT): JWT token handling

### 4. Server-Sent Events

- **sse_starlette**: EventSourceResponse

### 5. Type Hints (Standard Library)

- **typing**: Optional, List, Dict, Any

## Dependency Summary for MVP

The following external packages are used across all route files:

1. **fastapi** - Core web framework
2. **pydantic** - Data validation
3. **sqlalchemy** - Database ORM
4. **jwt** - JSON Web Token handling
5. **sse-starlette** - Server-sent events support

These are the primary external dependencies that need to be included in the core requirements.txt for the MVP deployment.

## Additional Route Files (Non-Core)

- available_models_routes.py: Uses same as llm_routes.py (fastapi, pydantic)
- health_routes.py: Uses only fastapi
- Other routes: Use similar patterns with fastapi as the main dependency
