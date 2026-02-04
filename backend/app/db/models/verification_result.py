"""
NutriLens Backend - Verification Result Model
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Float, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.scan import OverallVerdict as VerdictEnum # Reusing OverallVerdict for consistency if applicable, but maybe specific Verdict is better

if TYPE_CHECKING:
    from app.db.models.scan import Scan
    from app.db.models.claim import Claim


class VerificationResult(Base):
    """VerificationResult model for storing verification outcomes for each claim."""
    
    __tablename__ = "verification_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claim_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    verdict: Mapped[VerdictEnum] = mapped_column(
        SQLEnum(VerdictEnum),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Relationships
    scan: Mapped["Scan"] = relationship("Scan", back_populates="verification_results")
    claim: Mapped["Claim"] = relationship("Claim", back_populates="verification_results")
    
    def __repr__(self) -> str:
        return f"<VerificationResult {self.id} for Scan {self.scan_id} - {self.verdict}>"
