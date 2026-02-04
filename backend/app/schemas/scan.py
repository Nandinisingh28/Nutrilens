"""
NutriLens Backend - Scan Schemas

Pydantic models for scan operations.
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field

from app.db.models.scan import OverallVerdict


class IngredientSchema(BaseModel):
    id: int
    name: str
    position: int
    is_sugar_alias: bool
    is_additive: bool
    is_preservative: bool

    class Config:
        from_attributes = True


class NutritionFactSchema(BaseModel):
    id: int
    name: str
    value: float
    unit: str

    class Config:
        from_attributes = True


class VerificationResultSchema(BaseModel):
    id: int
    verdict: str
    confidence: float
    explanation: str
    evidence: dict

    class Config:
        from_attributes = True


class ClaimSchema(BaseModel):
    id: int
    text: str
    verifications: list[VerificationResultSchema] = Field(default_factory=list, alias="verification_results")

    class Config:
        from_attributes = True
        populate_by_name = True


class OCRResult(BaseModel):
    """OCR result for a single image."""
    confidence: float = Field(0.0, description="OCR confidence score 0-1")
    word_count: int = Field(0, description="Number of words detected")
    raw_text: Optional[str] = Field(None, description="Raw OCR text")
    quality: str = Field("unknown", description="Quality indicator: good/medium/low")


class OCRResults(BaseModel):
    """OCR results for both images."""
    ingredients: Optional[OCRResult] = None
    nutrition: Optional[OCRResult] = None
    # Legacy single-image result
    combined: Optional[OCRResult] = None


class ScanCreate(BaseModel):
    """Schema for creating a scan."""
    category_id: int
    product_name: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    claim_text: Optional[str] = Field(None, max_length=1000)
    # Legacy
    label_image_file_id: Optional[int] = None
    # New two-image support
    ingredients_image_file_id: Optional[int] = None
    nutrition_image_file_id: Optional[int] = None


class ScanResponse(BaseModel):
    """Schema for scan response."""
    id: int
    user_id: int
    category_id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    brand: Optional[str] = None
    claim_text: Optional[str] = None
    # Legacy image
    label_image_file_id: Optional[int] = None
    label_image_url: Optional[str] = None
    # New two-image support
    ingredients_image_file_id: Optional[int] = None
    nutrition_image_file_id: Optional[int] = None
    ingredients_image_url: Optional[str] = None
    nutrition_image_url: Optional[str] = None
    # OCR data
    ocr_raw_text: Optional[str] = None
    ocr_raw_ingredients_text: Optional[str] = None
    ocr_raw_nutrition_text: Optional[str] = None
    ocr_results: Optional[OCRResults] = None
    # Parsed data
    parsed_ingredients: Optional[dict] = None
    parsed_nutrition: Optional[dict] = None
    # Analysis
    results: Optional[dict] = Field(None, description="Legacy analysis results (deprecated)")
    overall_verdict: OverallVerdict
    
    # Normalized data
    ingredientsList: Optional[list[IngredientSchema]] = Field(None, alias="ingredients")
    nutritionFactsList: Optional[list[NutritionFactSchema]] = Field(None, alias="nutrition_facts")
    claimsList: Optional[list[ClaimSchema]] = Field(None, alias="claims")
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanSummary(BaseModel):
    """Schema for scan list summary."""
    id: int
    product_name: Optional[str] = None
    brand: Optional[str] = None
    category_id: int
    overall_verdict: OverallVerdict
    created_at: datetime
    # Include image URLs for thumbnails
    label_image_url: Optional[str] = None
    ingredients_image_url: Optional[str] = None
    nutrition_image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ScanUpdate(BaseModel):
    """Schema for updating a scan."""
    product_name: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    claim_text: Optional[str] = Field(None, max_length=1000)
