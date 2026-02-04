"""
NutriLens Backend - OCR Service

Tesseract OCR for extracting text from nutrition labels.
"""

import pytesseract
from PIL import Image
import numpy as np
import re
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.image_preprocessing import image_preprocessor

logger = get_logger(__name__)


class OCRService:
    """OCR service using pytesseract."""
    
    def __init__(self):
        # Configure tesseract path if specified
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
    
    def extract_text(self, image_bytes: bytes) -> dict:
        """
        Extract text from image using OCR.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dict with raw_text, cleaned_text, and confidence
        """
        try:
            # Preprocess image
            processed_img, metadata = image_preprocessor.preprocess(image_bytes)
            
            # Convert to PIL for pytesseract
            pil_image = image_preprocessor.to_pil(processed_img)
            
            # OCR configuration for nutrition labels
            custom_config = r'--oem 3 --psm 6 -l eng'
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(
                pil_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence (excluding -1 values)
            confidences = [c for c in ocr_data['conf'] if c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Get raw text
            raw_text = pytesseract.image_to_string(pil_image, config=custom_config)
            
            # Clean text
            cleaned_text = self._clean_text(raw_text)
            
            logger.info(f"OCR extracted {len(cleaned_text)} chars with {avg_confidence:.1f}% avg confidence")
            
            return {
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "confidence": round(avg_confidence / 100, 2),  # Normalize to 0-1
                "word_count": len([w for w in ocr_data['text'] if w.strip()]),
                "metadata": metadata,
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "raw_text": "",
                "cleaned_text": "",
                "confidence": 0,
                "word_count": 0,
                "error": str(e),
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        replacements = {
            '|': 'l',
            '0g': '0g',
            'Og': '0g',
            'lOO': '100',
            'l00': '100',
            'kcaI': 'kcal',
            'KcaI': 'Kcal',
            'Proteln': 'Protein',
            'Carbohyd rate': 'Carbohydrate',
            'Sodlum': 'Sodium',
            'Saturatod': 'Saturated',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def extract_regions(self, image_bytes: bytes) -> dict:
        """
        Extract text from specific regions of the label.
        
        Attempts to identify:
        - Ingredients section
        - Nutrition facts table
        - Claims/marketing text
        """
        try:
            processed_img, metadata = image_preprocessor.preprocess(image_bytes)
            pil_image = image_preprocessor.to_pil(processed_img)
            
            # Get text with bounding boxes
            custom_config = r'--oem 3 --psm 6 -l eng'
            ocr_data = pytesseract.image_to_data(
                pil_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Group text by vertical position (lines)
            lines = self._group_into_lines(ocr_data)
            
            # Identify sections
            ingredients_section = self._find_section(lines, ['ingredients', 'contains'])
            nutrition_section = self._find_section(lines, ['nutrition', 'facts', 'per 100g', 'per serving'])
            
            return {
                "lines": lines,
                "ingredients_section": ingredients_section,
                "nutrition_section": nutrition_section,
            }
            
        except Exception as e:
            logger.error(f"Region extraction failed: {e}")
            return {"error": str(e)}
    
    def _group_into_lines(self, ocr_data: dict) -> list:
        """Group OCR words into lines based on vertical position."""
        lines = []
        current_line = []
        last_top = -1
        
        for i, text in enumerate(ocr_data['text']):
            if not text.strip():
                continue
            
            top = ocr_data['top'][i]
            
            # New line if vertical position changes significantly
            if last_top >= 0 and abs(top - last_top) > 10:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
            
            current_line.append(text)
            last_top = top
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _find_section(self, lines: list, keywords: list) -> Optional[str]:
        """Find a section in lines based on keywords."""
        section_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            if any(kw in line_lower for kw in keywords):
                in_section = True
            
            if in_section:
                section_lines.append(line)
                
                # Stop at next section header
                if len(section_lines) > 1 and any(
                    kw in line_lower for kw in 
                    ['ingredients', 'nutrition', 'allergen', 'storage', 'directions']
                ):
                    break
        
        return '\n'.join(section_lines) if section_lines else None


# Singleton instance
ocr_service = OCRService()
