"""
Thresholds for Claim Verification
Loads rules from database (ClaimRule table), falls back to hardcoded defaults.
Based on FSSAI (Food Safety and Standards Authority of India) guidelines.
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


# ── Hardcoded fallback thresholds (original 2 categories) ────────────────

# Protein Bar Thresholds (per 100g unless specified)
PROTEIN_BAR_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    'HIGH_PROTEIN': {
        'conditions': [
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 20}
        ],
        'description': 'At least 20g protein per 100g'
    },
    'GOOD_SOURCE_OF_PROTEIN': {
        'conditions': [
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 10}
        ],
        'description': 'At least 10g protein per 100g'
    },
    'LOW_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 5}
        ],
        'description': 'Not more than 5g sugar per 100g'
    },
    'NO_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 0.5}
        ],
        'ingredient_check': 'no_sugar',
        'description': 'Less than 0.5g sugar and no sugar ingredients'
    },
    'NO_ADDED_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 5}
        ],
        'ingredient_check': 'no_added_sugar',
        'description': 'No added sugars in ingredients'
    },
    'HIGH_FIBER': {
        'conditions': [
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 6}
        ],
        'description': 'At least 6g fiber per 100g'
    },
    'LOW_FAT': {
        'conditions': [
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 3}
        ],
        'description': 'Not more than 3g fat per 100g'
    },
    'LOW_CALORIES': {
        'conditions': [
            {'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 250}
        ],
        'description': 'Not more than 250 kcal per 100g'
    },
    'HEALTHY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 15},
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 15},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 3}
        ],
        'ingredient_check': 'no_trans_fat',
        'description': 'Balanced nutritional profile with no harmful ingredients'
    },
    'CLEAN_INGREDIENTS': {
        'conditions': [],
        'ingredient_check': 'clean',
        'description': 'No artificial additives, preservatives, or sweeteners'
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
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 15},
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
    'NATURAL': {
        'conditions': [],
        'ingredient_check': 'natural',
        'description': 'No artificial ingredients'
    },
    'NO_PRESERVATIVES': {
        'conditions': [],
        'ingredient_check': 'no_preservatives',
        'description': 'No artificial preservatives'
    },
    'CHILD_FRIENDLY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 12},
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 5}
        ],
        'ingredient_check': 'no_artificial',
        'description': 'Moderate sugar, adequate protein, no artificial additives'
    }
}

# Breakfast Cereal Thresholds (per 100g unless specified)
CEREAL_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    'HIGH_PROTEIN': {
        'conditions': [
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 10}
        ],
        'description': 'At least 10g protein per 100g'
    },
    'GOOD_SOURCE_OF_PROTEIN': {
        'conditions': [
            {'nutrient': 'protein_per_100g', 'comparison': 'gte', 'value': 6}
        ],
        'description': 'At least 6g protein per 100g'
    },
    'LOW_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 10}
        ],
        'description': 'Not more than 10g sugar per 100g'
    },
    'NO_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 0.5}
        ],
        'ingredient_check': 'no_sugar',
        'description': 'Less than 0.5g sugar and no sugar ingredients'
    },
    'NO_ADDED_SUGAR': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 5}
        ],
        'ingredient_check': 'no_added_sugar',
        'description': 'No added sugars in ingredients'
    },
    'HIGH_FIBER': {
        'conditions': [
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 6}
        ],
        'description': 'At least 6g fiber per 100g'
    },
    'LOW_FAT': {
        'conditions': [
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 3}
        ],
        'description': 'Not more than 3g fat per 100g'
    },
    'LOW_CALORIES': {
        'conditions': [
            {'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 380}
        ],
        'description': 'Not more than 380 kcal per 100g'
    },
    'HEALTHY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 15},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 4}
        ],
        'ingredient_check': 'no_trans_fat',
        'description': 'Balanced nutritional profile'
    },
    'CLEAN_INGREDIENTS': {
        'conditions': [],
        'ingredient_check': 'clean',
        'description': 'No artificial additives'
    },
    'DIABETIC_FRIENDLY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 8},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 5}
        ],
        'description': 'Low sugar with high fiber'
    },
    'WEIGHT_LOSS_FRIENDLY': {
        'conditions': [
            {'nutrient': 'calories_per_100g', 'comparison': 'lte', 'value': 380},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 6}
        ],
        'description': 'High fiber, moderate calories'
    },
    'HEART_HEALTHY': {
        'conditions': [
            {'nutrient': 'fat_per_100g', 'comparison': 'lte', 'value': 5},
            {'nutrient': 'fiber_per_100g', 'comparison': 'gte', 'value': 5}
        ],
        'ingredient_check': 'no_trans_fat',
        'description': 'Low fat, high fiber, no trans fat'
    },
    'NATURAL': {
        'conditions': [],
        'ingredient_check': 'natural',
        'description': 'No artificial ingredients'
    },
    'NO_PRESERVATIVES': {
        'conditions': [],
        'ingredient_check': 'no_preservatives',
        'description': 'No artificial preservatives'
    },
    'CHILD_FRIENDLY': {
        'conditions': [
            {'nutrient': 'sugar_per_100g', 'comparison': 'lte', 'value': 15}
        ],
        'ingredient_check': 'no_artificial',
        'description': 'Moderate sugar, no artificial additives'
    }
}

# Hardcoded fallback mapping
_HARDCODED_THRESHOLDS = {
    'PROTEIN_BAR': PROTEIN_BAR_THRESHOLDS,
    'BREAKFAST_CEREAL': CEREAL_THRESHOLDS,
}


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
    Get thresholds for a specific product category.
    
    Priority:
      1. Database (ClaimRule table) — works for all 12 categories
      2. Hardcoded fallback — for PROTEIN_BAR and BREAKFAST_CEREAL only
      3. Protein bar defaults as last resort

    Args:
        category: Product category string
        db: Optional SQLAlchemy Session for DB-backed lookup
        
    Returns:
        Dictionary of claim thresholds
    """
    category_upper = category.upper().replace(' ', '_')

    # Try database first
    if db is not None:
        db_thresholds = _build_thresholds_from_db(db, category_upper)
        if db_thresholds:
            return db_thresholds

    # Hardcoded fallback
    return _HARDCODED_THRESHOLDS.get(category_upper, PROTEIN_BAR_THRESHOLDS)


def evaluate_condition(
    nutrition: dict,
    nutrient: str,
    comparison: str,
    value: float
) -> bool:
    """
    Evaluate a single nutritional condition.
    
    Args:
        nutrition: Dictionary with nutrition values
        nutrient: Key for the nutrient to check
        comparison: Comparison operator
        value: Threshold value
        
    Returns:
        True if condition is met
    """
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
