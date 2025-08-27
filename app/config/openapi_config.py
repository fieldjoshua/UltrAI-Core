"""
OpenAPI configuration for UltraAI Core API documentation.
"""

from typing import Dict, Any

def get_openapi_config() -> Dict[str, Any]:
    """Get OpenAPI configuration with enhanced documentation."""
    return {
        "title": "UltraAI Core API",
        "description": """
## Welcome to UltraAI Core API

UltraAI Core provides a powerful multi-model LLM orchestration platform with the patented Ultra Synthesis™ pipeline.

### Key Features:
- 🤖 **Multi-Model Orchestration**: Combine insights from GPT-4, Claude 3.5, Gemini, and more
- 🔄 **Ultra Synthesis™ Pipeline**: Three-stage analysis with peer review and synthesis
- 👤 **User Management**: Secure authentication with JWT tokens
- 💰 **Usage Tracking**: Transparent billing and balance management
- 📄 **Document Analysis**: Upload and analyze documents with multiple models
- 📊 **Real-time Monitoring**: Prometheus metrics and health checks

### Getting Started:
1. Register an account at `/api/auth/register`
2. Login to receive your JWT token at `/api/auth/login`
3. Include the token in the `Authorization: Bearer <token>` header
4. Start making requests to the orchestration endpoints

### API Documentation:
- [Full API Reference](/api/docs)
- [ReDoc Alternative](/api/redoc)
- [OpenAPI Schema](/api/openapi.json)

### Base URLs:
- Production: `https://ultrai-core.onrender.com/api`
- Development: `http://localhost:8000/api`
        """,
        "version": "1.0.0",
        "terms_of_service": "https://ultrai.app/terms",
        "contact": {
            "name": "UltraAI Support",
            "url": "https://ultrai.app/support",
            "email": "support@ultrai.app"
        },
        "license": {
            "name": "Proprietary",
            "url": "https://ultrai.app/license"
        },
        "servers": [
            {
                "url": "https://ultrai-core.onrender.com",
                "description": "Production server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        "tags": [
            {
                "name": "Auth",
                "description": "Authentication and user management endpoints"
            },
            {
                "name": "Orchestrator",
                "description": "Multi-model LLM orchestration endpoints"
            },
            {
                "name": "User",
                "description": "User profile and balance management"
            },
            {
                "name": "Documents",
                "description": "Document upload and analysis"
            },
            {
                "name": "Health",
                "description": "System health and monitoring"
            },
            {
                "name": "Models",
                "description": "Available models and pricing"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT authentication token obtained from /api/auth/login"
                }
            },
            "schemas": {
                # Enhanced schema examples
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["error"]},
                        "message": {"type": "string"},
                        "code": {"type": "string"},
                        "details": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ErrorDetail"}
                        },
                        "request_id": {"type": "string"}
                    },
                    "example": {
                        "status": "error",
                        "message": "Validation error",
                        "code": "VALIDATION_ERROR",
                        "details": [
                            {
                                "type": "missing",
                                "loc": ["body", "query"],
                                "msg": "Field required"
                            }
                        ],
                        "request_id": "550e8400-e29b-41d4"
                    }
                },
                "ErrorDetail": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "loc": {"type": "array", "items": {"type": "string"}},
                        "msg": {"type": "string"}
                    }
                }
            },
            "responses": {
                "UnauthorizedError": {
                    "description": "Authentication credentials are missing or invalid",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "status": "error",
                                "message": "Invalid authentication credentials",
                                "code": "UNAUTHORIZED"
                            }
                        }
                    }
                },
                "ForbiddenError": {
                    "description": "The user does not have necessary permissions",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "status": "error",
                                "message": "Insufficient permissions",
                                "code": "FORBIDDEN"
                            }
                        }
                    }
                },
                "NotFoundError": {
                    "description": "The requested resource was not found",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "status": "error",
                                "message": "Resource not found",
                                "code": "NOT_FOUND"
                            }
                        }
                    }
                },
                "ValidationError": {
                    "description": "Invalid request data",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "RateLimitError": {
                    "description": "Too many requests",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "status": "error",
                                "message": "Rate limit exceeded. Please try again later.",
                                "code": "RATE_LIMITED"
                            }
                        }
                    }
                }
            }
        }
    }


def customize_openapi_schema(app) -> Dict[str, Any]:
    """
    Customize the OpenAPI schema for the FastAPI app.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Customized OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = app.openapi()
    
    # Apply custom configuration
    config = get_openapi_config()
    for key, value in config.items():
        if key in openapi_schema:
            if isinstance(openapi_schema[key], dict) and isinstance(value, dict):
                openapi_schema[key].update(value)
            else:
                openapi_schema[key] = value
        else:
            openapi_schema[key] = value
    
    # Add security requirement to all protected endpoints
    for path_data in openapi_schema.get("paths", {}).values():
        for operation in path_data.values():
            if isinstance(operation, dict):
                # Check if endpoint requires authentication based on tags or summary
                if any(tag in ["User", "Orchestrator", "Documents"] for tag in operation.get("tags", [])):
                    if "security" not in operation:
                        operation["security"] = [{"bearerAuth": []}]
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema