"""
NutriLens Backend - OCR Service

Tesseract OCR for extracting text from nutrition labels.
Enhanced with multi-strategy preprocessing and multi-config extraction.
"""

import pytesseract
from PIL import Image
import numpy as np
import re
from typing import Optional, List, Tuple, Dict

from app.core.config import settings
from app.core.logging import get_logger
from app.services.image_preprocessing import image_preprocessor

logger = get_logger(__name__)


# Anchor keywords that indicate successful nutrition label reading
_NUTRITION_ANCHORS = [
    "nutrition", "protein", "carbohydrate", "sugar", "fat",
    "energy", "kcal", "sodium", "fiber", "serving",
    "per 100", "calories",
]


class OCRService:
    """OCR service using pytesseract with multi-strategy extraction."""
    
    # Tesseract configs to try (from most to least strict for tables)
    TESSERACT_CONFIGS = [
        '--oem 3 --psm 6 -l eng',   # Assume uniform block of text
        '--oem 3 --psm 4 -l eng',   # Assume single column of variable sizes
        '--oem 3 --psm 3 -l eng',   # Fully automatic page segmentation
    ]
    
    def __init__(self):
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
    
    def extract_text(self, image_bytes: bytes) -> dict:
        """
        Extract text from image using OCR.
        Tries multiple preprocessing strategies × Tesseract configs
        and returns the best result.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dict with raw_text, cleaned_text, and confidence
        """
        try:
            # Get all preprocessed versions
            strategy_images = image_preprocessor.preprocess_all_strategies(image_bytes)
            
            if not strategy_images:
                # Fallback: single preprocessing
                processed_img, metadata = image_preprocessor.preprocess(image_bytes)
                strategy_images = [("default", processed_img)]
            
            best_result = None
            best_score = -1
            
            for strategy_name, processed_img in strategy_images:
                pil_image = image_preprocessor.to_pil(processed_img)
                
                # Try top 2 Tesseract configs per strategy (limit combinations)
                for config in self.TESSERACT_CONFIGS[:2]:
                    try:
                        result = self._run_ocr(pil_image, config, strategy_name)
                        score = self._score_result(result)
                        
                        if score > best_score:
                            best_score = score
                            best_result = result
                            
                    except Exception as e:
                        logger.debug(f"OCR failed: strategy={strategy_name}, config={config}: {e}")
            
            if best_result is None:
                # Absolute fallback: single strategy, single config
                processed_img, metadata = image_preprocessor.preprocess(image_bytes)
                pil_image = image_preprocessor.to_pil(processed_img)
                best_result = self._run_ocr(pil_image, self.TESSERACT_CONFIGS[0], "fallback")
            
            # Clean the raw text
            raw_text = best_result["raw_text"]
            cleaned_text = self._clean_text(raw_text)
            
            logger.info(
                f"OCR extracted {len(cleaned_text)} chars, "
                f"confidence={best_result['confidence']:.1f}%, "
                f"strategy={best_result.get('strategy', 'unknown')}"
            )
            
            return {
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "confidence": round(best_result["confidence"] / 100, 2),
                "word_count": best_result["word_count"],
                "metadata": best_result.get("metadata", {}),
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
    
    def _run_ocr(self, pil_image: Image.Image, config: str, strategy: str) -> dict:
        """Run OCR with a specific config and return structured result."""
        ocr_data = pytesseract.image_to_data(
            pil_image,
            config=config,
            output_type=pytesseract.Output.DICT
        )
        
        confidences = [c for c in ocr_data['conf'] if c > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        raw_text = pytesseract.image_to_string(pil_image, config=config)
        word_count = len([w for w in ocr_data['text'] if w.strip()])
        
        return {
            "raw_text": raw_text,
            "confidence": avg_confidence,
            "word_count": word_count,
            "strategy": strategy,
            "config": config,
        }
    
    def _score_result(self, result: dict) -> float:
        """Score an OCR result based on confidence, word count, and anchor words."""
        confidence = result.get("confidence", 0)
        word_count = result.get("word_count", 0)
        raw_text = result.get("raw_text", "").lower()
        
        # Base score from confidence and word count
        score = confidence * 0.4 + min(word_count, 50) * 0.5
        
        # Bonus for anchor keywords found (strong indicator of correct reading)
        anchors_found = sum(1 for a in _NUTRITION_ANCHORS if a in raw_text)
        score += anchors_found * 5
        
        return score
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text with comprehensive error correction."""
        if not text:
            return ""
        
        # ── Character-level fixes ─────────────────────────────────────
        # Fix common single-character OCR confusions
        char_fixes = {
            '|': 'l',
            '¢': 'c',
        }
        for old, new in char_fixes.items():
            text = text.replace(old, new)
        
        # ── Unit confusion fixes ──────────────────────────────────────
        # OCR often reads (g) as (9), (G), (o), (0), etc.
        text = re.sub(r'\(9\)', '(g)', text)
        text = re.sub(r'\(G\)', '(g)', text)
        text = re.sub(r'\(o\)', '(g)', text)
        text = re.sub(r'\(0\)', '(g)', text)
        
        # ── Number / 100g fixes ───────────────────────────────────────
        text = text.replace('lOO', '100')
        text = text.replace('l00', '100')
        text = text.replace('1OO', '100')
        text = text.replace('Og', '0g')
        text = text.replace('0g', '0g')
        
        # ── kcal fixes ────────────────────────────────────────────────
        text = text.replace('kcaI', 'kcal')
        text = text.replace('KcaI', 'Kcal')
        text = text.replace('kcai', 'kcal')
        
        # ── Nutrient name corrections ─────────────────────────────────
        # These are common OCR misreadings of nutrition label terms
        nutrient_fixes = {
            # Protein
            'Proteln': 'Protein',
            'Protien': 'Protein',
            'Prctein': 'Protein',
            'Protain': 'Protein',
            # Carbohydrate
            'Carbohyd rate': 'Carbohydrate',
            'Carbohydrato': 'Carbohydrate',
            'Carboryoraio': 'Carbohydrate',
            'Carbchydrate': 'Carbohydrate',
            'Carbohydrare': 'Carbohydrate',
            'Carbohydrato': 'Carbohydrate',
            # Sugar
            'Sugers': 'Sugars',
            'Sugare': 'Sugars',
            'Sugats': 'Sugars',
            # Fat
            'Saturatod': 'Saturated',
            'Saturatcd': 'Saturated',
            'a rated': 'Saturated',
            'Saluraled': 'Saturated',
            # Sodium
            'Sodlum': 'Sodium',
            'Scdium': 'Sodium',
            'Sod1um': 'Sodium',
            # Energy
            'Enerqy': 'Energy',
            'Eneryg': 'Energy',
            # Fiber
            'Diotary': 'Dietary',
        }
        
        for old, new in nutrient_fixes.items():
            text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
        
        # ── Bracket/symbol confusion in numeric contexts ──────────────
        # } → ) and { → ( near numbers
        text = re.sub(r'(\d)\s*\}', r'\1)', text)
        text = re.sub(r'\{\s*(\d)', r'(\1', text)
        # [ → ( and ] → )  near nutrient names
        text = re.sub(r'\[\s*-', '<', text)
        
        # ── "Less than" / "Not more than" normalization ───────────────
        # Normalize various OCR-corrupted versions
        text = re.sub(r'/\s*(\d)', r'< \1', text)  # /05 → < 05
        text = re.sub(r'[<]\s*0(\d)', r'< 0.\1', text)  # < 05 → < 0.5
        
        # ── Whitespace cleanup ────────────────────────────────────────
        text = re.sub(r'[ \t]+', ' ', text)  # Collapse horizontal space
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        
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
            
            custom_config = r'--oem 3 --psm 6 -l eng'
            ocr_data = pytesseract.image_to_data(
                pil_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            lines = self._group_into_lines(ocr_data)
            
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
                
                if len(section_lines) > 1 and any(
                    kw in line_lower for kw in 
                    ['ingredients', 'nutrition', 'allergen', 'storage', 'directions']
                ):
                    break
        
        return '\n'.join(section_lines) if section_lines else None


# Singleton instance
ocr_service = OCRService()
