"""
NutriLens Backend - Parse Service

Parse nutrition facts from OCR text.
"""

import re
from typing import Optional, Dict, Any

from app.core.logging import get_logger
from app.utils.text_utils import clean_text, normalize_unit

logger = get_logger(__name__)


class ParseService:
    """Service for parsing nutrition facts from OCR text."""
    
    # Patterns for nutrition values
    PATTERNS = {
        "serving_size": r"(?:serving size|serv\.?\s*size)[:\s]*([^\n]+)",
        "servings_per_container": r"(?:servings?\s*per\s*container)[:\s]*(\d+\.?\d*)",
        "calories": r"calories[:\s]*(\d+)",
        "total_fat": r"total fat[:\s]*(\d+\.?\d*)\s*g",
        "saturated_fat": r"saturated fat[:\s]*(\d+\.?\d*)\s*g",
        "trans_fat": r"trans fat[:\s]*(\d+\.?\d*)\s*g",
        "cholesterol": r"cholesterol[:\s]*(\d+\.?\d*)\s*mg",
        "sodium": r"sodium[:\s]*(\d+\.?\d*)\s*mg",
        "total_carbs": r"(?:total )?carbohydrate[s]?[:\s]*(\d+\.?\d*)\s*g",
        "dietary_fiber": r"(?:dietary )?fiber[:\s]*(\d+\.?\d*)\s*g",
        "total_sugars": r"(?:total )?sugars?[:\s]*(\d+\.?\d*)\s*g",
        "added_sugars": r"(?:added )?sugars?[:\s]*(\d+\.?\d*)\s*g",
        "protein": r"protein[:\s]*(\d+\.?\d*)\s*g",
        "vitamin_d": r"vitamin d[:\s]*(\d+\.?\d*)",
        "calcium": r"calcium[:\s]*(\d+\.?\d*)",
        "iron": r"iron[:\s]*(\d+\.?\d*)",
        "potassium": r"potassium[:\s]*(\d+\.?\d*)",
    }
    
    async def parse_nutrition(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parse nutrition facts from OCR text.
        
        Args:
            ocr_text: Raw OCR text
        
        Returns:
            Dictionary of parsed nutrition values
        """
        if not ocr_text:
            return {}
        
        # Clean and normalize text
        text = clean_text(ocr_text.lower())
        
        nutrition = {}
        
        for field, pattern in self.PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Convert to float for numeric fields
                if field not in ["serving_size"]:
                    try:
                        nutrition[field] = float(value)
                    except ValueError:
                        nutrition[field] = value
                else:
                    nutrition[field] = value
        
        # Extract ingredients if present
        ingredients_match = re.search(
            r"ingredients?[:\s]*([^\n]+(?:\n[^\n]+)*)",
            text,
            re.IGNORECASE
        )
        if ingredients_match:
            nutrition["ingredients"] = ingredients_match.group(1).strip()
        
        # Detect allergens
        nutrition["allergens"] = self._detect_allergens(text)
        
        logger.info(f"Parsed {len(nutrition)} nutrition fields")
        
        return nutrition
    
    def _detect_allergens(self, text: str) -> list:
        """Detect common allergens in text."""
        allergens = []
        allergen_keywords = {
            "milk": ["milk", "dairy", "lactose", "whey", "casein"],
            "eggs": ["egg", "eggs", "albumin"],
            "peanuts": ["peanut", "peanuts"],
            "tree_nuts": ["almond", "cashew", "walnut", "pecan", "hazelnut", "pistachio"],
            "soy": ["soy", "soybean", "soya"],
            "wheat": ["wheat", "gluten"],
            "fish": ["fish", "cod", "salmon", "tuna"],
            "shellfish": ["shellfish", "shrimp", "crab", "lobster"],
        }
        
        for allergen, keywords in allergen_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if allergen not in allergens:
                        allergens.append(allergen)
                    break
        
        return allergens
