"""
NutriLens Backend - Nutrition Fact Model
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.product import Product


class NutritionFact(Base):
    """NutritionFact model for storing normalized nutrition information."""
    
    __tablename__ = "nutrition_facts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="nutrition_facts")
    
    def __repr__(self) -> str:
        return f"<NutritionFact {self.id} - {self.name}: {self.value}{self.unit}>"
