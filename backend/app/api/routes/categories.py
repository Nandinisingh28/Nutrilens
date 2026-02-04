"""
NutriLens Backend - Categories Routes

Category listing endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.db.models import Category
from app.schemas import CategoryResponse, success_response
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all categories."""
    result = await db.execute(select(Category).order_by(Category.title))
    categories = result.scalars().all()
    
    return success_response(
        data=[CategoryResponse.model_validate(c).model_dump() for c in categories],
    )
