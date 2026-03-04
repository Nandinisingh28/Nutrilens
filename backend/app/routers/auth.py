"""
Authentication Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth import AuthService
from app.services.email import send_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **name**: User's full name
    - **password**: Password (minimum 6 characters)
    
    Returns JWT access token on success.
    """
    auth_service = AuthService(db)
    
    # Create user
    user = auth_service.create_user(user_data)
    
    # Generate token
    token = auth_service.create_token_for_user(user)
    
    return token


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and get access token.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT access token on success.
    """
    auth_service = AuthService(db)
    
    # Authenticate
    user = auth_service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    token = auth_service.create_token_for_user(user)
    
    return token


@router.post("/logout")
async def logout():
    """
    Logout user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the stored token. This endpoint is provided for
    API completeness.
    """
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset link.
    
    - **email**: Registered email address
    
    Always returns a generic success message to prevent email enumeration.
    """
    auth_service = AuthService(db)
    
    # Generate token (returns None if email doesn't exist)
    token = auth_service.create_reset_token(request.email)
    
    # Send email if user exists
    if token:
        send_reset_email(request.email, token)
    
    # Always return success to prevent email enumeration
    return {"message": "If an account exists with this email, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token.
    
    - **token**: Reset token from the email link
    - **new_password**: New password (minimum 6 characters)
    """
    auth_service = AuthService(db)
    
    auth_service.reset_password(request.token, request.new_password)
    
    return {"message": "Password has been reset successfully. You can now log in with your new password."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user = Depends(__import__('app.services.auth', fromlist=['get_current_user']).get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)
