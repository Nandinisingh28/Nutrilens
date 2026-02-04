"""
NutriLens Backend - Text Utilities

Text processing and normalization utilities.
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean OCR text by removing noise and normalizing.
    
    Args:
        text: Raw OCR text
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that are likely OCR noise
    text = re.sub(r'[|\\~`^]', '', text)
    
    # Normalize common OCR mistakes
    replacements = {
        '0g': 'og',  # zero to letter o
        '1': 'l',    # for specific words
        'O': '0',    # letter O to zero in numbers
    }
    
    # Fix common number patterns
    text = re.sub(r'(\d)\s*g\s*(?=\d|$)', r'\1g ', text)
    text = re.sub(r'(\d)\s*mg\s*(?=\d|$)', r'\1mg ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_unit(value: str, unit: str) -> tuple[float, str]:
    """
    Normalize nutrition value and unit.
    
    Args:
        value: The numeric value
        unit: The unit (g, mg, etc.)
    
    Returns:
        Tuple of (normalized_value, normalized_unit)
    """
    try:
        num = float(value)
    except ValueError:
        return (0.0, unit)
    
    unit = unit.lower().strip()
    
    # Normalize to standard units
    if unit in ['mg', 'milligram', 'milligrams']:
        return (num, 'mg')
    elif unit in ['g', 'gram', 'grams']:
        return (num, 'g')
    elif unit in ['mcg', 'ug', 'microgram', 'micrograms']:
        return (num, 'mcg')
    elif unit in ['iu', 'international units']:
        return (num, 'IU')
    elif unit in ['%', 'percent', 'dv', '% dv']:
        return (num, '%DV')
    
    return (num, unit)


def extract_numbers(text: str) -> list[float]:
    """
    Extract all numbers from text.
    
    Args:
        text: Input text
    
    Returns:
        List of numbers found
    """
    pattern = r'[-+]?\d*\.?\d+'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def find_nutrition_value(text: str, nutrient: str) -> Optional[float]:
    """
    Find a specific nutrition value in text.
    
    Args:
        text: Text to search
        nutrient: Nutrient name to find
    
    Returns:
        The value if found, None otherwise
    """
    patterns = [
        rf'{nutrient}\s*[:\s]*(\d+\.?\d*)\s*(?:g|mg|mcg)?',
        rf'(\d+\.?\d*)\s*(?:g|mg|mcg)?\s*{nutrient}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def detect_sugar_aliases(ingredients: str) -> list[str]:
    """
    Detect sugar-related ingredients in an ingredients list.
    
    Args:
        ingredients: Ingredients text
    
    Returns:
        List of sugar aliases found
    """
    sugar_aliases = [
        'sugar', 'sucrose', 'glucose', 'fructose', 'dextrose',
        'maltose', 'lactose', 'galactose', 'corn syrup',
        'high fructose corn syrup', 'hfcs', 'honey', 'molasses',
        'agave', 'maple syrup', 'cane juice', 'fruit juice concentrate',
        'brown sugar', 'raw sugar', 'invert sugar', 'malt syrup',
        'dextrin', 'maltodextrin', 'barley malt', 'rice syrup',
        'caramel', 'treacle', 'muscovado', 'turbinado',
        'demerara', 'panela', 'jaggery', 'coconut sugar',
    ]
    
    ingredients_lower = ingredients.lower()
    found = []
    
    for alias in sugar_aliases:
        if alias in ingredients_lower:
            found.append(alias)
    
    return found


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
