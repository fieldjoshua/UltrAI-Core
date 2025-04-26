"""Main FastAPI application module."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.exceptions import UltraAIException, ErrorResponse
from app.core.logging import setup_logging, log_error
from pathlib import Path


# Initialize logging
setup_logging(
    log_path=Path("logs"),
    level=settings.LOG_LEVEL,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
)

app = FastAPI(title="Ultra API", description="Ultra AI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Exception handler for custom exceptions
@app.exception_handler(UltraAIException)
async def ultra_ai_exception_handler(
    request: Request, exc: UltraAIException
) -> JSONResponse:
    """Handle UltraAI exceptions and return standardized error responses."""
    error_response = exc.to_response()
    log_error(
        exc,
        context={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


# Exception handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle validation errors and return standardized error responses."""
    from app.core.exceptions import ValidationError

    error = ValidationError(message="Validation error", details={"errors": str(exc)})
    return await ultra_ai_exception_handler(request, error)


# Exception handler for all other exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions and return standardized error responses."""
    from app.core.exceptions import InternalServerError

    error = InternalServerError(
        message="An unexpected error occurred", details={"error": str(exc)}
    )
    return await ultra_ai_exception_handler(request, error)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Ultra API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8085)
