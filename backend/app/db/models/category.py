"""
NutriLens Backend - Category Model

Product categories for organizing scans.
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.scan import Scan
    from app.db.models.rule import Rule
    from app.db.models.product import Product


class Category(Base):
    """Category model for product classification."""
    
    __tablename__ = "categories"
    
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    scans: Mapped[list["Scan"]] = relationship(
        "Scan",
        back_populates="category_rel",
        lazy="dynamic",
    )
    rules: Mapped[list["Rule"]] = relationship(
        "Rule",
        back_populates="category",
        lazy="dynamic",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        lazy="dynamic",
    )
    
    def __repr__(self) -> str:
        return f"<Category {self.slug}>"
