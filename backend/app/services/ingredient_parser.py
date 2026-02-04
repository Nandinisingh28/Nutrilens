"""
NutriLens Backend - Ingredient Parser Service

Parses ingredient lists from OCR text.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedIngredient:
    """Parsed ingredient with metadata."""
    name: str
    position: int
    original: str
    is_sugar_alias: bool = False
    is_additive: bool = False
    is_preservative: bool = False
    matched_rules: List[str] = field(default_factory=list)


class IngredientParser:
    """Parser for ingredient lists."""
    
    # Common ingredient section markers
    INGREDIENT_MARKERS = [
        r'ingredients?\s*:',
        r'contains?\s*:',
        r'made\s+with\s*:',
        r'composition\s*:',
    ]
    
    # Common separators
    SEPARATORS = [',', ';', '•', '·', '-']
    
    # Parenthetical ingredient patterns (e.g., "chocolate (cocoa, sugar)")
    PAREN_PATTERN = re.compile(r'\([^)]+\)')
    
    def __init__(self):
        # These will be loaded from Rule table
        self.sugar_aliases: Set[str] = set()
        self.additives: Set[str] = set()
        self.preservatives: Set[str] = set()
    
    def load_rules(self, rules: List[Dict]) -> None:
        """Load rules from database."""
        for rule in rules:
            rule_type = rule.get('rule_type')
            key = rule.get('key', '').lower()
            value = rule.get('value', {})
            
            if rule_type == 'sugar_alias':
                self.sugar_aliases.add(key)
            elif rule_type == 'additive':
                self.additives.add(key)
                if value.get('is_preservative'):
                    self.preservatives.add(key)
    
    def parse(self, text: str) -> Dict:
        """
        Parse ingredients from text.
        
        Args:
            text: OCR text containing ingredients
            
        Returns:
            Dict with parsed ingredients data
        """
        if not text:
            return self._empty_result()
        
        # Find ingredients section
        ingredients_text = self._extract_ingredients_section(text)
        
        if not ingredients_text:
            # Try parsing entire text
            ingredients_text = text
        
        # Split into individual ingredients
        raw_ingredients = self._split_ingredients(ingredients_text)
        
        # Parse and classify each ingredient
        parsed = []
        sugar_aliases_found = []
        additives_found = []
        preservatives_found = []
        
        for i, raw in enumerate(raw_ingredients):
            ingredient = self._parse_ingredient(raw, i)
            parsed.append(ingredient)
            
            if ingredient.is_sugar_alias:
                sugar_aliases_found.append(ingredient.name)
            if ingredient.is_additive:
                additives_found.append(ingredient.name)
            if ingredient.is_preservative:
                preservatives_found.append(ingredient.name)
        
        return {
            "raw_text": ingredients_text,
            "count": len(parsed),
            "list": [
                {
                    "name": p.name,
                    "position": p.position,
                    "is_sugar_alias": p.is_sugar_alias,
                    "is_additive": p.is_additive,
                    "is_preservative": p.is_preservative,
                }
                for p in parsed
            ],
            "sugar_aliases_found": sugar_aliases_found,
            "additives_found": additives_found,
            "preservatives_found": preservatives_found,
            "has_sugar_alias": len(sugar_aliases_found) > 0,
            "has_preservatives": len(preservatives_found) > 0,
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "raw_text": "",
            "count": 0,
            "list": [],
            "sugar_aliases_found": [],
            "additives_found": [],
            "preservatives_found": [],
            "has_sugar_alias": False,
            "has_preservatives": False,
        }
    
    def _extract_ingredients_section(self, text: str) -> Optional[str]:
        """Extract the ingredients section from text."""
        text_lower = text.lower()
        
        for pattern in self.INGREDIENT_MARKERS:
            match = re.search(pattern, text_lower)
            if match:
                # Get text after the marker
                start = match.end()
                remaining = text[start:]
                
                # Find end of ingredients (next section or end)
                end_markers = [
                    r'nutrition\s*facts?',
                    r'allergen',
                    r'storage',
                    r'directions',
                    r'manufactured',
                    r'best\s+before',
                    r'net\s+weight',
                    r'serving\s+size',
                    r'calories',
                ]
                
                for end_pattern in end_markers:
                    end_match = re.search(end_pattern, remaining.lower())
                    if end_match:
                        remaining = remaining[:end_match.start()]
                        break
                
                return remaining.strip()
        
        return None
    
    def _split_ingredients(self, text: str) -> List[str]:
        """Split ingredients text into individual ingredients, respecting parentheses."""
        # Normalize text: remove newline and excessive space
        text = text.replace('\n', ' ').strip()
        
        ingredients = []
        current_chunk = []
        paren_depth = 0
        
        # We split by any of the separators, but only when paren_depth is 0
        seps = set(self.SEPARATORS)
        
        for char in text:
            if char == '(':
                paren_depth += 1
                current_chunk.append(char)
            elif char == ')':
                paren_depth = max(0, paren_depth - 1)
                current_chunk.append(char)
            elif char in seps and paren_depth == 0:
                # End of an ingredient
                ing = "".join(current_chunk).strip()
                if ing:
                    ingredients.append(ing)
                current_chunk = []
            else:
                current_chunk.append(char)
                
        # Final chunk
        if current_chunk:
            ing = "".join(current_chunk).strip()
            if ing:
                ingredients.append(ing)
                
        # Post-process: handle "and" separator if not already split
        final_list = []
        for ing in ingredients:
            if ' and ' in ing.lower() and '(' not in ing:
                parts = re.split(r'\s+and\s+', ing, flags=re.IGNORECASE)
                final_list.extend([p.strip() for p in parts if p.strip()])
            else:
                final_list.append(ing)
                
        return final_list
    
    def _parse_ingredient(self, raw: str, position: int) -> ParsedIngredient:
        """Parse a single ingredient."""
        # Clean and normalize
        name = self._normalize_name(raw)
        
        # Check classifications
        name_lower = name.lower()
        
        is_sugar = any(alias in name_lower for alias in self.sugar_aliases)
        is_additive = any(add in name_lower for add in self.additives)
        is_preservative = any(pres in name_lower for pres in self.preservatives)
        
        # Also check for E-numbers (common additive codes)
        if re.search(r'\bE\d{3}\b', name, re.IGNORECASE):
            is_additive = True
        
        return ParsedIngredient(
            name=name,
            position=position,
            original=raw,
            is_sugar_alias=is_sugar,
            is_additive=is_additive,
            is_preservative=is_preservative,
        )
    
    def _normalize_name(self, name: str) -> str:
        """Normalize ingredient name by stripping noise like percentages and weights."""
        name = name.strip()
        
        # Remove trailing/embedded percentages like "(10%)" or "10%"
        name = re.sub(r'\(\s*\d+(?:\.\d+)?\s*%\s*\)', '', name)
        name = re.sub(r'\b\d+(?:\.\d+)?\s*%\s*', '', name)
        
        # Remove weights and units like (50g), 20mg, 100 g, etc.
        name = re.sub(r'\(\s*\d+(?:\.\d+)?\s*(?:g|mg|mcg|ml|oz|lb)\s*\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b\d+(?:\.\d+)?\s*(?:g|mg|mcg|ml|oz|lb)\b', '', name, flags=re.IGNORECASE)
        
        # Clean up leading/trailing punctuation left after stripping
        name = re.sub(r'^[^\w(]+|[^\w)]+$', '', name)
        
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Remove empty parentheses or parentheses with only unit names left
        name = re.sub(r'\(\s*(?:g|mg|mcg|ml|oz|lb)?\s*\)', '', name, flags=re.IGNORECASE)
        
        # Clean up leading/trailing punctuation and double whitespace again
        name = re.sub(r'^[^\w(]+|[^\w)]+$', '', name)
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()


# Singleton instance
ingredient_parser = IngredientParser()
