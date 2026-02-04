"""
NutriLens Backend - Claim Model
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.scan import Scan
    from app.db.models.verification_result import VerificationResult


class Claim(Base):
    """Claim model for storing detected or entered claims."""
    
    __tablename__ = "claims"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    scan: Mapped["Scan"] = relationship("Scan", back_populates="claims")
    verification_results: Mapped[List["VerificationResult"]] = relationship("VerificationResult", back_populates="claim", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Claim {self.id} - {self.text}>"
