"""
NutriLens Backend - Ingredient Model
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.product import Product


class Ingredient(Base):
    """Ingredient model for storing normalized ingredient information."""
    
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    
    is_sugar_alias: Mapped[bool] = mapped_column(Boolean, default=False)
    is_additive: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preservative: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="ingredients")
    
    def __repr__(self) -> str:
        return f"<Ingredient {self.id} - {self.name} (pos: {self.position})>"
