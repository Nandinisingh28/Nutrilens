"""
NutriLens Backend - Claim Verification Engine

Verifies nutrition claims against parsed data and rules.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class Verdict(str, Enum):
    """Claim verdict types."""
    TRUE = "true"
    MISLEADING = "misleading"
    FALSE = "false"
    UNKNOWN = "unknown"


@dataclass
class ClaimResult:
    """Result of claim verification."""
    claim: str
    normalized_key: str
    verdict: Verdict
    confidence: float
    evidence: List[str]
    explanation: str
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim,
            "normalized_claim_key": self.normalized_key,
            "verdict": self.verdict.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "explanation": self.explanation,
            "suggestions": self.suggestions,
        }


class ClaimVerificationEngine:
    """Engine for verifying nutrition claims."""
    
    # Claim normalization mapping
    CLAIM_NORMALIZATIONS = {
        # High protein
        "high protein": "high_protein",
        "protein rich": "high_protein",
        "rich in protein": "high_protein",
        "excellent source of protein": "high_protein",
        
        # No added sugar
        "no added sugar": "no_added_sugar",
        "no added sugars": "no_added_sugar",
        "no sugar added": "no_added_sugar",
        "without added sugar": "no_added_sugar",
        "zero added sugar": "no_added_sugar",
        
        # Low sugar
        "low sugar": "low_sugar",
        "low in sugar": "low_sugar",
        "reduced sugar": "low_sugar",
        
        # Sugar free
        "sugar free": "sugar_free",
        "zero sugar": "sugar_free",
        "no sugar": "sugar_free",
        "sugarless": "sugar_free",
        
        # No preservatives
        "no preservatives": "no_preservatives",
        "preservative free": "no_preservatives",
        "without preservatives": "no_preservatives",
        "no artificial preservatives": "no_preservatives",
        
        # Natural
        "100% natural": "all_natural",
        "all natural": "all_natural",
        "natural": "all_natural",
        "100 percent natural": "all_natural",
        
        # Whole grain
        "whole grain": "whole_grain",
        "whole wheat": "whole_grain",
        "wholegrain": "whole_grain",
        "made with whole grains": "whole_grain",
        
        # Healthy
        "healthy": "healthy",
        "healthier choice": "healthy",
        "good for you": "healthy",
        
        # High fiber
        "high fiber": "high_fiber",
        "high fibre": "high_fiber",
        "rich in fiber": "high_fiber",
        "excellent source of fiber": "high_fiber",
        
        # Low fat
        "low fat": "low_fat",
        "low in fat": "low_fat",
        "reduced fat": "low_fat",
        "lite": "low_fat",
        "light": "low_fat",
    }
    
    # Thresholds (per 100g unless specified)
    THRESHOLDS = {
        "high_protein": {"min": 10, "unit": "g"},  # >=10g per 100g
        "low_sugar": {"max": 5, "unit": "g"},  # <=5g per 100g
        "sugar_free": {"max": 0.5, "unit": "g"},  # <=0.5g per 100g
        "high_fiber": {"min": 6, "unit": "g"},  # >=6g per 100g
        "low_fat": {"max": 3, "unit": "g"},  # <=3g per 100g
    }
    
    def __init__(self):
        self.custom_thresholds: Dict[str, Dict] = {}
    
    def load_thresholds(self, rules: List[Dict]) -> None:
        """Load threshold rules from database."""
        for rule in rules:
            if rule.get('rule_type') == 'claim_threshold':
                key = rule.get('key')
                value = rule.get('value', {})
                self.custom_thresholds[key] = value
    
    def detect_claims(self, text: str, user_claims: Optional[str] = None) -> List[str]:
        """
        Detect claims from text and user input.
        
        Args:
            text: OCR text
            user_claims: User-entered claims
            
        Returns:
            List of detected claim strings
        """
        claims = []
        
        # Combine sources
        all_text = f"{text or ''} {user_claims or ''}".lower()
        
        # Search for known claim patterns
        for claim_pattern in self.CLAIM_NORMALIZATIONS.keys():
            if claim_pattern in all_text:
                claims.append(claim_pattern)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_claims = []
        for c in claims:
            if c not in seen:
                seen.add(c)
                unique_claims.append(c)
        
        return unique_claims
    
    def normalize_claim(self, claim: str) -> str:
        """Normalize a claim to standard key."""
        claim_lower = claim.lower().strip()
        return self.CLAIM_NORMALIZATIONS.get(claim_lower, "unknown")
    
    def verify_claims(
        self,
        claims: List[str],
        ingredients: Dict,
        nutrition: Dict,
    ) -> List[ClaimResult]:
        """
        Verify all claims against parsed data.
        
        Args:
            claims: List of detected claims
            ingredients: Parsed ingredients data
            nutrition: Parsed nutrition data
            
        Returns:
            List of ClaimResult
        """
        results = []
        
        for claim in claims:
            normalized = self.normalize_claim(claim)
            
            # Dispatch to specific verifier
            verifier = self._get_verifier(normalized)
            result = verifier(claim, normalized, ingredients, nutrition)
            results.append(result)
        
        return results
    
    def _get_verifier(self, normalized_key: str):
        """Get the appropriate verifier function for a claim."""
        verifiers = {
            "high_protein": self._verify_high_protein,
            "no_added_sugar": self._verify_no_added_sugar,
            "low_sugar": self._verify_low_sugar,
            "sugar_free": self._verify_sugar_free,
            "no_preservatives": self._verify_no_preservatives,
            "all_natural": self._verify_all_natural,
            "whole_grain": self._verify_whole_grain,
            "healthy": self._verify_healthy,
            "high_fiber": self._verify_high_fiber,
            "low_fat": self._verify_low_fat,
        }
        return verifiers.get(normalized_key, self._verify_unknown)
    
    def _verify_high_protein(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify high protein claim."""
        values = nutrition.get("normalized_per_100g", {})
        protein = values.get("protein")
        
        threshold = self.custom_thresholds.get("high_protein", {}).get(
            "min_per_100g", self.THRESHOLDS["high_protein"]["min"]
        )
        
        if protein is None:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.UNKNOWN,
                confidence=0.3,
                evidence=["Protein content not found in nutrition label"],
                explanation="Cannot verify claim without protein information",
                suggestions=["Ensure nutrition facts are clearly visible"],
            )
        
        if protein >= threshold:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.TRUE,
                confidence=0.95,
                evidence=[f"Protein: {protein}g per 100g (threshold: {threshold}g)"],
                explanation=f"Product contains {protein}g protein per 100g, meeting the high protein standard of {threshold}g",
            )
        elif protein >= threshold * 0.7:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.8,
                evidence=[f"Protein: {protein}g per 100g (threshold: {threshold}g)"],
                explanation=f"Product has {protein}g protein per 100g, which is close but below the {threshold}g threshold",
                suggestions=["The claim may be technically inaccurate"],
            )
        else:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Protein: {protein}g per 100g (threshold: {threshold}g)"],
                explanation=f"Product only has {protein}g protein per 100g, well below the {threshold}g threshold for high protein claims",
            )
    
    def _verify_no_added_sugar(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify no added sugar claim."""
        sugar_aliases = ingredients.get("sugar_aliases_found", [])
        has_sugar_alias = ingredients.get("has_sugar_alias", False)
        sugar_value = nutrition.get("normalized_per_100g", {}).get("sugar")
        
        if has_sugar_alias:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.95,
                evidence=[
                    "Sugar aliases found in ingredients:",
                    *[f"  - {alias}" for alias in sugar_aliases[:5]],
                ],
                explanation=f"Ingredients contain {len(sugar_aliases)} added sugar(s): {', '.join(sugar_aliases[:3])}",
                suggestions=["This product contains added sugars despite the claim"],
            )
        
        # Check if sugar content is suspiciously high
        if sugar_value and sugar_value > 10:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.7,
                evidence=[
                    f"Sugar content: {sugar_value}g per 100g",
                    "No added sugar aliases detected in ingredients",
                ],
                explanation=f"While no obvious added sugars found, {sugar_value}g sugar per 100g is relatively high",
                suggestions=["Sugar may come from natural sources or unlisted additions"],
            )
        
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.TRUE,
            confidence=0.85,
            evidence=["No added sugar aliases found in ingredients"],
            explanation="No evidence of added sugars in the ingredient list",
        )
    
    def _verify_low_sugar(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify low sugar claim."""
        values = nutrition.get("normalized_per_100g", {})
        sugar = values.get("sugar")
        
        if sugar is None:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.UNKNOWN,
                confidence=0.3,
                evidence=["Sugar content not found"],
                explanation="Cannot verify without sugar information",
            )
        
        if sugar <= 5:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.TRUE,
                confidence=0.95,
                evidence=[f"Sugar: {sugar}g per 100g (≤5g is low)"],
                explanation=f"Product contains {sugar}g sugar per 100g, qualifying as low sugar",
            )
        elif sugar <= 10:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.8,
                evidence=[f"Sugar: {sugar}g per 100g (5-10g is borderline)"],
                explanation=f"Product has {sugar}g sugar, which is moderate rather than low",
                suggestions=["Consider products with less than 5g sugar per 100g"],
            )
        else:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Sugar: {sugar}g per 100g (>10g is not low)"],
                explanation=f"Product has {sugar}g sugar per 100g, which is not low",
            )
    
    def _verify_sugar_free(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify sugar free claim."""
        values = nutrition.get("normalized_per_100g", {})
        sugar = values.get("sugar")
        
        if sugar is None:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.UNKNOWN,
                confidence=0.3,
                evidence=["Sugar content not found"],
                explanation="Cannot verify without sugar information",
            )
        
        if sugar <= 0.5:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.TRUE,
                confidence=0.95,
                evidence=[f"Sugar: {sugar}g per 100g (≤0.5g qualifies as sugar-free)"],
                explanation="Product meets the sugar-free standard",
            )
        else:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Sugar: {sugar}g per 100g (>0.5g is not sugar-free)"],
                explanation=f"Product contains {sugar}g sugar per 100g",
            )
    
    def _verify_no_preservatives(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify no preservatives claim."""
        preservatives = ingredients.get("preservatives_found", [])
        
        if preservatives:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Preservatives found: {', '.join(preservatives[:5])}"],
                explanation=f"Ingredients contain {len(preservatives)} preservative(s)",
            )
        
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.TRUE,
            confidence=0.8,
            evidence=["No known preservatives detected in ingredients"],
            explanation="No preservatives found in the ingredient list",
        )
    
    def _verify_all_natural(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify all natural/100% natural claim."""
        additives = ingredients.get("additives_found", [])
        has_sugar_alias = ingredients.get("has_sugar_alias", False)
        
        issues = []
        if additives:
            issues.append(f"Additives found: {', '.join(additives[:3])}")
        
        if issues:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.85,
                evidence=issues,
                explanation="Product contains processed or artificial ingredients",
                suggestions=["'Natural' claims are often marketing language"],
            )
        
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.TRUE,
            confidence=0.7,
            evidence=["No obvious artificial additives detected"],
            explanation="Ingredients appear to be natural, though 'natural' is loosely defined",
        )
    
    def _verify_whole_grain(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify whole grain claim."""
        ingredient_list = ingredients.get("list", [])
        
        whole_grain_keywords = [
            "whole wheat", "whole grain", "wholegrain", "whole oat",
            "brown rice", "whole rye", "whole corn", "oatmeal", "rolled oats"
        ]
        
        # Check if whole grain is in top 3 ingredients
        top_3 = ingredient_list[:3] if len(ingredient_list) >= 3 else ingredient_list
        
        for ing in top_3:
            name = ing.get("name", "").lower()
            if any(wg in name for wg in whole_grain_keywords):
                return ClaimResult(
                    claim=claim,
                    normalized_key=key,
                    verdict=Verdict.TRUE,
                    confidence=0.9,
                    evidence=[f"Whole grain found in top ingredients: {ing.get('name')}"],
                    explanation="Whole grain ingredient is among the primary ingredients",
                )
        
        # Check if any whole grain exists
        for ing in ingredient_list:
            name = ing.get("name", "").lower()
            if any(wg in name for wg in whole_grain_keywords):
                return ClaimResult(
                    claim=claim,
                    normalized_key=key,
                    verdict=Verdict.MISLEADING,
                    confidence=0.75,
                    evidence=[f"Whole grain found but not in top 3: {ing.get('name')}"],
                    explanation="Whole grain present but not a primary ingredient",
                    suggestions=["Look for products where whole grain is the first ingredient"],
                )
        
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.FALSE,
            confidence=0.85,
            evidence=["No whole grain ingredients detected"],
            explanation="Could not find whole grain in the ingredient list",
        )
    
    def _verify_healthy(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify 'healthy' claim (subjective)."""
        values = nutrition.get("normalized_per_100g", {})
        sugar = values.get("sugar", 0)
        saturated_fat = values.get("saturated_fat", 0)
        sodium = values.get("sodium", 0)
        
        concerns = []
        
        if sugar and sugar > 15:
            concerns.append(f"High sugar: {sugar}g per 100g")
        if saturated_fat and saturated_fat > 5:
            concerns.append(f"High saturated fat: {saturated_fat}g per 100g")
        if sodium and sodium > 600:
            concerns.append(f"High sodium: {sodium}mg per 100g")
        
        additives = ingredients.get("additives_found", [])
        if len(additives) > 3:
            concerns.append(f"Multiple additives: {len(additives)} found")
        
        if len(concerns) >= 2:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.8,
                evidence=concerns,
                explanation="Multiple nutritional concerns identified",
            )
        elif concerns:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.7,
                evidence=concerns,
                explanation="Some nutritional concerns identified",
                suggestions=["'Healthy' is a subjective and often overused term"],
            )
        
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.TRUE,
            confidence=0.6,
            evidence=["No major nutritional concerns found"],
            explanation="Product appears reasonably healthy, though 'healthy' is subjective",
            suggestions=["Consider your overall dietary needs"],
        )
    
    def _verify_high_fiber(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify high fiber claim."""
        values = nutrition.get("normalized_per_100g", {})
        fiber = values.get("fiber")
        
        if fiber is None:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.UNKNOWN,
                confidence=0.3,
                evidence=["Fiber content not found"],
                explanation="Cannot verify without fiber information",
            )
        
        if fiber >= 6:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.TRUE,
                confidence=0.9,
                evidence=[f"Fiber: {fiber}g per 100g (≥6g is high)"],
                explanation=f"Product contains {fiber}g fiber per 100g, qualifying as high fiber",
            )
        elif fiber >= 3:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.MISLEADING,
                confidence=0.8,
                evidence=[f"Fiber: {fiber}g per 100g (3-6g is moderate)"],
                explanation="Product has moderate fiber, not high",
            )
        else:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Fiber: {fiber}g per 100g (<3g is low)"],
                explanation=f"Product only has {fiber}g fiber per 100g",
            )
    
    def _verify_low_fat(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Verify low fat claim."""
        values = nutrition.get("normalized_per_100g", {})
        fat = values.get("fat")
        
        if fat is None:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.UNKNOWN,
                confidence=0.3,
                evidence=["Fat content not found"],
                explanation="Cannot verify without fat information",
            )
        
        if fat <= 3:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.TRUE,
                confidence=0.9,
                evidence=[f"Fat: {fat}g per 100g (≤3g is low)"],
                explanation=f"Product contains {fat}g fat per 100g, qualifying as low fat",
            )
        else:
            return ClaimResult(
                claim=claim,
                normalized_key=key,
                verdict=Verdict.FALSE,
                confidence=0.9,
                evidence=[f"Fat: {fat}g per 100g (>3g is not low)"],
                explanation=f"Product has {fat}g fat per 100g",
            )
    
    def _verify_unknown(
        self, claim: str, key: str, ingredients: Dict, nutrition: Dict
    ) -> ClaimResult:
        """Handle unknown/unrecognized claims."""
        return ClaimResult(
            claim=claim,
            normalized_key=key,
            verdict=Verdict.UNKNOWN,
            confidence=0.5,
            evidence=["Claim not recognized"],
            explanation=f"Unable to verify '{claim}' - not in our verification database",
            suggestions=["This claim may require manual verification"],
        )
    
    def compute_overall_verdict(self, claim_results: List[ClaimResult]) -> Dict:
        """Compute overall verdict from individual claim results."""
        if not claim_results:
            return {
                "verdict": "unknown",
                "confidence": 0,
                "summary": "No claims to verify",
                "claim_count": 0,
            }
        
        verdict_counts = {
            Verdict.TRUE: 0,
            Verdict.MISLEADING: 0,
            Verdict.FALSE: 0,
            Verdict.UNKNOWN: 0,
        }
        
        total_confidence = 0
        for result in claim_results:
            verdict_counts[result.verdict] += 1
            total_confidence += result.confidence
        
        avg_confidence = total_confidence / len(claim_results)
        
        # Determine overall verdict
        if verdict_counts[Verdict.FALSE] > 0:
            overall = "false"
            summary = f"{verdict_counts[Verdict.FALSE]} claim(s) are false"
        elif verdict_counts[Verdict.MISLEADING] > 0:
            if verdict_counts[Verdict.TRUE] > 0:
                overall = "mixed"
                summary = f"{verdict_counts[Verdict.TRUE]} true, {verdict_counts[Verdict.MISLEADING]} misleading"
            else:
                overall = "misleading"
                summary = f"{verdict_counts[Verdict.MISLEADING]} claim(s) are misleading"
        elif verdict_counts[Verdict.TRUE] > 0:
            overall = "true"
            summary = f"All {verdict_counts[Verdict.TRUE]} claim(s) verified as true"
        else:
            overall = "unknown"
            summary = "Unable to verify claims"
        
        return {
            "verdict": overall,
            "confidence": round(avg_confidence, 2),
            "summary": summary,
            "claim_count": len(claim_results),
            "breakdown": {
                "true": verdict_counts[Verdict.TRUE],
                "misleading": verdict_counts[Verdict.MISLEADING],
                "false": verdict_counts[Verdict.FALSE],
                "unknown": verdict_counts[Verdict.UNKNOWN],
            },
        }


# Singleton instance
claim_engine = ClaimVerificationEngine()
