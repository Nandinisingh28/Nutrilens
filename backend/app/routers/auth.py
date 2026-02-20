"""
Authentication Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import AuthService

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
