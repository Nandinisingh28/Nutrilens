"""
Database-Driven Rule Models
Stores category nutrition thresholds, claim verification rules, and ingredient risks.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Enum
from app.database import Base
import enum


class RiskLevel(str, enum.Enum):
    """Risk level for flagged ingredients"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CategoryNutritionRule(Base):
    """
    Per-category nutrition thresholds for health evaluation.
    Defines what is considered healthy/unhealthy for each food category.
    """
    __tablename__ = "category_nutrition_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True, unique=True)
    protein_min = Column(Float, nullable=True, comment="Minimum protein (g/100g) for healthy rating")
    sugar_max = Column(Float, nullable=True, comment="Maximum sugar (g/100g) for healthy rating")
    fat_max = Column(Float, nullable=True, comment="Maximum fat (g/100g) for healthy rating")
    fiber_min = Column(Float, nullable=True, comment="Minimum fiber (g/100g) for healthy rating")
    sodium_max = Column(Float, nullable=True, comment="Maximum sodium (mg/100g) for healthy rating")
    calories_max = Column(Float, nullable=True, comment="Maximum calories (kcal/100g) for healthy rating")

    def __repr__(self):
        return f"<CategoryNutritionRule(category={self.category})>"


class ClaimRule(Base):
    """
    Per-category claim verification rules.
    Each row defines one condition for a claim type within a category.
    A claim type may have multiple rows (conditions) for a single category.
    """
    __tablename__ = "claim_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    claim_type = Column(String(100), nullable=False, index=True, comment="e.g. HIGH_PROTEIN, LOW_SUGAR")
    category = Column(String(50), nullable=False, index=True)
    nutrient = Column(String(50), nullable=True, comment="e.g. protein_per_100g, sugar_per_100g")
    operator = Column(String(10), nullable=True, comment="gte, lte, gt, lt")
    threshold = Column(Float, nullable=True, comment="Threshold value for the nutrient")
    requires_ingredient_check = Column(Boolean, default=False, nullable=False)
    ingredient_check_type = Column(String(50), nullable=True, comment="e.g. no_sugar, clean, no_trans_fat")
    description = Column(String(255), nullable=True, comment="Human-readable description of the rule")

    def __repr__(self):
        return f"<ClaimRule(claim={self.claim_type}, category={self.category}, nutrient={self.nutrient})>"


class IngredientRiskMaster(Base):
    """
    Master list of concerning ingredients with risk categorization.
    Used for flagging harmful/risky ingredients during scans.
    """
    __tablename__ = "ingredient_risk_master"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ingredient_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, comment="e.g. artificial_sweetener, preservative, added_sugar")
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM)
    description = Column(Text, nullable=True, comment="Why this ingredient is flagged")

    def __repr__(self):
        return f"<IngredientRiskMaster(name={self.ingredient_name}, risk={self.risk_level})>"
