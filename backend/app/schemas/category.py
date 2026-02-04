"""
NutriLens Backend - Category Schemas

Pydantic models for category operations.
"""

from typing import Optional
from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
