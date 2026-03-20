"""
Parsers for Nutrition and Ingredients Data
Enhanced with debug logging and more lenient pattern matching
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import difflib

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class NutritionInfo:
    """Structured nutrition information"""
    serving_size: Optional[str] = None
    protein_per_100g: Optional[float] = None
    sugar_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    calories_per_100g: Optional[float] = None
    sodium_per_100g: Optional[float] = None
    carbohydrates_per_100g: Optional[float] = None
    saturated_fat_per_100g: Optional[float] = None
    trans_fat_per_100g: Optional[float] = None
    cholesterol_per_100g: Optional[float] = None
    raw_text: str = ""
    debug_matches: Dict = None
    
    def __post_init__(self):
        if self.debug_matches is None:
            self.debug_matches = {}


@dataclass  
class IngredientsInfo:
    """Structured ingredients information"""
    ingredients_list: List[str] = None
    flagged_ingredients: List[Dict[str, str]] = None
    allergens_detected: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.ingredients_list is None:
            self.ingredients_list = []
        if self.flagged_ingredients is None:
            self.flagged_ingredients = []
        if self.allergens_detected is None:
            self.allergens_detected = []


class NutritionParser:
    """
    Parses nutrition information from OCR text.
    Enhanced with more lenient patterns for OCR errors.
    """
    
    # More lenient patterns (handles OCR errors, spacing issues, etc.)
    PATTERNS = {
        'protein': [
            r'protein[:\s]*(\d+\.?\d*)\s*g',
            r'protein[:\s]*(\d+\.?\d*)',
            r'protein\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'prot[e3]in[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*protein',
            r'प्रोटीन[:\s]*(\d+\.?\d*)',
        ],
        'sugar': [
            r'(?:total|added\s+)?sugar[s]?[:\s]*(\d+\.?\d*)\s*g',
            r'(?:total|added\s+)?sugar[s]?\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'sugar[s]?[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*sugar',
            r'sug[a4]r[:\s]*(\d+\.?\d*)',
            r'शक्कर[:\s]*(\d+\.?\d*)',
        ],
        'fat': [
            r'(?:total\s+)?fat[:\s]*(\d+\.?\d*)\s*g',
            r'(?:total\s+)?fat\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'(?<!saturated\s)(?<!unsaturated\s)(?<!trans\s)fat[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*(?:total\s+)?fat(?!ty)',
            r'f[a4]t[:\s]*(\d+\.?\d*)',
            r'वसा[:\s]*(\d+\.?\d*)',
        ],
        'fiber': [
            r'(?:dietary\s+)?fib(?:re|er)[:\s]*(\d+\.?\d*)\s*g',
            r'(?:dietary\s+)?fib(?:re|er)\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'fib(?:re|er)[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*fib(?:re|er)',
            r'fibre?[:\s]*(\d+\.?\d*)',
            r'फाइबर[:\s]*(\d+\.?\d*)',
        ],
        'calories': [
            r'(?:energy|calories?)[:\s]*(\d+\.?\d*)\s*(?:kcal|cal)',
            r'(?:energy|calories?)\s*(?:\(kcal\)|\(cal\))?[:\s]*(\d+\.?\d*)',
            r'(?:energy|calories?)[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:kcal|cal)',
            r'(\d+\.?\d*)\s*calories?',
            r'kcal[:\s]*(\d+\.?\d*)',
            r'cal[:\s]*(\d+\.?\d*)',
            r'ऊर्जा[:\s]*(\d+\.?\d*)',
        ],
        'sodium': [
            r'sodium[:\s]*(\d+\.?\d*)\s*mg',
            r'sodium\s*(?:\(mg\))?[:\s]*(\d+\.?\d*)',
            r'sodium[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*mg?\s*sodium',
            r'salt\s*(?:\(g\)|\(mg\))?[:\s]*(\d+\.?\d*)',
            r'सोडियम[:\s]*(\d+\.?\d*)',
        ],
        'carbohydrates': [
            r'(?:total\s+)?carbohydrate[s]?[:\s]*(\d+\.?\d*)\s*g',
            r'(?:total\s+)?carbohydrate[s]?\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'carbohydrate[s]?[:\s]*(\d+\.?\d*)',
            r'carbs?\s*(?:\(g\))?[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*carb',
            r'कार्बोहाइड्रेट[:\s]*(\d+\.?\d*)',
        ],
        'saturated_fat': [
            r'saturated\s+fat(?:ty)?\s*(?:acids?)?[:\s]*(\d+\.?\d*)\s*g',
            r'saturated\s+fat(?:ty)?\s*(?:acids?)?[:\s]*(\d+\.?\d*)',
            r'sat(?:urated)?\s*fat[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*sat\s*fat',
        ],
        'trans_fat': [
            r'trans\s+fat(?:ty)?\s*(?:acids?)?[:\s]*(\d+\.?\d*)\s*g',
            r'trans\s+fat(?:ty)?\s*(?:acids?)?[:\s]*(\d+\.?\d*)',
            r'trans\s*fat[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*g?\s*trans\s*fat',
        ],
        'cholesterol': [
            r'cholesterol[:\s]*(\d+\.?\d*)\s*mg',
            r'cholesterol[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*mg?\s*cholesterol',
        ],
        'serving_size': [
            r'serving\s*(?:size)?[:\s]*(\d+\.?\d*\s*(?:g|ml|gm))',
            r'per\s+(\d+\.?\d*\s*(?:g|ml|gm))',
            r'(\d+\.?\d*)\s*(?:g|gm)\s*(?:per\s+serving|serving)',
            r'per\s+serve?[:\s]*(\d+\.?\d*)',
        ],
    }
    
    # Per serving to per 100g conversion
    STANDARD_SERVING_SIZES = {
        'protein_bar': 40,
        'breakfast_cereal': 30,
    }
    
    def parse(self, text: str, category: str = None) -> NutritionInfo:
        """Parse nutrition text into structured data with debug info"""
        text_lower = text.lower()
        
        # --- OCR Error Tolerance (Sanitization) ---
        # Common issue: OCR reads "0g" as "og" and "0mg" as "omg"
        # We selectively replace isolated "omg" and "og" when they appear next to numbers or as values
        text_lower = re.sub(r'\b[oO]\s*mg\b', '0mg', text_lower)
        text_lower = re.sub(r'\b[oO]\s*g\b', '0g', text_lower)
        
        debug_matches = {}
        
        logger.debug(f"Parsing nutrition from text ({len(text_lower)} chars): {text_lower[:500]}...")
        
        # Extract serving size
        serving_size = self._extract_value('serving_size', text_lower)
        serving_g = self._parse_serving_size(serving_size)
        debug_matches['serving_size'] = {'value': serving_size, 'grams': serving_g}
        
        # If no serving size found, use category default
        if serving_g is None and category:
            category_key = category.lower().replace(' ', '_')
            serving_g = self.STANDARD_SERVING_SIZES.get(category_key, 100)
        elif serving_g is None:
            serving_g = 100
        
        # Determine if values are per serving or per 100g
        is_per_100g = 'per 100' in text_lower or 'per100' in text_lower or '100g' in text_lower
        debug_matches['is_per_100g'] = is_per_100g
        
        # Extract values with debug
        protein = self._extract_numeric_with_debug('protein', text_lower, debug_matches)
        sugar = self._extract_numeric_with_debug('sugar', text_lower, debug_matches)
        fat = self._extract_numeric_with_debug('fat', text_lower, debug_matches)
        fiber = self._extract_numeric_with_debug('fiber', text_lower, debug_matches)
        calories = self._extract_numeric_with_debug('calories', text_lower, debug_matches)
        sodium = self._extract_numeric_with_debug('sodium', text_lower, debug_matches)
        carbs = self._extract_numeric_with_debug('carbohydrates', text_lower, debug_matches)
        sat_fat = self._extract_numeric_with_debug('saturated_fat', text_lower, debug_matches)
        trans_fat = self._extract_numeric_with_debug('trans_fat', text_lower, debug_matches)
        cholesterol = self._extract_numeric_with_debug('cholesterol', text_lower, debug_matches)
        
        # Convert to per 100g if needed
        if not is_per_100g and serving_g != 100:
            factor = 100 / serving_g
            protein = protein * factor if protein is not None else None
            sugar = sugar * factor if sugar is not None else None
            fat = fat * factor if fat is not None else None
            fiber = fiber * factor if fiber is not None else None
            calories = calories * factor if calories is not None else None
            carbs = carbs * factor if carbs is not None else None
            sodium = sodium * factor if sodium is not None else None
            sat_fat = sat_fat * factor if sat_fat is not None else None
            trans_fat = trans_fat * factor if trans_fat is not None else None
            cholesterol = cholesterol * factor if cholesterol is not None else None
            debug_matches['conversion_factor'] = factor
        
        result = NutritionInfo(
            serving_size=serving_size,
            protein_per_100g=round(protein, 1) if protein is not None else None,
            sugar_per_100g=round(sugar, 1) if sugar is not None else None,
            fat_per_100g=round(fat, 1) if fat is not None else None,
            fiber_per_100g=round(fiber, 1) if fiber is not None else None,
            calories_per_100g=round(calories, 1) if calories is not None else None,
            sodium_per_100g=round(sodium, 1) if sodium is not None else None,
            carbohydrates_per_100g=round(carbs, 1) if carbs is not None else None,
            saturated_fat_per_100g=round(sat_fat, 1) if sat_fat is not None else None,
            trans_fat_per_100g=round(trans_fat, 1) if trans_fat is not None else None,
            cholesterol_per_100g=round(cholesterol, 1) if cholesterol is not None else None,
            raw_text=text,
            debug_matches=debug_matches
        )
        
        logger.info(f"Parsed nutrition: protein={result.protein_per_100g}, "
                   f"sugar={result.sugar_per_100g}, fat={result.fat_per_100g}, "
                   f"calories={result.calories_per_100g}")
        
        return result
    
    def _extract_value(self, key: str, text: str) -> Optional[str]:
        """Extract string value using patterns"""
        for pattern in self.PATTERNS.get(key, []):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None
    
    def _extract_numeric_with_debug(self, key: str, text: str, debug_dict: Dict) -> Optional[float]:
        """Extract numeric value with debug info"""
        for pattern in self.PATTERNS.get(key, []):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1) if match.groups() else match.group(0)
                try:
                    numeric = re.search(r'(\d+\.?\d*)', value_str)
                    if numeric:
                        value = float(numeric.group(1))
                        debug_dict[key] = {
                            'pattern': pattern,
                            'match': match.group(0),
                            'value': value
                        }
                        return value
                except ValueError:
                    pass
        
        debug_dict[key] = {'found': False}
        return None
    
    def _extract_numeric(self, key: str, text: str) -> Optional[float]:
        """Extract numeric value using patterns"""
        value_str = self._extract_value(key, text)
        if value_str:
            try:
                numeric = re.search(r'(\d+\.?\d*)', value_str)
                if numeric:
                    return float(numeric.group(1))
            except ValueError:
                pass
        return None
    
    def _parse_serving_size(self, serving_str: Optional[str]) -> Optional[float]:
        """Parse serving size string to grams"""
        if not serving_str:
            return None
        
        try:
            numeric = re.search(r'(\d+\.?\d*)', serving_str)
            if numeric:
                return float(numeric.group(1))
        except ValueError:
            pass
        
        return None


class IngredientsParser:
    """
    Parses ingredients list from OCR text.
    Identifies and flags concerning ingredients.
    Detects common allergens.
    Loads flagged ingredients from DB (IngredientRiskMaster) if available,
    otherwise uses hardcoded defaults.
    """
    
    # Hardcoded fallback list
    _DEFAULT_FLAGGED = {
        'aspartame': {'category': 'artificial_sweetener', 'concern': 'Controversial artificial sweetener'},
        'sucralose': {'category': 'artificial_sweetener', 'concern': 'Artificial sweetener'},
        'stevia': {'category': 'artificial_sweetener', 'concern': 'Natural zero-calorie sweetener'},
        'saccharin': {'category': 'artificial_sweetener', 'concern': 'Artificial sweetener'},
        'acesulfame': {'category': 'artificial_sweetener', 'concern': 'Artificial sweetener'},
        'high fructose corn syrup': {'category': 'added_sugar', 'concern': 'High fructose corn syrup'},
        'hfcs': {'category': 'added_sugar', 'concern': 'High fructose corn syrup'},
        'corn syrup': {'category': 'added_sugar', 'concern': 'Added sugar'},
        'maltodextrin': {'category': 'added_sugar', 'concern': 'High glycemic ingredient'},
        'sodium benzoate': {'category': 'preservative', 'concern': 'Common preservative'},
        'potassium sorbate': {'category': 'preservative', 'concern': 'Common preservative'},
        'bha': {'category': 'preservative', 'concern': 'Controversial preservative'},
        'bht': {'category': 'preservative', 'concern': 'Controversial preservative'},
        'red 40': {'category': 'artificial_color', 'concern': 'Artificial color'},
        'yellow 5': {'category': 'artificial_color', 'concern': 'Artificial color'},
        'tartrazine': {'category': 'artificial_color', 'concern': 'Artificial color (E102)'},
        'partially hydrogenated': {'category': 'trans_fat', 'concern': 'Contains trans fats'},
        'monosodium glutamate': {'category': 'flavor_enhancer', 'concern': 'Flavor enhancer (MSG)'},
        'msg': {'category': 'flavor_enhancer', 'concern': 'Flavor enhancer (MSG)'},
    }
    
    # Common allergen keywords for detection
    ALLERGEN_KEYWORDS = [
        'milk', 'eggs', 'egg', 'fish', 'shellfish', 'tree nuts', 'peanuts',
        'peanut', 'wheat', 'soybeans', 'soy', 'gluten', 'sesame', 'mustard',
        'celery', 'lupin'
    ]
    
    # Normalize allergen names for cleaner output
    _ALLERGEN_NORMALIZE = {
        'egg': 'eggs',
        'soybeans': 'soy',
        'peanut': 'peanuts',
    }
    
    def __init__(self, db=None):
        self.FLAGGED_INGREDIENTS = self._load_flagged(db)
    
    def _load_flagged(self, db) -> dict:
        """Load flagged ingredients from DB; fall back to hardcoded defaults."""
        if db is None:
            return dict(self._DEFAULT_FLAGGED)
        try:
            from app.models.rules import IngredientRiskMaster
            rows = db.query(IngredientRiskMaster).all()
            if not rows:
                return dict(self._DEFAULT_FLAGGED)
            result = {}
            for row in rows:
                result[row.ingredient_name.lower()] = {
                    'category': row.category,
                    'concern': row.description or '',
                    'risk_level': row.risk_level.value if row.risk_level else 'MEDIUM',
                }
            return result
        except Exception as e:
            logger.warning(f"Failed to load ingredient risks from DB: {e}")
            return dict(self._DEFAULT_FLAGGED)
    
    def parse(self, text: str) -> IngredientsInfo:
        """Parse ingredients text into structured data with allergen detection"""
        logger.debug(f"Parsing ingredients from text ({len(text)} chars): {text[:300]}...")
        
        cleaned = self._clean_text(text)
        ingredients_list = self._extract_ingredients_list(cleaned)
        flagged = self._flag_ingredients(ingredients_list, cleaned)
        allergens = self._detect_allergens(cleaned)
        
        logger.info(f"Parsed {len(ingredients_list)} ingredients, {len(flagged)} flagged, "
                   f"{len(allergens)} allergens detected")
        
        return IngredientsInfo(
            ingredients_list=ingredients_list,
            flagged_ingredients=flagged,
            allergens_detected=allergens,
            raw_text=text
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize ingredients text"""
        text = re.sub(r'^.*?ingredients?\s*:?\s*', '', text, flags=re.IGNORECASE)
        text = text.replace('|', 'I')
        return text.strip()
    
    def _extract_ingredients_list(self, text: str) -> List[str]:
        """Extract individual ingredients from text"""
        items = re.split(r'[,;]', text)
        
        ingredients = []
        for item in items:
            cleaned = item.strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            if 2 < len(cleaned) < 100:
                cleaned = cleaned.rstrip('.')
                ingredients.append(cleaned)
        
        return ingredients
    
    
    def _flag_ingredients(self, ingredients_list: List[str], full_text: str) -> List[Dict[str, str]]:
        """Identify and flag concerning ingredients with fuzzy matching"""
        flagged = []
        text_lower = full_text.lower()
        
        # Check exact matches first (faster)
        for ingredient_key, info in self.FLAGGED_INGREDIENTS.items():
            if ingredient_key in text_lower:
                flagged.append({
                    'ingredient': ingredient_key,
                    'category': info['category'],
                    'concern': info['concern']
                })
                continue
                
            # Fuzzy match if exact match not found
            # Check against each extracted ingredient item
            for item in ingredients_list:
                item_lower = item.lower()
                # Skip very short items to avoid false positives
                if len(item_lower) < 4:
                    continue
                    
                # Calculate similarity
                ratio = difflib.SequenceMatcher(None, ingredient_key, item_lower).ratio()
                
                # If > 85% similarity, flag it
                # OR if the key is contained in the item with high similarity (e.g. "pure sucralose")
                if ratio > 0.85:
                    flagged.append({
                        'ingredient': ingredient_key,
                        'category': info['category'],
                        'concern': info['concern'] + f" (detected as '{item}')"
                    })
                    break
        
        return flagged
    
    def has_added_sugar(self, ingredients_info: IngredientsInfo) -> bool:
        """Check if product has added sugars"""
        added_sugar_terms = [
            'sugar', 'sucrose', 'glucose', 'fructose', 'dextrose',
            'corn syrup', 'high fructose', 'maltose', 'syrup',
            'molasses', 'honey', 'jaggery'
        ]
        
        text_lower = ingredients_info.raw_text.lower()
        return any(term in text_lower for term in added_sugar_terms)
    
    def has_artificial_sweeteners(self, ingredients_info: IngredientsInfo) -> bool:
        """Check for artificial sweeteners"""
        return any(
            f['category'] == 'artificial_sweetener' 
            for f in ingredients_info.flagged_ingredients
        )
    
    def has_preservatives(self, ingredients_info: IngredientsInfo) -> bool:
        """Check for preservatives"""
        return any(
            f['category'] == 'preservative'
            for f in ingredients_info.flagged_ingredients
        )
    
    def has_trans_fats(self, ingredients_info: IngredientsInfo) -> bool:
        """Check for trans fats"""
        return any(
            f['category'] == 'trans_fat'
            for f in ingredients_info.flagged_ingredients
        )
    
    def count_concerning_ingredients(self, ingredients_info: IngredientsInfo) -> int:
        """Count total concerning ingredients"""
        return len(ingredients_info.flagged_ingredients)
    
    def _detect_allergens(self, text: str) -> List[str]:
        """
        Detect common allergens in ingredients text.
        
        Checks for: milk, eggs, fish, shellfish, tree nuts, peanuts,
        wheat, soy, gluten, sesame, mustard, celery, lupin.
        
        Returns:
            List of normalized allergen names found
        """
        detected = set()
        text_lower = text.lower()
        
        for allergen in self.ALLERGEN_KEYWORDS:
            if allergen in text_lower:
                # Normalize to canonical name
                normalized = self._ALLERGEN_NORMALIZE.get(allergen, allergen)
                detected.add(normalized)
        
        return sorted(detected)
