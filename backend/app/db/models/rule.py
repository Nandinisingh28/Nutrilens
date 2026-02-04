"""
NutriLens Backend - Rule Model

Rules for nutrition claim verification.
"""

from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.category import Category


class RuleType(str, Enum):
    """Types of verification rules."""
    SUGAR_ALIAS = "sugar_alias"
    ADDITIVE = "additive"
    CLAIM_THRESHOLD = "claim_threshold"
    CLAIM_PATTERN = "claim_pattern"


class Rule(Base):
    """Rule model for claim verification logic."""
    
    __tablename__ = "rules"
    
    # Category (null = global rule)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="rules")
    
    # Rule definition
    rule_type: Mapped[RuleType] = mapped_column(
        SQLEnum(RuleType),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def __repr__(self) -> str:
        return f"<Rule {self.rule_type} - {self.key}>"
