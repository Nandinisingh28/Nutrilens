"""
NutriLens Backend - Files Routes

File serving endpoints.
"""

from typing import Annotated
import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import User, FileAsset
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get file by ID.
    
    - Owner-only access
    - Returns the actual file content
    """
    file_asset = await db.get(FileAsset, file_id)
    
    if not file_asset:
        raise NotFoundError("File", file_id)
    
    # Check ownership
    if file_asset.owner_user_id != current_user.id:
        raise ForbiddenError("You do not have access to this file")
    
    # Check file exists on disk
    if not os.path.exists(file_asset.storage_path):
        logger.error(f"File not found on disk: {file_asset.storage_path}")
        raise NotFoundError("File", file_id)
    
    return FileResponse(
        path=file_asset.storage_path,
        media_type=file_asset.mime_type,
        filename=file_asset.original_filename,
    )
