"""
NutriLens Backend - Common Schemas

Shared schemas for API responses.
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str = Field(..., description="Error code")
    details: Optional[Any] = Field(None, description="Additional error details")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[T] = Field(None, description="Response data payload")
    error: Optional[ErrorDetail] = Field(None, description="Error details if any")
    
    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    success: bool = True
    message: str = "Success"
    data: list[T] = Field(default_factory=list)
    meta: PaginationMeta
    error: Optional[ErrorDetail] = None


# Helper functions
def success_response(
    data: Any = None,
    message: str = "Success",
) -> dict:
    """Create a success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
    }


def error_response(
    message: str,
    code: str = "ERROR",
    details: Any = None,
) -> dict:
    """Create an error response."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": details,
        },
    }
