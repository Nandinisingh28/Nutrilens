"""
Verification Services Package
"""
from app.services.verification.engine import ClaimVerificationEngine
from app.services.verification.thresholds import get_thresholds, PROTEIN_BAR_THRESHOLDS, CEREAL_THRESHOLDS
from app.services.verification.claims import CLAIM_TYPES, normalize_claim, parse_compound_claim

__all__ = [
    "ClaimVerificationEngine",
    "get_thresholds",
    "PROTEIN_BAR_THRESHOLDS",
    "CEREAL_THRESHOLDS",
    "CLAIM_TYPES",
    "normalize_claim",
    "parse_compound_claim"
]
