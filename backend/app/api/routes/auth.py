"""
NutriLens Backend - Authentication Routes

Handles user registration, login, logout, and token refresh.
"""

from datetime import timedelta
from typing import Annotated
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.db.models import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import check_login_rate_limit, check_forgot_password_rate_limit
from app.core.exceptions import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ConflictError,
)
from app.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse,
    success_response,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Store for password reset tokens (in-memory for demo, use Redis in production)
_reset_tokens: dict[str, int] = {}  # token -> user_id


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set authentication cookies if cookie mode is enabled."""
    if settings.USE_COOKIE_AUTH:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )


@router.post("/signup")
async def signup(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    """
    Register a new user.
    
    - Validates email uniqueness
    - Validates password policy
    - Hashes password
    - Creates user record
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise ConflictError("Email already registered")
    
    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
        is_active=True,
        is_verified=False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.email}")
    
    # TODO: Send verification email in background
    # background_tasks.add_task(send_verification_email, user.email)
    
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="Registration successful",
    )


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Authenticate user and return tokens.
    
    - Rate limited to 5 attempts per minute
    - Validates credentials
    - Returns access and refresh tokens
    """
    # Check rate limit
    check_login_rate_limit(request)
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    
    if not user.is_active:
        raise AppException(
            message="User account is disabled",
            code="ACCOUNT_DISABLED",
            status_code=403,
        )
    
    # Create tokens
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    logger.info(f"User logged in: {user.email}")
    
    # Set cookies if enabled
    _set_auth_cookies(response, access_token, refresh_token)
    
    return success_response(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ).model_dump(),
        message="Login successful",
    )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing auth cookies.
    
    Note: For JWT, tokens are stateless. This only clears cookies.
    For true token invalidation, implement a token blacklist.
    """
    if settings.USE_COOKIE_AUTH:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
    
    return success_response(message="Logout successful")


@router.post("/refresh")
async def refresh_token(
    request_body: RefreshTokenRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Refresh access token using refresh token.
    """
    user_id = verify_token(request_body.refresh_token, token_type="refresh")
    
    if user_id is None:
        raise UnauthorizedError("Invalid or expired refresh token")
    
    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    
    # Create new tokens
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(subject=user.id)
    
    # Set cookies if enabled
    _set_auth_cookies(response, access_token, new_refresh_token)
    
    return success_response(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ).model_dump(),
        message="Token refreshed",
    )


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    request_body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    """
    Request password reset email.
    
    - Rate limited to 3 attempts per 10 minutes
    - Always returns success to prevent email enumeration
    """
    # Check rate limit
    check_forgot_password_rate_limit(request)
    
    result = await db.execute(select(User).where(User.email == request_body.email))
    user = result.scalar_one_or_none()
    
    if user:
        # Generate reset token
        reset_token = token_urlsafe(32)
        _reset_tokens[reset_token] = user.id
        
        # TODO: Send reset email in background
        # background_tasks.add_task(send_reset_email, user.email, reset_token)
        logger.info(f"Password reset requested for: {request_body.email}")
    
    return success_response(
        message="If the email exists, a reset link will be sent",
    )


@router.post("/reset-password")
async def reset_password(
    request_body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Reset password using reset token.
    """
    # Validate token
    user_id = _reset_tokens.get(request_body.token)
    if not user_id:
        raise AppException(
            message="Invalid or expired reset token",
            code="INVALID_TOKEN",
            status_code=400,
        )
    
    # Find user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User")
    
    # Update password
    user.hashed_password = get_password_hash(request_body.new_password)
    await db.commit()
    
    # Invalidate token
    del _reset_tokens[request_body.token]
    
    logger.info(f"Password reset completed for: {user.email}")
    
    return success_response(message="Password reset successful")
