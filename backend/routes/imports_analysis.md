# Route Files Import Analysis

## External Dependencies Summary

### 1. auth_routes.py

- **jwt** - JWT token handling
- **fastapi** - Web framework (APIRouter, Depends, Header, HTTPException, status)
- **fastapi.responses** - JSONResponse
- **fastapi.security** - OAuth2PasswordBearer
- **sqlalchemy.orm** - Session

### 2. llm_routes.py

- **fastapi** - Web framework (APIRouter, HTTPException)
- **pydantic** - BaseModel for request/response models
- **typing** - Type hints (List, Optional)

### 3. analyze_routes.py

- **fastapi** - Web framework (APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Request, UploadFile, status)
- **fastapi.responses** - JSONResponse
- **sqlalchemy.orm** - Session
- **sse_starlette.sse** - EventSourceResponse (for server-sent events)

### 4. orchestrator_routes.py

- **fastapi** - Web framework (APIRouter, Body, HTTPException, Query)
- **pydantic** - BaseModel, Field for request/response models
- **typing** - Type hints (Any, Dict, List, Optional)

### 5. document_routes.py

- **fastapi** - Web framework (APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile)
- **fastapi.responses** - JSONResponse
- **typing** - Type hints (Any, Dict, List, Optional)

## Summary of External Dependencies

1. **FastAPI ecosystem**:

   - fastapi (core)
   - fastapi.responses
   - fastapi.security
   - pydantic

2. **Database**:

   - sqlalchemy.orm

3. **Authentication**:

   - jwt (PyJWT)

4. **Server-Sent Events**:

   - sse_starlette

5. **Standard library** (not external):
   - logging
   - typing
   - json
   - time
   - os
   - sys
   - uuid
   - datetime
   - shutil
