"""
Scan and Related Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProductCategory(str, enum.Enum):
    """Product category enumeration"""
    PROTEIN_BAR = "PROTEIN_BAR"
    BREAKFAST_CEREAL = "BREAKFAST_CEREAL"
    BISCUITS_COOKIES = "BISCUITS_COOKIES"
    SNACKS = "SNACKS"
    CHOCOLATES_CONFECTIONERY = "CHOCOLATES_CONFECTIONERY"
    BEVERAGES = "BEVERAGES"
    ENERGY_DRINKS = "ENERGY_DRINKS"
    DAIRY_PRODUCTS = "DAIRY_PRODUCTS"
    INSTANT_NOODLES_RTE = "INSTANT_NOODLES_RTE"
    SAUCES_SPREADS = "SAUCES_SPREADS"
    HEALTH_SUPPLEMENTS = "HEALTH_SUPPLEMENTS"
    FROZEN_FOODS = "FROZEN_FOODS"


class ScanMode(str, enum.Enum):
    """Scan mode enumeration"""
    PRECISION = "PRECISION"
    QUICK = "QUICK"


class ImageType(str, enum.Enum):
    """Image type enumeration"""
    NUTRITION = "NUTRITION"
    INGREDIENTS = "INGREDIENTS"
    COMBINED = "COMBINED"


class Verdict(str, enum.Enum):
    """Claim verification verdict"""
    TRUE = "TRUE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"
    MISLEADING = "MISLEADING"
    FALSE = "FALSE"
    UNVERIFIABLE = "UNVERIFIABLE"


class Scan(Base):
    """Main scan record"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    scan_mode = Column(Enum(ScanMode), nullable=False)
    user_claim = Column(Text, nullable=False)
    final_verdict = Column(Enum(Verdict), nullable=True)
    score = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    images = relationship("ScanImage", back_populates="scan", cascade="all, delete-orphan")
    nutrition = relationship("ExtractedNutrition", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    ingredients = relationship("ExtractedIngredients", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    claim_results = relationship("ClaimResult", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan(id={self.id}, user_id={self.user_id}, verdict={self.final_verdict})>"


class ScanImage(Base):
    """Uploaded scan images"""
    __tablename__ = "scan_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    image_type = Column(Enum(ImageType), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    scan = relationship("Scan", back_populates="images")
    
    def __repr__(self):
        return f"<ScanImage(id={self.id}, type={self.image_type})>"


class ExtractedNutrition(Base):
    """Extracted nutrition data from OCR"""
    __tablename__ = "extracted_nutrition"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, unique=True, index=True)
    serving_size = Column(String(100), nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    sugar_per_100g = Column(Float, nullable=True)
    fat_per_100g = Column(Float, nullable=True)
    fiber_per_100g = Column(Float, nullable=True)
    calories_per_100g = Column(Float, nullable=True)
    sodium_per_100g = Column(Float, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    # Relationships
    scan = relationship("Scan", back_populates="nutrition")
    
    def __repr__(self):
        return f"<ExtractedNutrition(id={self.id}, scan_id={self.scan_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "serving_size": self.serving_size,
            "protein": self.protein_per_100g,
            "sugar": self.sugar_per_100g,
            "fat": self.fat_per_100g,
            "fiber": self.fiber_per_100g,
            "calories": self.calories_per_100g,
            "sodium": self.sodium_per_100g
        }


class ExtractedIngredients(Base):
    """Extracted ingredients data from OCR"""
    __tablename__ = "extracted_ingredients"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, unique=True, index=True)
    ingredients_list = Column(Text, nullable=True)
    flagged_ingredients = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    # Relationships
    scan = relationship("Scan", back_populates="ingredients")
    
    def __repr__(self):
        return f"<ExtractedIngredients(id={self.id}, scan_id={self.scan_id})>"


class ClaimResult(Base):
    """Individual claim verification results"""
    __tablename__ = "claim_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    claim_type = Column(String(100), nullable=False)
    sub_claim = Column(String(255), nullable=True)
    verdict = Column(Enum(Verdict), nullable=False)
    reason = Column(Text, nullable=True)
    
    # Relationships
    scan = relationship("Scan", back_populates="claim_results")
    
    def __repr__(self):
        return f"<ClaimResult(id={self.id}, claim={self.claim_type}, verdict={self.verdict})>"
