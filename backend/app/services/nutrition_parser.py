"""
NutriLens Backend - Nutrition Parser Service

Parses nutrition facts from OCR text.
"""

import re
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
    """Parser for nutrition facts."""
    
    # Nutrient patterns (name, possible aliases, unit)
    NUTRIENTS = [
        ("energy", ["energy", "calories", "kcal", "kj", "cal"], "kcal"),
        ("protein", ["protein", "proteins"], "g"),
        ("carbohydrates", ["carbohydrate", "carbohydrates", "carbs", "total carbs"], "g"),
        ("sugar", ["sugar", "sugars", "total sugar", "of which sugars"], "g"),
        ("fat", ["fat", "total fat", "fats"], "g"),
        ("saturated_fat", ["saturated fat", "saturated", "sat fat", "of which saturates"], "g"),
        ("fiber", ["fiber", "fibre", "dietary fiber", "dietary fibre"], "g"),
        ("sodium", ["sodium", "salt", "na"], "mg"),
        ("cholesterol", ["cholesterol"], "mg"),
    ]
    
    # Value extraction patterns
    VALUE_PATTERN = re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(g|mg|kcal|kj|%)?',
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
                
                # Find end
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
        
        # Default to per 100g
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
        """Extract a specific nutrient value."""
        text_lower = text.lower()
        
        for alias in aliases:
            # Search for the nutrient name followed by a value
            # Handle various formats: "Protein 10g", "Protein: 10 g", "Protein.....10g"
            pattern = rf'{re.escape(alias)}[\s.:]*[^\d]*(\d+(?:[.,]\d+)?)\s*(g|mg|kcal|kj|%)?'
            match = re.search(pattern, text_lower)
            
            if match:
                value_str = match.group(1).replace(',', '.')
                value = float(value_str)
                unit = match.group(2) or default_unit
                raw = match.group(0)
                
                # Convert kJ to kcal if needed
                if unit.lower() == 'kj':
                    value = value / 4.184
                    unit = 'kcal'
                
                return value, unit, raw
        
        return None, None, None
    
    def _normalize_to_100g(
        self, 
        nutrients: Dict[str, float], 
        reference: str, 
        serving_size: Optional[Dict]
    ) -> Dict[str, float]:
        """Normalize nutrient values to per 100g."""
        if reference == "100g" or reference == "100ml":
            return nutrients.copy()
        
        # If we have serving size, calculate per 100g
        if serving_size and serving_size.get("value"):
            serving_g = serving_size["value"]
            factor = 100 / serving_g
            
            return {k: round(v * factor, 2) for k, v in nutrients.items()}
        
        # Cannot normalize without serving size
        return nutrients.copy()


# Singleton instance
nutrition_parser = NutritionParser()
