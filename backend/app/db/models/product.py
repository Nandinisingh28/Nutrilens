"""
NutriLens Backend - Product Model
"""

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.category import Category
    from app.db.models.scan import Scan
    from app.db.models.ingredient import Ingredient
    from app.db.models.nutrition_fact import NutritionFact


class Product(Base):
    """Product model for storing normalized product information."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    scans: Mapped[List["Scan"]] = relationship("Scan", back_populates="product")
    ingredients: Mapped[List["Ingredient"]] = relationship("Ingredient", back_populates="product", cascade="all, delete-orphan")
    nutrition_facts: Mapped[List["NutritionFact"]] = relationship("NutritionFact", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Product {self.id} - {self.name} ({self.brand})>"
