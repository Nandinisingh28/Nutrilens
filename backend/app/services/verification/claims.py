"""
Claim Type Definitions and Parsing
"""
import re
from typing import List, Tuple, Optional


# Mapping of common claim phrases to normalized claim types
CLAIM_TYPES = {
    # Protein claims
    'HIGH_PROTEIN': [
        'high protein', 'protein rich', 'protein packed', 'high in protein',
        'rich in protein', 'excellent protein', 'loaded with protein'
    ],
    'GOOD_SOURCE_OF_PROTEIN': [
        'good source of protein', 'contains protein', 'with protein',
        'source of protein', 'protein source'
    ],
    
    # Sugar claims
    'LOW_SUGAR': [
        'low sugar', 'less sugar', 'reduced sugar', 'low in sugar'
    ],
    'NO_SUGAR': [
        'no sugar', 'sugar free', 'sugarfree', 'zero sugar', '0 sugar',
        'without sugar', 'free of sugar'
    ],
    'NO_ADDED_SUGAR': [
        'no added sugar', 'no sugar added', 'without added sugar',
        'zero added sugar', 'unsweetened', 'no added sugars'
    ],
    
    # Fiber claims
    'HIGH_FIBER': [
        'high fiber', 'high fibre', 'fiber rich', 'fibre rich',
        'high in fiber', 'high in fibre', 'rich in fiber', 'rich in fibre'
    ],
    
    # Fat claims
    'LOW_FAT': [
        'low fat', 'less fat', 'reduced fat', 'fat free', 'low in fat'
    ],
    
    # Calorie claims
    'LOW_CALORIES': [
        'low calorie', 'low calories', 'low cal', 'lite', 'light',
        'reduced calories', 'fewer calories'
    ],
    
    # General health claims
    'HEALTHY': [
        'healthy', 'healthful', 'nutritious', 'wholesome', 'good for you'
    ],
    'CLEAN_INGREDIENTS': [
        'clean ingredients', 'clean label', 'simple ingredients',
        'minimal ingredients', 'clean eating'
    ],
    
    # Specific health conditions
    'DIABETIC_FRIENDLY': [
        'diabetic friendly', 'diabetes friendly', 'good for diabetics',
        'suitable for diabetics', 'diabetic safe', 'low glycemic', 'low gi'
    ],
    'WEIGHT_LOSS_FRIENDLY': [
        'weight loss', 'diet friendly', 'for weight loss', 'slimming',
        'helps lose weight', 'diet', 'weight management'
    ],
    'CHILD_FRIENDLY': [
        'child friendly', 'kid friendly', 'for kids', 'children',
        'suitable for children', 'kids', 'for children'
    ],
    'HEART_HEALTHY': [
        'heart healthy', 'good for heart', 'heart friendly',
        'cardiovascular health', 'heart health'
    ],
    
    # Natural claims
    'NATURAL': [
        'natural', 'all natural', '100% natural', 'made with natural',
        'naturally', 'nature'
    ],
    'NO_PRESERVATIVES': [
        'no preservatives', 'preservative free', 'without preservatives',
        'no artificial preservatives'
    ],
    
    # New claim types
    'LOW_SODIUM': [
        'low sodium', 'less sodium', 'low salt', 'less salt',
        'reduced sodium', 'low in sodium', 'no salt'
    ],
    'HIGH_CALCIUM': [
        'high calcium', 'rich in calcium', 'calcium rich',
        'good source of calcium', 'high in calcium', 'calcium'
    ],
    'NO_TRANS_FAT': [
        'no trans fat', 'trans fat free', 'zero trans fat',
        'without trans fat', '0 trans fat', '0g trans fat'
    ],
    'ORGANIC': [
        'organic', '100% organic', 'certified organic',
        'usda organic', 'organically grown'
    ],
    'NO_ARTIFICIAL_COLORS': [
        'no artificial colors', 'no artificial colours',
        'color free', 'without artificial colors',
        'no artificial color', 'no added colors'
    ],
    'NO_ARTIFICIAL_FLAVORS': [
        'no artificial flavors', 'no artificial flavours',
        'without artificial flavors', 'no artificial flavor',
        'no added flavors', 'natural flavors only'
    ],
    'WHOLE_GRAIN': [
        'whole grain', 'whole grains', 'whole wheat',
        'made with whole grains', '100% whole grain',
        'wholegrain', 'multigrain'
    ]
}


def normalize_claim(claim: str) -> Optional[str]:
    """
    Normalize a user claim to a standard claim type.
    
    Args:
        claim: User's claim text
        
    Returns:
        Normalized claim type or None if not recognized
    """
    claim_lower = claim.lower().strip()
    
    for claim_type, variations in CLAIM_TYPES.items():
        for variation in variations:
            if variation in claim_lower:
                return claim_type
    
    # Try fuzzy matching for common patterns
    if 'protein' in claim_lower and ('high' in claim_lower or 'rich' in claim_lower):
        return 'HIGH_PROTEIN'
    
    if 'sugar' in claim_lower and ('low' in claim_lower or 'no' in claim_lower or 'less' in claim_lower):
        if 'add' in claim_lower:
            return 'NO_ADDED_SUGAR'
        return 'LOW_SUGAR'
    
    if 'fiber' in claim_lower or 'fibre' in claim_lower:
        return 'HIGH_FIBER'
    
    if 'fat' in claim_lower and ('low' in claim_lower or 'no' in claim_lower):
        return 'LOW_FAT'
    
    if 'calorie' in claim_lower or 'cal' in claim_lower:
        return 'LOW_CALORIES'
    
    if 'sodium' in claim_lower or 'salt' in claim_lower:
        return 'LOW_SODIUM'
    
    if 'trans fat' in claim_lower:
        return 'NO_TRANS_FAT'
    
    if 'organic' in claim_lower:
        return 'ORGANIC'
    
    if 'whole grain' in claim_lower or 'whole wheat' in claim_lower:
        return 'WHOLE_GRAIN'
    
    if 'calcium' in claim_lower:
        return 'HIGH_CALCIUM'
    
    return None


def parse_compound_claim(claim: str) -> List[str]:
    """
    Parse a compound claim into individual claim types.
    
    Examples:
        "High Protein and Low Sugar" -> ['HIGH_PROTEIN', 'LOW_SUGAR']
        "Healthy, Natural, No Preservatives" -> ['HEALTHY', 'NATURAL', 'NO_PRESERVATIVES']
    
    Args:
        claim: User's compound claim text
        
    Returns:
        List of normalized claim types
    """
    claims = []
    
    # Split by common separators
    parts = re.split(r'[,&]|\band\b|\bwith\b', claim, flags=re.IGNORECASE)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        normalized = normalize_claim(part)
        if normalized and normalized not in claims:
            claims.append(normalized)
    
    # If no claims found, try to find all claims in the full text
    if not claims:
        claim_lower = claim.lower()
        for claim_type, variations in CLAIM_TYPES.items():
            for variation in variations:
                if variation in claim_lower and claim_type not in claims:
                    claims.append(claim_type)
                    break  # Only add each type once
    
    return claims


def get_claim_description(claim_type: str) -> str:
    """
    Get a human-readable description for a claim type.
    
    Args:
        claim_type: Normalized claim type
        
    Returns:
        Human-readable description
    """
    descriptions = {
        'HIGH_PROTEIN': 'High Protein',
        'GOOD_SOURCE_OF_PROTEIN': 'Good Source of Protein',
        'LOW_SUGAR': 'Low Sugar',
        'NO_SUGAR': 'No Sugar / Sugar Free',
        'NO_ADDED_SUGAR': 'No Added Sugar',
        'HIGH_FIBER': 'High Fiber',
        'LOW_FAT': 'Low Fat',
        'NO_TRANS_FAT': 'No Trans Fat',
        'LOW_CALORIES': 'Low Calories',
        'LOW_SODIUM': 'Low Sodium',
        'HIGH_CALCIUM': 'High Calcium',
        'HEALTHY': 'Healthy',
        'CLEAN_INGREDIENTS': 'Clean Ingredients',
        'DIABETIC_FRIENDLY': 'Diabetic Friendly',
        'WEIGHT_LOSS_FRIENDLY': 'Weight Loss Friendly',
        'CHILD_FRIENDLY': 'Child Friendly',
        'HEART_HEALTHY': 'Heart Healthy',
        'NATURAL': 'Natural (Partially Verifiable)',
        'ORGANIC': 'Organic (Partially Verifiable)',
        'NO_PRESERVATIVES': 'No Preservatives',
        'NO_ARTIFICIAL_COLORS': 'No Artificial Colors',
        'NO_ARTIFICIAL_FLAVORS': 'No Artificial Flavors',
        'WHOLE_GRAIN': 'Whole Grain',
    }
    
    return descriptions.get(claim_type, claim_type.replace('_', ' ').title())


def is_nutrition_dependent(claim_type: str) -> bool:
    """
    Check if a claim type depends on nutrition data.
    
    Args:
        claim_type: Normalized claim type
        
    Returns:
        True if claim requires nutrition data
    """
    nutrition_claims = {
        'HIGH_PROTEIN', 'GOOD_SOURCE_OF_PROTEIN',
        'LOW_SUGAR', 'HIGH_FIBER', 'LOW_FAT', 'LOW_CALORIES',
        'LOW_SODIUM',
        'DIABETIC_FRIENDLY', 'WEIGHT_LOSS_FRIENDLY',
        'HEALTHY', 'HEART_HEALTHY', 'CHILD_FRIENDLY'
    }
    
    return claim_type in nutrition_claims


def is_ingredient_dependent(claim_type: str) -> bool:
    """
    Check if a claim type depends on ingredient data.
    
    Args:
        claim_type: Normalized claim type
        
    Returns:
        True if claim requires ingredient data
    """
    ingredient_claims = {
        'NO_ADDED_SUGAR', 'NO_SUGAR', 'CLEAN_INGREDIENTS', 'NATURAL',
        'NO_PRESERVATIVES', 'HEALTHY', 'HEART_HEALTHY', 'CHILD_FRIENDLY',
        'NO_TRANS_FAT', 'ORGANIC', 'NO_ARTIFICIAL_COLORS',
        'NO_ARTIFICIAL_FLAVORS', 'WHOLE_GRAIN', 'HIGH_CALCIUM'
    }
    
    return claim_type in ingredient_claims
