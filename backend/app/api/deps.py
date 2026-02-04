"""
NutriLens Backend - API Dependencies

Shared dependencies for API endpoints.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.db.models import User
from app.core.security import verify_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedError

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Supports both:
    - Authorization header: Bearer <token>
    - Cookie: access_token (if USE_COOKIE_AUTH is enabled)
    """
    token = None
    
    # Try header first
    if credentials:
        token = credentials.credentials
    
    # Try cookie if header not present and cookie auth is enabled
    if not token and settings.USE_COOKIE_AUTH:
        token = request.cookies.get("access_token")
    
    if not token:
        raise UnauthorizedError("Not authenticated")
    
    # Verify token
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        raise UnauthorizedError("Invalid or expired token")
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise UnauthorizedError("User not found")
    
    if not user.is_active:
        raise UnauthorizedError("User account is disabled")
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise UnauthorizedError("Inactive user")
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise UnauthorizedError("Email not verified")
    return current_user
