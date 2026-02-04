"""
NutriLens Backend - Users Routes

User profile management endpoints.
"""

from typing import Annotated
import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.db.models import User, FileAsset, FileKind
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AppException
from app.schemas import (
    UserResponse,
    UserUpdate,
    FileUploadResponse,
    success_response,
)
from app.schemas.auth import PasswordChangeRequest
from app.core.security import verify_password, get_password_hash

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current user's profile."""
    # Build avatar URL if exists
    avatar_url = None
    if current_user.avatar_file_id:
        avatar_url = f"/api/files/{current_user.avatar_file_id}"
    
    user_data = UserResponse.model_validate(current_user).model_dump()
    user_data["avatar_url"] = avatar_url
    
    return success_response(data=user_data)


@router.put("/me")
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user's profile."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"User profile updated: {current_user.email}")
    
    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Profile updated",
    )


@router.post("/me/avatar")
async def upload_avatar(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Upload user avatar."""
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise AppException(
            message=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
            code="INVALID_FILE_TYPE",
            status_code=400,
        )
    
    # Validate file size
    content = await file.read()
    size_bytes = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    if size_bytes > max_bytes:
        raise AppException(
            message=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
            code="FILE_TOO_LARGE",
            status_code=400,
        )
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # Ensure upload directory exists
    avatar_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    
    storage_path = os.path.join(avatar_dir, filename)
    
    # Save file
    with open(storage_path, "wb") as f:
        f.write(content)
    
    # Delete old avatar if exists
    if current_user.avatar_file_id:
        old_avatar = await db.get(FileAsset, current_user.avatar_file_id)
        if old_avatar:
            # Delete file from disk
            if os.path.exists(old_avatar.storage_path):
                os.remove(old_avatar.storage_path)
            await db.delete(old_avatar)
    
    # Create file asset record
    file_asset = FileAsset(
        owner_user_id=current_user.id,
        kind=FileKind.AVATAR,
        storage_path=storage_path,
        mime_type=file.content_type or "image/jpeg",
        size_bytes=size_bytes,
        original_filename=file.filename,
    )
    db.add(file_asset)
    await db.flush()
    
    # Update user avatar reference
    current_user.avatar_file_id = file_asset.id
    await db.commit()
    await db.refresh(file_asset)
    
    logger.info(f"Avatar uploaded for user: {current_user.email}")
    
    return success_response(
        data=FileUploadResponse(
            id=file_asset.id,
            kind=file_asset.kind,
            url=f"/api/files/{file_asset.id}",
            mime_type=file_asset.mime_type,
            size_bytes=file_asset.size_bytes,
        ).model_dump(),
        message="Avatar uploaded",
    )


@router.put("/me/password")
async def change_password(
    request_body: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change current user's password."""
    # Verify current password
    if not verify_password(request_body.current_password, current_user.hashed_password):
        raise AppException(
            message="Current password is incorrect",
            code="INVALID_PASSWORD",
            status_code=400,
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request_body.new_password)
    await db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return success_response(message="Password changed successfully")
