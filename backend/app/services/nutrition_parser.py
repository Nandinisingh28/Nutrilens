"""
NutriLens Backend - Nutrition Parser Service

Parses nutrition facts from OCR text.
Enhanced with edge-case value handling and fuzzy name matching.
"""

import re
import difflib
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class NutrientValue:
    """Parsed nutrient value."""
    name: str
    value: float
    unit: str
    per: str  # "100g", "serving", etc.
    raw: str


class NutritionParser:
    """Parser for nutrition facts.
    
    Enhanced to handle:
    - "< 0.5", "less than 0.5", "Not more than 1.72" patterns
    - OCR-corrupted nutrient names via fuzzy matching
    - Multi-column labels (Per 100g vs Per Serve % RDA)
    """
    
    # Nutrient patterns (name, possible aliases, unit)
    NUTRIENTS = [
        ("energy", ["energy", "calories", "kcal", "kj", "cal"], "kcal"),
        ("protein", ["protein", "proteins"], "g"),
        ("carbohydrates", ["carbohydrate", "carbohydrates", "carbs", "total carbs"], "g"),
        ("sugar", ["total sugar", "total sugars", "sugar", "sugars", "of which sugars"], "g"),
        ("added_sugar", ["added sugar", "added sugars"], "g"),
        ("saturated_fat", ["saturated fat", "saturated", "sat fat", "of which saturates"], "g"),
        ("trans_fat", ["trans fat", "trans fats"], "g"),
        ("fat", ["total fat", "fat", "fats"], "g"),
        ("fiber", ["fiber", "fibre", "dietary fiber", "dietary fibre"], "g"),
        ("sodium", ["sodium", "salt", "na"], "mg"),
        ("cholesterol", ["cholesterol"], "mg"),
    ]
    
    # Fuzzy matching threshold for OCR-corrupted nutrient names
    FUZZY_THRESHOLD = 0.70
    
    # Value extraction patterns — handles normal, "less than", and "not more than"
    VALUE_PATTERN = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(g|mg|kcal|kj|%)?',
        re.IGNORECASE
    )
    
    LESS_THAN_PATTERN = re.compile(
        r'(?:less\s+than|not\s+more\s+than|<|lt)\s*(\d+(?:[.,]\d+)?)',
        re.IGNORECASE
    )
    
    # Per serving/100g patterns
    PER_PATTERNS = [
        (r'per\s*100\s*g', "100g"),
        (r'per\s*100\s*ml', "100ml"),
        (r'per\s*serving', "serving"),
        (r'per\s*pack', "pack"),
        (r'per\s*portion', "portion"),
    ]
    
    def parse(self, text: str) -> Dict:
        """
        Parse nutrition facts from text.
        
        Args:
            text: OCR text containing nutrition facts
            
        Returns:
            Dict with parsed nutrition data
        """
        if not text:
            return self._empty_result()
        
        # Find nutrition section
        nutrition_text = self._extract_nutrition_section(text)
        
        if not nutrition_text:
            nutrition_text = text
        
        # Determine reference (per 100g, per serving, etc.)
        reference = self._detect_reference(nutrition_text)
        
        # Extract serving size if present
        serving_size = self._extract_serving_size(nutrition_text)
        
        # Parse individual nutrients
        nutrients = {}
        raw_values = {}
        
        for nutrient_key, aliases, default_unit in self.NUTRIENTS:
            value, unit, raw = self._extract_nutrient(nutrition_text, aliases, default_unit)
            if value is not None:
                nutrients[nutrient_key] = value
                raw_values[nutrient_key] = {
                    "value": value,
                    "unit": unit,
                    "raw": raw,
                }
        
        # If standard extraction missed nutrients, try fuzzy matching
        if len(nutrients) < 3:
            logger.debug("Few nutrients found, trying fuzzy matching...")
            self._fuzzy_extract_nutrients(nutrition_text, nutrients, raw_values)
        
        # Normalize to per 100g if possible
        normalized = self._normalize_to_100g(nutrients, reference, serving_size)
        
        return {
            "raw_text": nutrition_text,
            "reference": reference,
            "serving_size": serving_size,
            "values": nutrients,
            "normalized_per_100g": normalized,
            "raw_values": raw_values,
            "has_values": len(nutrients) > 0,
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "raw_text": "",
            "reference": None,
            "serving_size": None,
            "values": {},
            "normalized_per_100g": {},
            "raw_values": {},
            "has_values": False,
        }
    
    def _extract_nutrition_section(self, text: str) -> Optional[str]:
        """Extract nutrition facts section."""
        text_lower = text.lower()
        
        markers = [
            r'nutrition\s*facts?',
            r'nutritional\s*information',
            r'nutrition\s*information',
            r'typical\s*values',
        ]
        
        for pattern in markers:
            match = re.search(pattern, text_lower)
            if match:
                start = match.start()
                remaining = text[start:]
                
                end_markers = [r'ingredients?:', r'allergen', r'storage', r'directions']
                for end_pattern in end_markers:
                    end_match = re.search(end_pattern, remaining.lower())
                    if end_match:
                        remaining = remaining[:end_match.start()]
                        break
                
                return remaining.strip()
        
        return None
    
    def _detect_reference(self, text: str) -> str:
        """Detect what the values are per (100g, serving, etc.)."""
        text_lower = text.lower()
        
        for pattern, ref in self.PER_PATTERNS:
            if re.search(pattern, text_lower):
                return ref
        
        return "100g"
    
    def _extract_serving_size(self, text: str) -> Optional[Dict]:
        """Extract serving size information."""
        patterns = [
            r'serving\s*size[:\s]*(\d+(?:[.,]\d+)?)\s*(g|ml)',
            r'(\d+(?:[.,]\d+)?)\s*(g|ml)\s*per\s*serving',
            r'one\s*serving[:\s]*(\d+(?:[.,]\d+)?)\s*(g|ml)',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1).replace(',', '.'))
                unit = match.group(2)
                return {"value": value, "unit": unit}
        
        return None
    
    def _extract_nutrient(
        self, 
        text: str, 
        aliases: List[str], 
        default_unit: str
    ) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        """Extract a specific nutrient value.
        
        Handles:
        - Normal values: "Protein 10g"
        - Less-than values: "Total Sugars < 0.5", "< 0.5"
        - Not-more-than values: "Not more than 1.72"
        """
        text_lower = text.lower()
        
        for alias in aliases:
            # Build a pattern to find the nutrient line
            escaped = re.escape(alias)
            # Word boundary prevents bare "fat" from matching inside "saturated fat"
            boundary = r'(?<!\w)' if len(alias) <= 4 else ''
            
            # First, try to find "less than" or "not more than" after the nutrient name
            lt_pattern = rf'{boundary}{escaped}[\s.:(]*(?:\(g\)|\(mg\))?\s*(?:less\s+than|not\s+more\s+than|<|lt)\s*(\d+(?:[.,]\d+)?)\s*(g|mg|kcal|kj|%)?'
            lt_match = re.search(lt_pattern, text_lower)
            if lt_match:
                value_str = lt_match.group(1).replace(',', '.')
                value = float(value_str)
                unit = lt_match.group(2) or default_unit
                raw = lt_match.group(0)
                return value, unit, raw
            
            # Then, try normal value extraction
            pattern = rf'{boundary}{escaped}[\s.:]*(?:\(g\)|\(mg\))?\s*[^\d]*(\d+(?:[.,]\d+)?)\s*(g|mg|kcal|kj|%)?'
            match = re.search(pattern, text_lower)
            
            if match:
                value_str = match.group(1).replace(',', '.')
                value = float(value_str)
                unit = match.group(2) or default_unit
                raw = match.group(0)
                
                # Skip if value looks like a percentage (> 100 for non-energy nutrients)
                if unit == '%' or (default_unit == 'g' and value > 200):
                    # Try next match — might have picked up the % RDA column
                    continue
                
                # Convert kJ to kcal if needed
                if unit.lower() == 'kj':
                    value = value / 4.184
                    unit = 'kcal'
                
                return value, unit, raw
        
        return None, None, None
    
    def _fuzzy_extract_nutrients(
        self, 
        text: str, 
        nutrients: Dict, 
        raw_values: Dict
    ) -> None:
        """Try fuzzy matching on each line for OCR-corrupted nutrient names."""
        lines = text.split('\n')
        
        all_aliases = {}
        for nutrient_key, aliases, default_unit in self.NUTRIENTS:
            if nutrient_key not in nutrients:
                for alias in aliases:
                    all_aliases[alias] = (nutrient_key, default_unit)
        
        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower or len(line_lower) < 3:
                continue
            
            # Get the "name" part before any numbers
            name_match = re.match(r'^([a-z\s]+)', line_lower)
            if not name_match:
                continue
            
            line_name = name_match.group(1).strip()
            if len(line_name) < 3:
                continue
            
            # Fuzzy match against all unfound aliases
            best_match = None
            best_ratio = 0
            
            for alias, (nutrient_key, default_unit) in all_aliases.items():
                ratio = difflib.SequenceMatcher(None, line_name, alias).ratio()
                if ratio > best_ratio and ratio >= self.FUZZY_THRESHOLD:
                    best_ratio = ratio
                    best_match = (nutrient_key, default_unit, alias)
            
            if best_match:
                nutrient_key, default_unit, matched_alias = best_match
                
                # Extract value from this line
                value_match = re.search(r'(\d+(?:[.,]\d+)?)', line)
                if value_match:
                    value = float(value_match.group(1).replace(',', '.'))
                    
                    # Sanity check
                    if default_unit == 'g' and value > 200:
                        continue
                    
                    nutrients[nutrient_key] = value
                    raw_values[nutrient_key] = {
                        "value": value,
                        "unit": default_unit,
                        "raw": line.strip(),
                        "fuzzy_matched": matched_alias,
                        "confidence": round(best_ratio, 2),
                    }
                    logger.debug(
                        f"Fuzzy matched '{line_name}' → '{matched_alias}' "
                        f"({best_ratio:.0%}), value={value}"
                    )
    
    def _normalize_to_100g(
        self, 
        nutrients: Dict[str, float], 
        reference: str, 
        serving_size: Optional[Dict]
    ) -> Dict[str, float]:
        """Normalize nutrient values to per 100g."""
        if reference == "100g" or reference == "100ml":
            return nutrients.copy()
        
        if serving_size and serving_size.get("value"):
            serving_g = serving_size["value"]
            factor = 100 / serving_g
            
            return {k: round(v * factor, 2) for k, v in nutrients.items()}
        
        return nutrients.copy()


# Singleton instance
nutrition_parser = NutritionParser()
