"""
Thresholds for Claim Verification
Strict Universal FSSAI Guidelines
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClaimThreshold:
    """Threshold definition for a claim type"""
    nutrient: str
    comparison: str  # 'gte', 'lte', 'gt', 'lt'
    value: float
    unit: str
    secondary_check: str = None  # Optional secondary condition


# ══════════════════════════════════════════════════════════════════════
# Shared ingredient-only claims
# ══════════════════════════════════════════════════════════════════════

_SHARED_INGREDIENT_CLAIMS: Dict[str, Dict[str, Any]] = {
    'GLUTEN_FREE': {
        'conditions': [],
        'ingredient_check': 'gluten_free',
        'description': 'No gluten-containing ingredients'
    },
    'VEGAN': {
        'conditions': [],
        'ingredient_check': 'vegan',
        'description': 'No animal-derived ingredients'
    },
    'EGGLESS': {
        'conditions': [],
        'ingredient_check': 'eggless',
        'description': 'No egg-derived ingredients'
    },
    'NO_PRESERVATIVES': {
        'conditions': [],
        'ingredient_check': 'no_preservatives',
        'description': 'No artificial preservatives'
    },
    'NO_ARTIFICIAL_COLORS': {
        'conditions': [],
        'ingredient_check': 'no_artificial_colors',
        'description': 'No artificial colors'
    },
    'NO_ARTIFICIAL_FLAVORS': {
        'conditions': [],
        'ingredient_check': 'no_artificial_flavors',
        'description': 'No artificial flavors'
    },
    'CLEAN_INGREDIENTS': {
        'conditions': [],
        'ingredient_check': 'clean',
        'description': 'No artificial additives, preservatives, or sweeteners'
    },
    'NATURAL': {
        'conditions': [],
        'ingredient_check': 'natural',
        'description': 'No artificial ingredients'
    },
    'NO_PALM_OIL': {
        'conditions': [],
        'ingredient_check': 'no_palm_oil',
        'description': 'No palm oil'
    },
    'NO_ADDED_MSG': {
        'conditions': [],
        'ingredient_check': 'no_added_msg',
        'description': 'No added MSG'
    },
    'LACTOSE_FREE': {
        'conditions': [],
        'ingredient_check': 'lactose_free',
        'description': 'No lactose or lactose-containing ingredients'
    },
    'WHOLE_GRAIN': {
        'conditions': [],
        'ingredient_check': 'whole_grain',
        'description': 'Contains whole grain ingredients'
    },
    'WHOLE_WHEAT': {
        'conditions': [],
        'ingredient_check': 'whole_wheat',
        'description': 'Made with whole wheat'
    },
    'MULTIGRAIN': {
        'conditions': [],
        'ingredient_check': 'multigrain',
        'description': 'Made with multiple grains'
    },
    'WHEY_PROTEIN': {
        'conditions': [],
        'ingredient_check': 'whey_protein',
        'description': 'Contains whey protein'
    },
    'PLANT_PROTEIN': {
        'conditions': [],
        'ingredient_check': 'plant_protein',
        'description': 'Contains plant-based protein'
    },
    'FRUIT_100_PERCENT': {
        'conditions': [],
        'ingredient_check': 'fruit_100_percent',
        'description': '100% fruit, no artificial additives'
    },
    'ORGANIC': {
        'conditions': [],
        'ingredient_check': 'organic',
        'description': 'Organic (partially verifiable from label)'
    },
}

# ══════════════════════════════════════════════════════════════════════
# STRICT UNIVERSAL FSSAI THRESHOLDS 
# ══════════════════════════════════════════════════════════════════════

FSSAI_UNIVERSAL_THRESHOLDS = {
    'HIGH_PROTEIN': {
        'conditions': [{'nutrient': 'protein_energy_percent', 'comparison': 'gte', 'value': 20}],
        'description': 'Protein energy ≥ 20% of total energy'
    },
    'SOURCE_OF_PROTEIN': {
        'conditions': [{'nutrient': 'protein_energy_percent', 'comparison': 'gte', 'value': 12}],
        'description': 'Protein energy ≥ 12% of total energy'
    },
    'HIGH_FIBER': {
        'conditions': [{'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 6}],
        'description': 'Fiber ≥ 6g'
    },
    'SOURCE_OF_FIBER': {
        'conditions': [{'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 3}],
        'description': 'Fiber ≥ 3g'
    },
    'LOW_FAT': {
        'conditions': [{'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 3}],
        'description': 'Fat ≤ 3g'
    },
    'FAT_FREE': {
        'conditions': [{'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 0.5}],
        'description': 'Fat ≤ 0.5g'
    },
    'LOW_SATURATED_FAT': {
        'conditions': [{'nutrient': 'saturated_fat_per_100g', 'comparison': 'lte', 'value': 1.5}],
        'description': 'Saturated fat ≤ 1.5g'
    },
    'SATURATED_FAT_FREE': {
        'conditions': [{'nutrient': 'saturated_fat_per_100g', 'comparison': 'lte', 'value': 0.1}],
        'description': 'Saturated fat ≤ 0.1g'
    },
    'TRANS_FAT_FREE': {
        'conditions': [{'nutrient': 'trans_fat_per_100g', 'comparison': 'lte', 'value': 0.2}],
        'ingredient_check': 'no_trans_fat',
        'description': 'Trans fat ≤ 0.2g and no trans fat ingredients'
    },
    'SUGAR_FREE': {
        'conditions': [{'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 0.5}],
        'ingredient_check': 'no_sugar',
        'description': 'Sugar ≤ 0.5g and no sugar ingredients'
    },
    'NO_ADDED_SUGAR': {
        'conditions': [],
        'ingredient_check': 'no_added_sugar',
        'description': 'No added sugar ingredients (sugar, honey, syrup, etc.)'
    },
    'LOW_ENERGY': {
        'conditions': [{'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 40}],
        'description': 'Energy ≤ 40 kcal'
    },
    'ENERGY_FREE': {
        'conditions': [{'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 4}],
        'description': 'Energy ≤ 4 kcal'
    },
    'CHOLESTEROL_FREE': {
        'conditions': [{'nutrient': 'cholesterol_per_100g', 'comparison': 'lte', 'value': 2}],
        'ingredient_check': 'cholesterol_free',
        'description': 'Cholesterol ≤ 2mg and no cholesterol ingredients'
    },
    'LOW_CHOLESTEROL': {
        'conditions': [{'nutrient': 'cholesterol_per_100g', 'comparison': 'lte', 'value': 20}],
        'description': 'Cholesterol ≤ 20mg'
    },
    
    # Legacy fallbacks for compound claims that might still be used
    'HEALTHY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 15},
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 15},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 3}
        ],
        'ingredient_check': 'no_trans_fat',
        'description': 'Balanced nutritional profile with no harmful ingredients'
    },
    'DIABETIC_FRIENDLY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 5},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 3}
        ],
        'description': 'Low sugar with good fiber content'
    },
    'WEIGHT_LOSS_FRIENDLY': {
        'conditions': [
            {'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 350},
            {'nutrient': 'protein_energy_percent', 'comparison': 'gte', 'value': 15},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 4}
        ],
        'description': 'High protein, high fiber, moderate calories'
    },
    'HEART_HEALTHY': {
        'conditions': [
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 12},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 3}
        ],
        'ingredient_check': 'no_trans_fat',
        'description': 'Low saturated fat, no trans fat, good fiber'
    },
    'CHILD_FRIENDLY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 12},
            {'nutrient': 'protein_energy_percent', 'comparison': 'gte', 'value': 5}
        ],
        'ingredient_check': 'no_artificial',
        'description': 'Moderate sugar, adequate protein, no artificial additives'
    },
    'LOW_SUGAR': {
        'conditions': [{'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 5}],
        'description': 'Sugar ≤ 5g per 100g'
    },
}

# Merge them all into a single dictionary
UNIVERSAL_THRESHOLDS = dict(_SHARED_INGREDIENT_CLAIMS)
UNIVERSAL_THRESHOLDS.update(FSSAI_UNIVERSAL_THRESHOLDS)


def _build_thresholds_from_db(db, category: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Build the thresholds dictionary from ClaimRule rows in the DB.
    Returns None if no rows are found (caller should use fallback).
    """
    try:
        from app.models.rules import ClaimRule
        rows = db.query(ClaimRule).filter(ClaimRule.category == category).all()
        if not rows:
            return None

        thresholds: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            ct = row.claim_type
            if ct not in thresholds:
                thresholds[ct] = {
                    'conditions': [],
                    'description': row.description or '',
                }
                if row.requires_ingredient_check and row.ingredient_check_type:
                    thresholds[ct]['ingredient_check'] = row.ingredient_check_type

            if row.nutrient and row.operator and row.threshold is not None:
                thresholds[ct]['conditions'].append({
                    'nutrient': row.nutrient,
                    'comparison': row.operator,
                    'value': row.threshold,
                })
        return thresholds
    except Exception as e:
        logger.warning(f"Failed to load thresholds from DB: {e}")
        return None


def get_thresholds(category: str, db=None) -> Dict[str, Dict[str, Any]]:
    """
    Get strict universal FSSAI thresholds (ignoring legacy category logic).
    
    Priority:
      1. Database (ClaimRule table)
      2. Universal fallback (FSSAI)
    """
    category_upper = category.upper().replace(' ', '_')

    # Try database first
    if db is not None:
        db_thresholds = _build_thresholds_from_db(db, category_upper)
        if db_thresholds:
            return db_thresholds

    # Strict Universal FSSAI rules
    return UNIVERSAL_THRESHOLDS


def evaluate_condition(
    nutrition: dict,
    nutrient: str,
    comparison: str,
    value: float
) -> bool:
    """Evaluate a single nutritional condition."""
    actual = nutrition.get(nutrient)
    
    if actual is None:
        return False
    
    if comparison == 'gte':
        return actual >= value
    elif comparison == 'lte':
        return actual <= value
    elif comparison == 'gt':
        return actual > value
    elif comparison == 'lt':
        return actual < value
    elif comparison == 'eq':
        return actual == value
    else:
        return False
