"""
NutriLens Backend - Reasoner Service

Rule engine for nutrition analysis and verdicts.
"""

from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


# Default thresholds (per serving)
DEFAULT_THRESHOLDS = {
    "calories": {"warn": 400, "critical": 600},
    "total_fat": {"warn": 15, "critical": 25},
    "saturated_fat": {"warn": 5, "critical": 10},
    "trans_fat": {"warn": 0.5, "critical": 1},
    "sodium": {"warn": 600, "critical": 1200},
    "total_sugars": {"warn": 12, "critical": 25},
    "added_sugars": {"warn": 6, "critical": 12},
    "cholesterol": {"warn": 100, "critical": 200},
}

# Sugar aliases for ingredient detection
SUGAR_ALIASES = [
    "sugar", "sucrose", "glucose", "fructose", "dextrose",
    "maltose", "lactose", "galactose", "corn syrup",
    "high fructose corn syrup", "hfcs", "honey", "molasses",
    "agave", "maple syrup", "cane juice", "fruit juice concentrate",
    "brown sugar", "raw sugar", "invert sugar", "malt syrup",
    "dextrin", "maltodextrin", "barley malt", "rice syrup",
]

# Category-specific adjustments
CATEGORY_ADJUSTMENTS = {
    "beverages": {
        "total_sugars": {"warn": 8, "critical": 15},
        "sodium": {"warn": 100, "critical": 300},
    },
    "snacks": {
        "calories": {"warn": 200, "critical": 400},
        "sodium": {"warn": 400, "critical": 800},
    },
    "cereals": {
        "total_sugars": {"warn": 8, "critical": 15},
        "dietary_fiber": {"min_recommended": 3},
    },
}


class ReasonerService:
    """Rule engine for nutrition analysis."""
    
    def __init__(self):
        self.thresholds = DEFAULT_THRESHOLDS.copy()
        self.sugar_aliases = SUGAR_ALIASES
    
    async def analyze(
        self,
        nutrition: Dict[str, Any],
        category: str = "other",
    ) -> Dict[str, Any]:
        """
        Analyze nutrition data and generate verdict.
        
        Args:
            nutrition: Parsed nutrition data
            category: Product category for adjusted thresholds
        
        Returns:
            Analysis result with verdict, score, warnings, and recommendations
        """
        if not nutrition:
            return {
                "verdict": "unknown",
                "reason": "No nutrition data available",
                "score": None,
                "warnings": [],
                "recommendations": ["Scan a clearer image of the nutrition label"],
            }
        
        # Get category-specific thresholds
        thresholds = self._get_thresholds(category)
        
        # Analyze each nutrient
        warnings = []
        critical_issues = []
        positive_aspects = []
        
        score = 100  # Start with perfect score
        
        for nutrient, limits in thresholds.items():
            value = nutrition.get(nutrient)
            
            if value is None:
                continue
            
            if "critical" in limits and value >= limits["critical"]:
                critical_issues.append(
                    f"Very high {self._format_nutrient(nutrient)}: {value}{self._get_unit(nutrient)}"
                )
                score -= 25
            elif "warn" in limits and value >= limits["warn"]:
                warnings.append(
                    f"High {self._format_nutrient(nutrient)}: {value}{self._get_unit(nutrient)}"
                )
                score -= 10
        
        # Check for positive aspects
        if nutrition.get("dietary_fiber", 0) >= 3:
            positive_aspects.append("Good source of fiber")
            score += 5
        
        if nutrition.get("protein", 0) >= 5:
            positive_aspects.append("Good source of protein")
            score += 5
        
        # Check ingredients for sugar aliases
        ingredients = nutrition.get("ingredients", "").lower()
        sugar_count = sum(1 for alias in self.sugar_aliases if alias in ingredients)
        if sugar_count >= 3:
            warnings.append(f"Contains {sugar_count} different types of sugars")
            score -= 15
        
        # Determine verdict
        score = max(0, min(100, score))  # Clamp to 0-100
        
        if score >= 70:
            verdict = "healthy"
            reason = "This product has acceptable nutrition levels"
        elif score >= 40:
            verdict = "moderate"
            reason = "This product should be consumed in moderation"
        else:
            verdict = "unhealthy"
            reason = "This product has concerning nutrition levels"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            nutrition, warnings, critical_issues, category
        )
        
        return {
            "verdict": verdict,
            "reason": reason,
            "score": score,
            "warnings": critical_issues + warnings,
            "recommendations": recommendations,
            "positive_aspects": positive_aspects,
        }
    
    def _get_thresholds(self, category: str) -> Dict[str, Dict[str, float]]:
        """Get thresholds adjusted for category."""
        thresholds = self.thresholds.copy()
        
        if category in CATEGORY_ADJUSTMENTS:
            for nutrient, limits in CATEGORY_ADJUSTMENTS[category].items():
                if nutrient in thresholds:
                    thresholds[nutrient].update(limits)
                else:
                    thresholds[nutrient] = limits
        
        return thresholds
    
    def _format_nutrient(self, nutrient: str) -> str:
        """Format nutrient name for display."""
        return nutrient.replace("_", " ").title()
    
    def _get_unit(self, nutrient: str) -> str:
        """Get unit for nutrient."""
        if nutrient in ["sodium", "cholesterol", "potassium"]:
            return "mg"
        elif nutrient == "calories":
            return ""
        else:
            return "g"
    
    def _generate_recommendations(
        self,
        nutrition: Dict[str, Any],
        warnings: List[str],
        critical_issues: List[str],
        category: str,
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if nutrition.get("sodium", 0) >= 600:
            recommendations.append(
                "Consider lower-sodium alternatives"
            )
        
        if nutrition.get("total_sugars", 0) >= 12:
            recommendations.append(
                "Look for products with less added sugar"
            )
        
        if nutrition.get("saturated_fat", 0) >= 5:
            recommendations.append(
                "Choose products lower in saturated fat"
            )
        
        if not nutrition.get("dietary_fiber"):
            recommendations.append(
                "Consider products with added fiber"
            )
        
        if not recommendations:
            recommendations.append(
                "This product fits well in a balanced diet"
            )
        
        return recommendations
