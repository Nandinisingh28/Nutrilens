"""
NutriLens Backend - Scan Model

Scan entity for storing nutrition label scan history.
"""

from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.category import Category
    from app.db.models.file_asset import FileAsset
    from app.db.models.product import Product
    from app.db.models.claim import Claim
    from app.db.models.verification_result import VerificationResult


class OverallVerdict(str, Enum):
    """Overall verdict for nutrition claim analysis."""
    TRUE = "true"
    MISLEADING = "misleading"
    FALSE = "false"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Scan(Base):
    """Scan model for nutrition label analysis history."""
    
    __tablename__ = "scans"
    
    # Relationships - User
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship("User", back_populates="scans")
    
    # Relationships - Product
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="scans")
    
    # Relationships - Category
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    category_rel: Mapped["Category"] = relationship("Category", back_populates="scans")
    
    # Relationships - Label Image (legacy single image)
    label_image_file_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("file_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    label_image: Mapped[Optional["FileAsset"]] = relationship(
        "FileAsset",
        foreign_keys=[label_image_file_id],
        lazy="joined",
    )
    
    # NEW: Ingredients Image
    ingredients_image_file_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("file_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    ingredients_image: Mapped[Optional["FileAsset"]] = relationship(
        "FileAsset",
        foreign_keys=[ingredients_image_file_id],
        lazy="joined",
    )
    
    # NEW: Nutrition Image
    nutrition_image_file_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("file_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    nutrition_image: Mapped[Optional["FileAsset"]] = relationship(
        "FileAsset",
        foreign_keys=[nutrition_image_file_id],
        lazy="joined",
    )
    
    # Relationships - Others
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="scan", cascade="all, delete-orphan")
    verification_results: Mapped[List["VerificationResult"]] = relationship("VerificationResult", back_populates="scan", cascade="all, delete-orphan")
    
    # User input
    claim_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # OCR Results - Legacy (single image)
    ocr_raw_text: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    
    # NEW: OCR Results - Separate sources
    ocr_raw_ingredients_text: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    ocr_raw_nutrition_text: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    
    # Analysis Results Summary
    overall_verdict: Mapped[OverallVerdict] = mapped_column(
        SQLEnum(OverallVerdict),
        default=OverallVerdict.UNKNOWN,
    )
    
    # Metadata for fallback/debugging
    raw_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Scan {self.id} - {self.overall_verdict}>"
