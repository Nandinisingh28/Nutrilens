"""
User Profile Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth import AuthService, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    
    Returns:
    - **id**: User ID
    - **email**: Email address
    - **name**: User's name
    - **created_at**: Account creation timestamp
    - **updated_at**: Last update timestamp
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile.
    
    Editable fields:
    - **email**: New email address (must be unique)
    - **name**: New name
    
    Password change is not supported via this endpoint.
    """
    auth_service = AuthService(db)
    
    # Validate at least one field is provided
    if update_data.email is None and update_data.name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (email or name) must be provided"
        )
    
    # Update user
    updated_user = auth_service.update_user(
        current_user,
        email=update_data.email,
        name=update_data.name
    )
    
    return UserResponse.model_validate(updated_user)
