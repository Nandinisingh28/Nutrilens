"""
NutriLens Backend - User Schemas

Pydantic models for user operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: EmailStr
    name: str
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    goal: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, max_length=20)
    goal: Optional[str] = Field(None, max_length=255)


class UserPublic(BaseModel):
    """Public user info (limited fields)."""
    id: int
    name: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True
