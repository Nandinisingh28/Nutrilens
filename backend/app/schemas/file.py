"""
NutriLens Backend - File Schemas

Pydantic models for file operations.
"""

from datetime import datetime
from pydantic import BaseModel

from app.db.models.file_asset import FileKind


class FileAssetResponse(BaseModel):
    """Schema for file asset response."""
    id: int
    kind: FileKind
    mime_type: str
    size_bytes: int
    original_filename: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: int
    kind: FileKind
    url: str
    mime_type: str
    size_bytes: int
