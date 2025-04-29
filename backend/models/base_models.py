"""
Base models for the Ultra backend.

This module provides base Pydantic models with enhanced validation capabilities
for all API models.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, TypeVar

from pydantic import (
    BaseModel,
    Field,
    root_validator,
    validator,
    constr,
    conint,
    confloat,
)

# Type variable for model classes
ModelT = TypeVar("ModelT", bound=BaseModel)


class APIBaseModel(BaseModel):
    """Base model for all API models with enhanced validation"""

    class Config:
        """Configuration for all API models"""

        # Validate assignment to model fields
        validate_assignment = True
        # Forbid extra attributes that are not model fields
        extra = "forbid"
        # Keep field order as defined in model
        orm_mode = True
        # Allow population by field name
        allow_population_by_field_name = True


class ResponseStatus(str, Enum):
    """API response status enum"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorDetail(APIBaseModel):
    """Error detail model"""

    type: str = Field(..., description="Error type identifier")
    msg: str = Field(..., description="Human-readable error message")
    loc: List[Any] = Field(
        default_factory=list, description="Location of the error (e.g., field path)"
    )
    ctx: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )

    @validator("loc")
    def format_location(cls, v):
        """Format location as list of strings"""
        return [str(item) for item in v]


class ErrorResponse(APIBaseModel):
    """Standard error response model"""

    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = Field(
        default=None, description="Detailed error information"
    )
    request_id: Optional[str] = Field(
        default=None, description="Request ID for tracking"
    )


class SuccessResponse(APIBaseModel):
    """Standard success response model"""

    status: ResponseStatus = Field(
        ResponseStatus.SUCCESS, description="Response status"
    )
    message: Optional[str] = Field(
        default=None, description="Human-readable success message"
    )
    data: Any = Field(..., description="Response data")
    request_id: Optional[str] = Field(
        default=None, description="Request ID for tracking"
    )


class PaginationParams(APIBaseModel):
    """Pagination parameters model"""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset based on page number and page size"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit (page size)"""
        return self.page_size


class PaginatedResponse(SuccessResponse):
    """Paginated response model"""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")

    @root_validator
    def calculate_pagination_info(cls, values):
        """Calculate pagination information"""
        page = values.get("page", 1)
        page_size = values.get("page_size", 20)
        total_items = values.get("total_items", 0)

        if page_size <= 0:
            page_size = 20
            values["page_size"] = page_size

        total_pages = (
            (total_items + page_size - 1) // page_size if total_items > 0 else 0
        )
        values["total_pages"] = total_pages
        values["has_previous"] = page > 1
        values["has_next"] = page < total_pages

        return values


class ValidationResult(APIBaseModel):
    """Result of a validation operation"""

    valid: bool = Field(..., description="Whether the validation passed")
    errors: Optional[List[ErrorDetail]] = Field(
        default=None, description="Validation errors if any"
    )

    @validator("errors", always=True)
    def check_errors(cls, errors, values):
        """Ensure errors field is consistent with valid flag"""
        valid = values.get("valid", False)
        if valid and errors:
            raise ValueError("Cannot have errors when valid=True")
        if not valid and not errors:
            raise ValueError("Must have errors when valid=False")
        return errors


# Commonly used field types
EmailStr = constr(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PasswordStr = constr(min_length=8)
UsernameStr = constr(pattern=r"^[a-zA-Z0-9_-]{3,16}$", strip_whitespace=True)
NonEmptyStr = constr(min_length=1, strip_whitespace=True)
IdStr = constr(pattern=r"^[a-zA-Z0-9_-]+$")
UrlStr = constr(pattern=r"^https?://", strip_whitespace=True)

# Integer constraints
PositiveInt = conint(gt=0)
NonNegativeInt = conint(ge=0)
PercentageInt = conint(ge=0, le=100)

# Float constraints
PositiveFloat = confloat(gt=0.0)
NonNegativeFloat = confloat(ge=0.0)
PercentageFloat = confloat(ge=0.0, le=100.0)


# Common field definitions
def required_str(description: str, **kwargs) -> Any:
    """Field definition for a required string"""
    return Field(..., description=description, **kwargs)


def optional_str(description: str, **kwargs) -> Any:
    """Field definition for an optional string"""
    return Field(None, description=description, **kwargs)


def required_int(description: str, **kwargs) -> Any:
    """Field definition for a required integer"""
    return Field(..., description=description, **kwargs)


def optional_int(description: str, **kwargs) -> Any:
    """Field definition for an optional integer"""
    return Field(None, description=description, **kwargs)


def required_float(description: str, **kwargs) -> Any:
    """Field definition for a required float"""
    return Field(..., description=description, **kwargs)


def optional_float(description: str, **kwargs) -> Any:
    """Field definition for an optional float"""
    return Field(None, description=description, **kwargs)


def required_bool(description: str, **kwargs) -> Any:
    """Field definition for a required boolean"""
    return Field(..., description=description, **kwargs)


def optional_bool(description: str, **kwargs) -> Any:
    """Field definition for an optional boolean"""
    return Field(None, description=description, **kwargs)


def required_list(description: str, **kwargs) -> Any:
    """Field definition for a required list"""
    return Field(default_factory=list, description=description, **kwargs)


def optional_list(description: str, **kwargs) -> Any:
    """Field definition for an optional list"""
    return Field(None, description=description, **kwargs)


def required_dict(description: str, **kwargs) -> Any:
    """Field definition for a required dictionary"""
    return Field(default_factory=dict, description=description, **kwargs)


def optional_dict(description: str, **kwargs) -> Any:
    """Field definition for an optional dictionary"""
    return Field(None, description=description, **kwargs)


def required_email(description: str, **kwargs) -> Any:
    """Field definition for a required email"""
    return Field(..., description=description, **kwargs)


def optional_email(description: str, **kwargs) -> Any:
    """Field definition for an optional email"""
    return Field(None, description=description, **kwargs)
