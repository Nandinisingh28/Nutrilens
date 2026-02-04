"""
NutriLens Backend - Health Check Route

Simple health check endpoint.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return success_response(
        data={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
    )
