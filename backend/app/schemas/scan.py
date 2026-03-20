"""
Scan Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ProductCategory(str, Enum):
    """Product category enumeration"""
    PROTEIN_BAR = "PROTEIN_BAR"
    BREAKFAST_CEREAL = "BREAKFAST_CEREAL"
    BISCUITS_COOKIES = "BISCUITS_COOKIES"
    SNACKS = "SNACKS"
    CHOCOLATES_CONFECTIONERY = "CHOCOLATES_CONFECTIONERY"
    BEVERAGES = "BEVERAGES"
    ENERGY_DRINKS = "ENERGY_DRINKS"
    INSTANT_NOODLES_RTE = "INSTANT_NOODLES_RTE"
    SAUCES_SPREADS = "SAUCES_SPREADS"
    HEALTH_SUPPLEMENTS = "HEALTH_SUPPLEMENTS"
    FROZEN_FOODS = "FROZEN_FOODS"


class ScanMode(str, Enum):
    """Scan mode enumeration"""
    PRECISION = "PRECISION"
    QUICK = "QUICK"


class Verdict(str, Enum):
    """Claim verification verdict"""
    TRUE = "TRUE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"
    MISLEADING = "MISLEADING"
    FALSE = "FALSE"
    UNVERIFIABLE = "UNVERIFIABLE"


class ScanCreate(BaseModel):
    """Schema for creating a new scan"""
    category: ProductCategory = Field(..., description="Product category")
    claim: str = Field(..., min_length=1, max_length=500, description="User's claim to verify")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "PROTEIN_BAR",
                "claim": "High Protein and Low Sugar"
            }
        }


class NutritionData(BaseModel):
    """Extracted nutrition information"""
    serving_size: Optional[str] = None
    protein: Optional[float] = Field(None, description="Protein per 100g")
    sugar: Optional[float] = Field(None, description="Sugar per 100g")
    fat: Optional[float] = Field(None, description="Fat per 100g")
    fiber: Optional[float] = Field(None, description="Fiber per 100g")
    calories: Optional[float] = Field(None, description="Calories per 100g")
    sodium: Optional[float] = Field(None, description="Sodium per 100g")
    carbohydrates: Optional[float] = Field(None, description="Total carbohydrates per 100g")
    saturated_fat: Optional[float] = Field(None, description="Saturated fat per 100g")
    trans_fat: Optional[float] = Field(None, description="Trans fat per 100g")
    cholesterol: Optional[float] = Field(None, description="Cholesterol per 100g in mg")
    
    class Config:
        from_attributes = True


class ClaimResultResponse(BaseModel):
    """Individual claim verification result"""
    claim_type: str
    sub_claim: Optional[str] = None
    verdict: Verdict
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    """Full scan result response"""
    scan_id: int
    category: ProductCategory
    scan_mode: ScanMode
    user_claim: str
    verdict: Optional[Verdict] = None
    score: Optional[float] = None
    health_score: Optional[float] = Field(None, description="ML-based health score (0-100)")
    explanation: Optional[str] = None
    nutrition: Optional[NutritionData] = None
    ingredient_warnings: List[str] = []
    sub_claims: List[ClaimResultResponse] = []
    created_at: datetime
    # Debug fields for OCR output
    ocr_nutrition_text: Optional[str] = Field(None, description="Raw OCR text from nutrition label")
    ocr_ingredients_text: Optional[str] = Field(None, description="Raw OCR text from ingredients list")
    
    class Config:
        from_attributes = True


class ScanHistoryItem(BaseModel):
    """Scan history list item"""
    scan_id: int
    category: ProductCategory
    scan_mode: ScanMode
    user_claim: str
    final_verdict: Optional[Verdict] = None
    score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    """Scan history response"""
    scans: List[ScanHistoryItem] = []
    total: int = 0
