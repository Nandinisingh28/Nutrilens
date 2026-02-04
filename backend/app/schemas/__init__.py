"""Schemas package exports."""

from app.schemas.common import (
    APIResponse,
    ErrorDetail,
    PaginationMeta,
    PaginatedResponse,
    success_response,
    error_response,
)
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordChangeRequest,
)
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserPublic,
)
from app.schemas.scan import (
    ScanCreate,
    ScanResponse,
    ScanSummary,
    ScanUpdate,
)
from app.schemas.category import CategoryResponse
from app.schemas.file import FileAssetResponse, FileUploadResponse

__all__ = [
    # Common
    "APIResponse",
    "ErrorDetail",
    "PaginationMeta",
    "PaginatedResponse",
    "success_response",
    "error_response",
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "RefreshTokenRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "PasswordChangeRequest",
    # User
    "UserResponse",
    "UserUpdate",
    "UserPublic",
    # Scan
    "ScanCreate",
    "ScanResponse",
    "ScanSummary",
    "ScanUpdate",
    # Category
    "CategoryResponse",
    # File
    "FileAssetResponse",
    "FileUploadResponse",
]
