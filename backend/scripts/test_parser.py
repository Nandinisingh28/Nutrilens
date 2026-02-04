
import sys
import os
from unittest.mock import MagicMock

# Stub out heavy dependencies before importing any app modules
mock_fastapi = MagicMock()
sys.modules['fastapi'] = mock_fastapi
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.ext.asyncio'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['app.core.config'] = MagicMock()
sys.modules['app.core.logging'] = MagicMock()
sys.modules['app.db'] = MagicMock()
sys.modules['app.core.exceptions'] = MagicMock()
sys.modules['app.main'] = MagicMock()

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ingredient_parser import IngredientParser

def test_parser():
    parser = IngredientParser()
    
    test_cases = [
        {
            "name": "Nested Parentheses",
            "text": "INGREDIENTS: Enriched Flour (Wheat Flour, Niacin, Reduced Iron, Thiamine Mononitrate (Vitamin B1), Riboflavin (Vitamin B2), Folic Acid), Sugar, Vegetable Oil (Soybean, Palm, And/Or Palm Kernel Oil With Tbhq For Freshness), Salt, Contains 2% Or Less Of Cornstarch, Molasses, Soy Lecithin, Baking Soda, Natural and Artificial Flavors."
        },
        {
            "name": "Weights and Units",
            "text": "Ingredients: Sugar (50g), Cocoa Butter (20mg), Milk Powder (10%), Lecithin (0.5g), Vanilla (2% mcg)."
        },
        {
            "name": "Multiple Separators",
            "text": "Sugar • Flour; Salt; Lecithin"
        },
        {
            "name": "No Marker",
            "text": "Sugar, Salt, Water, Citric Acid."
        }
    ]
    
    for case in test_cases:
        print(f"\n--- Testing: {case['name']} ---")
        result = parser.parse(case['text'])
        print(f"Raw Text Extraction: {result['raw_text'][:100]}...")
        print(f"Count: {result['count']}")
        for i, ing in enumerate(result['list']):
            print(f"  {i+1}. {ing['name']}")

if __name__ == "__main__":
    test_parser()
