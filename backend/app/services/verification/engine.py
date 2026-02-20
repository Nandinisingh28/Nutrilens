"""
Claim Verification Engine
Hybrid approach: ML for health scoring + Rule-based for claim verification
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.services.verification.thresholds import get_thresholds, evaluate_condition
from app.services.verification.claims import (
    parse_compound_claim, 
    get_claim_description,
    is_nutrition_dependent,
    is_ingredient_dependent
)
from app.services.ml.model import get_health_model
from app.services.ocr.parser import NutritionInfo, IngredientsInfo, IngredientsParser

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None


class Verdict(str, Enum):
    """Claim verification verdict"""
    TRUE = "TRUE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"
    MISLEADING = "MISLEADING"
    FALSE = "FALSE"
    UNVERIFIABLE = "UNVERIFIABLE"


@dataclass
class SubClaimResult:
    """Result for an individual sub-claim"""
    claim_type: str
    display_name: str
    verdict: Verdict
    reason: str
    actual_value: Optional[str] = None
    threshold_value: Optional[str] = None


@dataclass
class VerificationResult:
    """Complete verification result"""
    final_verdict: Verdict
    score: float
    explanation: str
    sub_claims: List[SubClaimResult] = field(default_factory=list)
    ingredient_warnings: List[str] = field(default_factory=list)
    health_score: float = 0
    risk_labels: List[str] = field(default_factory=list)


class ClaimVerificationEngine:
    """
    Engine for verifying food packaging claims.
    Uses a hybrid approach combining ML health scoring with rule-based verification.
    """
    
    def __init__(self, db=None):
        self.health_model = get_health_model()
        self.ingredients_parser = IngredientsParser(db=db)
        self.db = db
    
    def verify(
        self,
        claim: str,
        category: str,
        nutrition: Optional[NutritionInfo] = None,
        ingredients: Optional[IngredientsInfo] = None
    ) -> VerificationResult:
        """
        Verify a user claim against extracted nutrition and ingredient data.
        
        Args:
            claim: User's claim to verify
            category: Product category (PROTEIN_BAR or BREAKFAST_CEREAL)
            nutrition: Extracted nutrition info
            ingredients: Extracted ingredients info
            
        Returns:
            VerificationResult with verdict and analysis
        """
        # Parse compound claims
        claim_types = parse_compound_claim(claim)
        
        if not claim_types:
            # Could not parse any recognizable claims
            return self._unverifiable_result(
                "Could not identify specific claims to verify. Please use clearer claim terms like 'High Protein', 'Low Sugar', etc."
            )
        
        # Get category thresholds
        thresholds = get_thresholds(category, db=self.db)
        
        # Check if we have required data
        has_nutrition = self._has_valid_nutrition(nutrition)
        has_ingredients = ingredients is not None and ingredients.raw_text
        
        # Prepare nutrition dict for evaluation
        nutrition_dict = self._nutrition_to_dict(nutrition) if nutrition else {}
        
        # Create ingredient flags
        ingredient_flags = self._create_ingredient_flags(ingredients) if ingredients else {}
        
        # Get ML health score
        ml_result = None
        if has_nutrition:
            ml_result = self.health_model.predict(nutrition_dict, ingredient_flags)
        
        # Verify each sub-claim
        sub_results = []
        for claim_type in claim_types:
            result = self._verify_single_claim(
                claim_type,
                thresholds,
                nutrition_dict,
                ingredients,
                ingredient_flags,
                has_nutrition,
                has_ingredients
            )
            sub_results.append(result)
        
        # Calculate final verdict
        final_verdict, score = self._calculate_final_verdict(sub_results)
        
        # Generate explanation
        explanation = self._generate_explanation(
            sub_results, 
            final_verdict, 
            nutrition_dict,
            category
        )
        
        # Get ingredient warnings
        warnings = self._get_ingredient_warnings(ingredients) if ingredients else []
        
        return VerificationResult(
            final_verdict=final_verdict,
            score=score,
            explanation=explanation,
            sub_claims=sub_results,
            ingredient_warnings=warnings,
            health_score=ml_result.score if ml_result else 0,
            risk_labels=ml_result.risk_labels if ml_result else []
        )
    
    def _verify_single_claim(
        self,
        claim_type: str,
        thresholds: Dict,
        nutrition: Dict,
        ingredients: Optional[IngredientsInfo],
        ingredient_flags: Dict,
        has_nutrition: bool,
        has_ingredients: bool
    ) -> SubClaimResult:
        """Verify a single claim type"""
        
        threshold_def = thresholds.get(claim_type)
        display_name = get_claim_description(claim_type)
        
        if threshold_def is None:
            return SubClaimResult(
                claim_type=claim_type,
                display_name=display_name,
                verdict=Verdict.UNVERIFIABLE,
                reason=f"No verification rules defined for '{display_name}'"
            )
        
        # Check data requirements
        needs_nutrition = is_nutrition_dependent(claim_type)
        needs_ingredients = is_ingredient_dependent(claim_type)
        
        # Special handling for sugar-related claims
        # Different logic for "no sugar" vs "low sugar"
        is_no_sugar_claim = claim_type in ['NO_ADDED_SUGAR', 'NO_SUGAR', 'SUGAR_FREE', 'ZERO_SUGAR']
        is_low_sugar_claim = claim_type == 'LOW_SUGAR'
        
        if (is_no_sugar_claim or is_low_sugar_claim) and has_ingredients:
            has_sugar_in_ingredients = self.ingredients_parser.has_added_sugar(ingredients)
            
            # Check for sweeteners (common logic for all sugar claims)
            sweeteners = [
                item['ingredient'].title() 
                for item in ingredients.flagged_ingredients 
                if item['category'] == 'artificial_sweetener'
            ]
            sweetener_msg = ""
            if sweeteners:
                names = ", ".join(sweeteners)
                lower_names = names.lower()
                context_msg = ""
                if 'stevia' in lower_names:
                    context_msg = " Stevia is a natural option."
                elif 'sucralose' in lower_names:
                    context_msg = " Sucralose is a common zero-calorie sweetener."
                elif 'aspartame' in lower_names:
                    context_msg = " Contains Aspartame."
                sweetener_msg = f" (Contains: {names}.{context_msg})"

            if not has_sugar_in_ingredients:
                reason_text = "No sugar ingredients found" + sweetener_msg
                return SubClaimResult(
                    claim_type=claim_type,
                    display_name=display_name,
                    verdict=Verdict.TRUE,
                    reason=reason_text
                )
            else:
                # Sugar IS in ingredients
                if is_no_sugar_claim:
                    # "No sugar" claim but sugar found - FALSE
                    return SubClaimResult(
                        claim_type=claim_type,
                        display_name=display_name,
                        verdict=Verdict.FALSE,
                        reason=f"Sugar found in ingredients list{sweetener_msg}"
                    )
                elif is_low_sugar_claim:
                    # "Low sugar" needs to check actual amount in nutrition facts
                    sugar_amount = nutrition.get('sugar_per_100g')
                    if sugar_amount is not None:
                        # Use per-category threshold from DB rules
                        low_sugar_threshold = 5.0  # default fallback
                        low_sugar_def = thresholds.get('LOW_SUGAR', {})
                        ls_conditions = low_sugar_def.get('conditions', [])
                        for cond in ls_conditions:
                            if cond.get('nutrient') == 'sugar_per_100g':
                                low_sugar_threshold = cond.get('value', 5.0)
                                break
                        if sugar_amount <= low_sugar_threshold:
                            return SubClaimResult(
                                claim_type=claim_type,
                                display_name=display_name,
                                verdict=Verdict.TRUE,
                                reason=f"Sugar is {sugar_amount}g per 100g (≤{low_sugar_threshold}g){sweetener_msg}"
                            )
                        else:
                            return SubClaimResult(
                                claim_type=claim_type,
                                display_name=display_name,
                                verdict=Verdict.FALSE,
                                reason=f"Sugar is {sugar_amount}g per 100g (>{low_sugar_threshold}g){sweetener_msg}"
                            )
                    else:
                        # Sugar in ingredients but can't verify amount
                        return SubClaimResult(
                            claim_type=claim_type,
                            display_name=display_name,
                            verdict=Verdict.UNVERIFIABLE,
                            reason="Sugar found in ingredients but amount not available to verify 'low sugar' claim"
                        )
        
        if needs_nutrition and not has_nutrition:
            return SubClaimResult(
                claim_type=claim_type,
                display_name=display_name,
                verdict=Verdict.UNVERIFIABLE,
                reason=f"Could not extract nutrition facts from image to verify '{display_name}' claim. Please ensure the nutrition label is clearly visible."
            )
        
        if needs_ingredients and not has_ingredients:
            # Some claims can proceed without ingredients, but with reduced confidence
            pass
        
        # Evaluate nutritional conditions
        conditions = threshold_def.get('conditions', [])
        conditions_met = 0
        conditions_failed = []
        conditions_unverifiable = []
        
        for condition in conditions:
            nutrient = condition['nutrient']
            comparison = condition['comparison']
            threshold_value = condition['value']
            
            actual = nutrition.get(nutrient)
            
            if actual is None:
                conditions_unverifiable.append(nutrient)
                continue
            
            if evaluate_condition(nutrition, nutrient, comparison, threshold_value):
                conditions_met += 1
            else:
                conditions_failed.append({
                    'nutrient': nutrient,
                    'actual': actual,
                    'threshold': threshold_value,
                    'comparison': comparison
                })
        
        # Evaluate ingredient check if required
        ingredient_check = threshold_def.get('ingredient_check')
        ingredient_passed = True
        ingredient_reason = ""
        
        if ingredient_check and has_ingredients:
            ingredient_passed, ingredient_reason = self._check_ingredient_requirement(
                ingredient_check,
                ingredients,
                ingredient_flags
            )
        
        # Determine verdict
        total_conditions = len(conditions)
        
        if total_conditions == 0:
            # Pure ingredient-based claim
            if ingredient_check:
                if ingredient_passed:
                    verdict = Verdict.TRUE
                    reason = f"{display_name} verified: {ingredient_reason}"
                else:
                    verdict = Verdict.FALSE
                    reason = f"{display_name} not verified: {ingredient_reason}"
            else:
                verdict = Verdict.UNVERIFIABLE
                reason = f"No verification rules defined for '{display_name}' - this claim type may not be supported"
        
        elif len(conditions_unverifiable) == total_conditions:
            # All conditions unverifiable - list missing nutrients
            missing = [n.replace('_per_100g', '').replace('_', ' ').title() for n in conditions_unverifiable]
            verdict = Verdict.UNVERIFIABLE
            reason = f"Missing required nutrition data: {', '.join(missing)}. Could not extract from image."
        
        elif conditions_met == total_conditions and (ingredient_passed or not ingredient_check):
            # All conditions met
            verdict = Verdict.TRUE
            reason = self._format_success_reason(claim_type, nutrition, threshold_def)
        
        elif conditions_met == 0 and len(conditions_failed) == total_conditions:
            # All conditions failed
            verdict = Verdict.FALSE
            reason = self._format_failure_reason(claim_type, conditions_failed, threshold_def)
        
        elif conditions_met > 0:
            # Some conditions met
            if conditions_met >= total_conditions / 2:
                verdict = Verdict.PARTIALLY_TRUE
            else:
                verdict = Verdict.MISLEADING
            reason = self._format_partial_reason(claim_type, conditions_met, total_conditions, conditions_failed)
        
        else:
            verdict = Verdict.UNVERIFIABLE
            reason = f"Insufficient data to verify '{display_name}' - some nutrition values could not be extracted"
        
        # Adjust for ingredient issues
        if not ingredient_passed and verdict in (Verdict.TRUE, Verdict.PARTIALLY_TRUE):
            if verdict == Verdict.TRUE:
                verdict = Verdict.MISLEADING
            reason += f" However, {ingredient_reason}"
        
        # Format actual and threshold values
        actual_str = None
        threshold_str = None
        if conditions and nutrition.get(conditions[0]['nutrient']) is not None:
            actual_str = f"{nutrition.get(conditions[0]['nutrient'])}g per 100g"
            threshold_str = threshold_def.get('description', '')
        
        return SubClaimResult(
            claim_type=claim_type,
            display_name=display_name,
            verdict=verdict,
            reason=reason,
            actual_value=actual_str,
            threshold_value=threshold_str
        )
    
    def _check_ingredient_requirement(
        self,
        check_type: str,
        ingredients: IngredientsInfo,
        flags: Dict
    ) -> Tuple[bool, str]:
        """Check ingredient-based requirements"""
        
        if check_type == 'no_added_sugar' or check_type == 'no_sugar':
            has_sugar = self.ingredients_parser.has_added_sugar(ingredients)
            if has_sugar:
                return False, "Product contains sugar ingredients"
            return True, "No sugar ingredients found"
        
        elif check_type == 'clean':
            count = self.ingredients_parser.count_concerning_ingredients(ingredients)
            if count == 0:
                return True, "No concerning ingredients found"
            return False, f"Found {count} concerning ingredient(s)"
        
        elif check_type == 'no_trans_fat':
            has_trans = self.ingredients_parser.has_trans_fats(ingredients)
            if has_trans:
                return False, "Product may contain trans fats"
            return True, "No trans fats detected"
        
        elif check_type == 'natural':
            has_artificial = self.ingredients_parser.has_artificial_sweeteners(ingredients)
            has_preserv = self.ingredients_parser.has_preservatives(ingredients)
            if has_artificial or has_preserv:
                return False, "Contains artificial ingredients"
            return True, "No artificial ingredients detected"
        
        elif check_type == 'no_preservatives':
            has_preserv = self.ingredients_parser.has_preservatives(ingredients)
            if has_preserv:
                return False, "Contains preservatives"
            return True, "No preservatives detected"
        
        elif check_type == 'no_artificial':
            has_artificial = self.ingredients_parser.has_artificial_sweeteners(ingredients)
            if has_artificial:
                return False, "Contains artificial sweeteners"
            return True, "No artificial additives detected"
        
        elif check_type == 'organic':
            # Cannot fully verify organic certification from label alone
            # Check for non-organic harmful ingredients as a proxy
            count = self.ingredients_parser.count_concerning_ingredients(ingredients)
            if count > 2:
                return False, f"Found {count} concerning ingredients – unlikely to be truly organic"
            return True, "No contradicting ingredients found (note: organic certification cannot be verified from label alone)"
        
        elif check_type == 'high_calcium':
            # Partially verifiable – look for calcium-related ingredients
            raw = ingredients.raw_text.lower() if ingredients.raw_text else ""
            calcium_keywords = ['calcium', 'milk solids', 'cheese', 'yogurt', 'curd', 'paneer', 'ragi', 'finger millet']
            found = [kw for kw in calcium_keywords if kw in raw]
            if found:
                return True, f"Calcium-related ingredients found: {', '.join(found)} (partially verifiable – exact calcium content not on label)"
            return False, "No calcium-rich ingredients detected (partially verifiable)"
        
        elif check_type == 'no_artificial_colors':
            raw = ingredients.raw_text.lower() if ingredients.raw_text else ""
            color_keywords = ['red 40', 'yellow 5', 'yellow 6', 'blue 1', 'blue 2',
                              'tartrazine', 'sunset yellow', 'allura red', 'brilliant blue',
                              'artificial color', 'artificial colour', 'fd&c', 'e102', 'e110', 'e129', 'e133']
            found = [kw for kw in color_keywords if kw in raw]
            if found:
                return False, f"Artificial colors found: {', '.join(found)}"
            return True, "No artificial colors detected in ingredients"
        
        elif check_type == 'no_artificial_flavors':
            raw = ingredients.raw_text.lower() if ingredients.raw_text else ""
            flavor_keywords = ['artificial flavor', 'artificial flavour', 'nature identical',
                               'synthetic flavor', 'imitation flavor']
            found = [kw for kw in flavor_keywords if kw in raw]
            if found:
                return False, f"Artificial flavors found: {', '.join(found)}"
            return True, "No artificial flavors detected in ingredients"
        
        elif check_type == 'whole_grain':
            raw = ingredients.raw_text.lower() if ingredients.raw_text else ""
            wg_keywords = ['whole grain', 'whole wheat', 'whole oat', 'whole rye', 'whole corn',
                           'brown rice', 'whole barley', 'oats', 'millet', 'quinoa', 'ragi']
            found = [kw for kw in wg_keywords if kw in raw]
            if found:
                return True, f"Whole grain ingredients found: {', '.join(found)}"
            return False, "No whole grain ingredients detected"
        
        return True, ""
    
    def _calculate_final_verdict(
        self,
        sub_results: List[SubClaimResult]
    ) -> Tuple[Verdict, float]:
        """Calculate overall verdict and score from sub-claims"""
        
        if not sub_results:
            return Verdict.UNVERIFIABLE, 0
        
        verdicts = [r.verdict for r in sub_results]
        
        # Count each verdict type
        true_count = verdicts.count(Verdict.TRUE)
        partial_count = verdicts.count(Verdict.PARTIALLY_TRUE)
        misleading_count = verdicts.count(Verdict.MISLEADING)
        false_count = verdicts.count(Verdict.FALSE)
        unverifiable_count = verdicts.count(Verdict.UNVERIFIABLE)
        
        total = len(verdicts)
        verifiable = total - unverifiable_count
        
        if verifiable == 0:
            return Verdict.UNVERIFIABLE, 0
        
        # Calculate score (0-100)
        score = (
            (true_count * 100) + 
            (partial_count * 60) + 
            (misleading_count * 30) + 
            (false_count * 0)
        ) / verifiable
        
        # Determine final verdict
        if false_count > 0:
            if true_count > false_count:
                return Verdict.PARTIALLY_TRUE, score
            elif misleading_count > 0:
                return Verdict.MISLEADING, score
            else:
                return Verdict.FALSE, score
        
        if misleading_count > 0:
            return Verdict.MISLEADING, score
        
        if partial_count > 0:
            return Verdict.PARTIALLY_TRUE, score
        
        if true_count == verifiable:
            return Verdict.TRUE, score
        
        return Verdict.UNVERIFIABLE, score
    
    def _generate_explanation(
        self,
        sub_results: List[SubClaimResult],
        final_verdict: Verdict,
        nutrition: Dict,
        category: str
    ) -> str:
        """Generate human-readable explanation"""
        
        parts = []
        
        # Summary
        if final_verdict == Verdict.TRUE:
            parts.append("✅ All claims verified successfully!")
        elif final_verdict == Verdict.PARTIALLY_TRUE:
            parts.append("⚠️ Some claims verified, but not all conditions are met.")
        elif final_verdict == Verdict.MISLEADING:
            parts.append("⚠️ The claims are technically misleading based on the product's nutritional profile.")
        elif final_verdict == Verdict.FALSE:
            parts.append("❌ The claims could not be verified and appear to be inaccurate.")
        else:
            parts.append("❓ Could not fully verify the claims due to missing information.")
        
        parts.append("")
        
        # Sub-claim details
        for result in sub_results:
            emoji = self._verdict_emoji(result.verdict)
            parts.append(f"{emoji} **{result.display_name}**: {result.verdict.value}")
            parts.append(f"   {result.reason}")
            parts.append("")
        
        # Nutrition summary if available
        if nutrition.get('protein_per_100g') or nutrition.get('sugar_per_100g'):
            parts.append("**Nutrition Summary (per 100g):**")
            if nutrition.get('protein_per_100g'):
                parts.append(f"• Protein: {nutrition['protein_per_100g']}g")
            if nutrition.get('sugar_per_100g'):
                parts.append(f"• Sugar: {nutrition['sugar_per_100g']}g")
            if nutrition.get('fat_per_100g'):
                parts.append(f"• Fat: {nutrition['fat_per_100g']}g")
            if nutrition.get('fiber_per_100g'):
                parts.append(f"• Fiber: {nutrition['fiber_per_100g']}g")
            if nutrition.get('calories_per_100g'):
                parts.append(f"• Calories: {nutrition['calories_per_100g']} kcal")
        
        return "\n".join(parts)
    
    def _verdict_emoji(self, verdict: Verdict) -> str:
        """Get emoji for verdict"""
        mapping = {
            Verdict.TRUE: "✅",
            Verdict.PARTIALLY_TRUE: "🟡",
            Verdict.MISLEADING: "⚠️",
            Verdict.FALSE: "❌",
            Verdict.UNVERIFIABLE: "❓"
        }
        return mapping.get(verdict, "•")
    
    def _format_success_reason(self, claim_type: str, nutrition: Dict, threshold_def: Dict) -> str:
        """Format success reason with actual values"""
        conditions = threshold_def.get('conditions', [])
        if conditions:
            cond = conditions[0]
            actual = nutrition.get(cond['nutrient'])
            return f"Product meets requirement: {actual}g per 100g (threshold: {threshold_def.get('description', '')})"
        return f"Product meets the {get_claim_description(claim_type)} requirements"
    
    def _format_failure_reason(self, claim_type: str, failed: List[Dict], threshold_def: Dict) -> str:
        """Format failure reason with actual values"""
        if failed:
            f = failed[0]
            nutrient_name = f['nutrient'].replace('_per_100g', '').replace('_', ' ').title()
            return f"{nutrient_name} is {f['actual']}g per 100g, but requirement is {threshold_def.get('description', '')}"
        return f"Product does not meet {get_claim_description(claim_type)} requirements"
    
    def _format_partial_reason(
        self, 
        claim_type: str, 
        met: int, 
        total: int, 
        failed: List[Dict]
    ) -> str:
        """Format partial success reason"""
        return f"Meets {met} of {total} conditions for {get_claim_description(claim_type)}"
    
    def _has_valid_nutrition(self, nutrition: Optional[NutritionInfo]) -> bool:
        """Check if nutrition data is valid"""
        if not nutrition:
            return False
        
        # At least one key nutrient should be present
        return any([
            nutrition.protein_per_100g is not None,
            nutrition.sugar_per_100g is not None,
            nutrition.calories_per_100g is not None
        ])
    
    def _nutrition_to_dict(self, nutrition: NutritionInfo) -> Dict:
        """Convert NutritionInfo to dictionary"""
        return {
            'protein_per_100g': nutrition.protein_per_100g,
            'sugar_per_100g': nutrition.sugar_per_100g,
            'fat_per_100g': nutrition.fat_per_100g,
            'fiber_per_100g': nutrition.fiber_per_100g,
            'calories_per_100g': nutrition.calories_per_100g,
            'sodium_per_100g': nutrition.sodium_per_100g,
        }
    
    def _create_ingredient_flags(self, ingredients: IngredientsInfo) -> Dict:
        """Create ingredient flags dictionary"""
        return {
            'has_artificial_sweetener': self.ingredients_parser.has_artificial_sweeteners(ingredients),
            'has_preservatives': self.ingredients_parser.has_preservatives(ingredients),
            'has_trans_fat': self.ingredients_parser.has_trans_fats(ingredients),
        }
    
    def _get_ingredient_warnings(self, ingredients: IngredientsInfo) -> List[str]:
        """Get list of ingredient warnings"""
        warnings = []
        
        for flagged in ingredients.flagged_ingredients:
            ingredient = flagged.get('ingredient', '').title()
            concern = flagged.get('concern', '')
            warnings.append(f"{ingredient}: {concern}")
        
        return warnings
    
    def _unverifiable_result(self, reason: str) -> VerificationResult:
        """Create an unverifiable result"""
        return VerificationResult(
            final_verdict=Verdict.UNVERIFIABLE,
            score=0,
            explanation=f"❓ {reason}",
            sub_claims=[],
            ingredient_warnings=[]
        )
