
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

@dataclass
class ParsedIngredient:
    name: str
    position: int
    original: str
    is_sugar_alias: bool = False
    is_additive: bool = False
    is_preservative: bool = False

class IngredientParser:
    INGREDIENT_MARKERS = [
        r'ingredients?\s*:',
        r'contains?\s*:',
        r'made\s+with\s*:',
        r'composition\s*:',
    ]
    
    SEPARATORS = [',', ';', '•', '·', '-']
    
    def __init__(self):
        self.sugar_aliases = set()
        self.additives = set()
        self.preservatives = set()

    def parse(self, text: str) -> Dict:
        ingredients_text = self._extract_ingredients_section(text)
        if not ingredients_text:
            ingredients_text = text
        
        raw_ingredients = self._split_ingredients(ingredients_text)
        parsed = []
        for i, raw in enumerate(raw_ingredients):
            name = self._normalize_name(raw)
            parsed.append({
                "name": name,
                "position": i,
                "original": raw
            })
        
        return {
            "raw_text": ingredients_text,
            "count": len(parsed),
            "list": parsed
        }

    def _extract_ingredients_section(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for pattern in self.INGREDIENT_MARKERS:
            match = re.search(pattern, text_lower)
            if match:
                start = match.end()
                remaining = text[start:]
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
        text = text.replace('\n', ' ').strip()
        ingredients = []
        current_chunk = []
        paren_depth = 0
        seps = set(self.SEPARATORS)
        
        for char in text:
            if char == '(':
                paren_depth += 1
                current_chunk.append(char)
            elif char == ')':
                paren_depth = max(0, paren_depth - 1)
                current_chunk.append(char)
            elif char in seps and paren_depth == 0:
                ing = "".join(current_chunk).strip()
                if ing:
                    ingredients.append(ing)
                current_chunk = []
            else:
                current_chunk.append(char)
                
        if current_chunk:
            ing = "".join(current_chunk).strip()
            if ing:
                ingredients.append(ing)
                
        final_list = []
        for ing in ingredients:
            if ' and ' in ing.lower() and '(' not in ing:
                parts = re.split(r'\s+and\s+', ing, flags=re.IGNORECASE)
                final_list.extend([p.strip() for p in parts if p.strip()])
            else:
                final_list.append(ing)
        return final_list

    def _normalize_name(self, name: str) -> str:
        name = name.strip()
        # Percentages
        name = re.sub(r'\(\s*\d+(?:\.\d+)?\s*%\s*\)', '', name)
        name = re.sub(r'\b\d+(?:\.\d+)?\s*%\s*', '', name)
        # Weights/Units
        name = re.sub(r'\(\s*\d+(?:\.\d+)?\s*(?:g|mg|mcg|ml|oz|lb)\s*\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b\d+(?:\.\d+)?\s*(?:g|mg|mcg|ml|oz|lb)\b', '', name, flags=re.IGNORECASE)
        # Cleaning
        name = re.sub(r'^[^\w(]+|[^\w)]+$', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()

def run_tests():
    parser = IngredientParser()
    test_cases = [
        {
            "name": "Nested Parentheses",
            "text": "INGREDIENTS: Enriched Flour (Wheat Flour, Vitamin B1 (Thiamine), Vitamin B2 (Riboflavin)), Sugar, Oil (Palm, Soybean)."
        },
        {
            "name": "Weights and Units",
            "text": "Ingredients: Sugar (50g), Cocoa (20 mg), Milk (10%), Lecithin (0.5g), Vanilla (2% mcg)."
        },
        {
            "name": "Multi-line Section",
            "text": "Composition: Sugar,\nWater,\nSalt.\nNutrition Facts: ..."
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        result = parser.parse(case['text'])
        print(f"Items Found: {result['count']}")
        for item in result['list']:
            print(f"  - {item['name']}")

if __name__ == "__main__":
    run_tests()
