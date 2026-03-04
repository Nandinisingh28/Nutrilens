"""
OCR Text Extraction with Enhanced Sensitivity and Debug Logging

Enhanced with image quality checking, confidence-based result selection,
and additional preprocessing modes (denoised, sharpened).
"""
import pytesseract
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import os
import shutil
import logging

from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.ocr_space_service import OCRSpaceOCR
from app.config import get_settings

# Configure debug logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ── Windows Tesseract Auto-Detection ──────────────────────────────────
if os.name == 'nt':
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        _common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
        ]
        for _path in _common_paths:
            if os.path.exists(_path):
                pytesseract.pytesseract.tesseract_cmd = _path
                logger.info(f"Tesseract found at: {_path}")
                break


class OCRExtractor:
    """
    Extracts text from food label images using keyword-anchored regions.
    Enhanced with multiple preprocessing modes, confidence-based selection,
    and image quality checking.
    """
    
    # Anchor keywords for different sections (expanded list)
    NUTRITION_ANCHORS = [
        "NUTRITION", "NUTRITIONAL", "NUTRITIVE", "NUTRITION FACTS",
        "NUTRITIONAL INFORMATION", "NUTRITION INFORMATION",
        "NUTRITIVE VALUE", "NUTRIENTS", "NUTRIENT",
        "ENERGY", "PROTEIN", "CARBOHYDRATE", "FAT",
        "CALORIES", "KCAL", "SERVING",
        "PER 100", "PER SERVING", "AMOUNT PER",
        "पोषण", "पोषक तत्व"  # Hindi
    ]
    
    INGREDIENTS_ANCHORS = [
        "INGREDIENTS", "INGREDIENT", "CONTAINS", "COMPOSITION",
        "MADE WITH", "MADE FROM", "CONTENTS",
        "सामग्री", "घटक"  # Hindi
    ]
    
    # Tesseract configs to try (from most to least strict)
    _WHITELIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;()[]{}%-/ "
    
    TESSERACT_CONFIGS = [
        # 1. Best for block text with whitelist (LSTM only)
        f'--oem 1 --psm 6 -l eng -c tessedit_char_whitelist="{_WHITELIST}"',
        
        # 2. Standard block text (for general fallback)
        '--oem 3 --psm 6 -l eng',
        
        # 3. Single column (good for ingredient lists)
        f'--oem 1 --psm 4 -l eng -c tessedit_char_whitelist="{_WHITELIST}"',
        
        # 4. Sparse text (for scattered labels)
        '--oem 3 --psm 11 -l eng',
        
        # 5. Last resort: Fully automatic
        '--oem 3 --psm 3 -l eng',
    ]
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.debug_info = {}
        
        # OCR.space (free cloud OCR — 500 req/day)
        _settings = get_settings()
        self._ocr_space = OCRSpaceOCR(
            api_key=_settings.ocr_space_api_key
        )
        self._ocr_provider = _settings.ocr_provider
    
    def extract_from_image(self, image_data: bytes) -> Dict[str, str]:
        """
        Extract both nutrition and ingredients text from an image.
        
        Strategy:
        1. Try Google Vision API (if configured and available)
        2. Fall back to Tesseract multi-strategy pipeline
        """
        self.debug_info = {
            'preprocessing_modes': [],
            'texts_extracted': [],
            'anchors_found': [],
            'best_mode': None,
            'raw_texts': [],
            'image_quality': None,
            'ocr_source': None,
        }
        
        # ── Image quality check ───────────────────────────────────────
        quality = self.preprocessor.check_quality(image_data)
        self.debug_info['image_quality'] = quality
        
        if not quality.get('is_valid'):
            logger.warning(f"Image quality issues detected: {quality.get('issues', [])}")
        
        # ── Try OCR.space first ──────────────────────────────────────
        if self._ocr_provider == "ocr_space" and self._ocr_space.is_available:
            ocr_text = self._ocr_space.detect_text(image_data)
            
            if ocr_text and len(ocr_text) >= 20:
                cleaned_text = self._clean_text(ocr_text)
                
                self.debug_info['best_mode'] = "ocr_space"
                self.debug_info['ocr_source'] = "ocr_space"
                
                # Log anchors found
                text_upper = cleaned_text.upper()
                found_anchors = [a for a in self.NUTRITION_ANCHORS + self.INGREDIENTS_ANCHORS 
                               if a.upper() in text_upper]
                self.debug_info['anchors_found'] = found_anchors
                
                logger.info(
                    f"Using OCR.space: {len(cleaned_text)} chars, "
                    f"anchors={found_anchors}"
                )
                
                # Extract sections
                nutrition_text = self._extract_section(
                    cleaned_text, self.NUTRITION_ANCHORS, "nutrition"
                )
                ingredients_text = self._extract_section(
                    cleaned_text, self.INGREDIENTS_ANCHORS, "ingredients"
                )
                
                return {
                    "nutrition_text": nutrition_text or cleaned_text,
                    "ingredients_text": ingredients_text or cleaned_text,
                    "full_text": cleaned_text,
                    "debug_info": self.debug_info,
                    "ocr_source": "ocr_space",
                }
            else:
                logger.info("OCR.space returned insufficient text, falling back to Tesseract")
        
        # ── Tesseract multi-strategy fallback ─────────────────────────
        self.debug_info['ocr_source'] = "tesseract"
        
        best_nutrition = ""
        best_ingredients = ""
        best_full_text = ""
        best_score = -1
        
        # Limit to the most effective preprocessing approaches to save time
        preprocessing_modes = [
            ('standard', self._preprocess_standard),
            ('enhanced', self._preprocess_enhanced),
            ('inverted', self._preprocess_inverted),
        ]
        
        all_attempts = []
        
        for mode_name, preprocess_func in preprocessing_modes:
            try:
                processed = preprocess_func(image_data)
                
                # Try only the best 2 Tesseract configs
                for config in self.TESSERACT_CONFIGS[:2]:
                    try:
                        # Use image_to_data for confidence scores
                        ocr_data = pytesseract.image_to_data(
                            processed, config=config,
                            output_type=pytesseract.Output.DICT
                        )
                        full_text = " ".join([x for x in ocr_data['text'] if x.strip()])
                        word_count = len(full_text.split())
                        
                        # Calculate average confidence
                        conf_values = [int(c) for c in ocr_data['conf'] if c != '-1' and int(c) > 0]
                        avg_conf = sum(conf_values) / len(conf_values) if conf_values else 0
                        
                        # Also get the full string output for section extraction
                        full_string = pytesseract.image_to_string(processed, config=config)
                        
                        attempt = {
                            'mode': mode_name,
                            'config': config,
                            'word_count': word_count,
                            'confidence': avg_conf,
                            'text_len': len(full_string),
                            'preview': full_string[:500] if full_string else ""
                        }
                        all_attempts.append(attempt)
                        self.debug_info['raw_texts'].append(attempt)
                        
                        # ── Confidence-based selection ────────────────
                        # Prefer results with meaningful text AND high confidence
                        score = self._score_attempt(full_string, avg_conf, word_count)
                        
                        if score > best_score:
                            best_score = score
                            best_full_text = full_string
                            self.debug_info['best_mode'] = f"{mode_name} + {config}"
                            
                            # Log anchors found
                            text_upper = full_string.upper()
                            found_anchors = [a for a in self.NUTRITION_ANCHORS + self.INGREDIENTS_ANCHORS 
                                           if a.upper() in text_upper]
                            self.debug_info['anchors_found'] = found_anchors
                            
                    except Exception as e:
                        logger.debug(f"OCR failed with config {config}: {e}")
                        
            except Exception as e:
                logger.debug(f"Preprocessing mode {mode_name} failed: {e}")
        
        # ── Clean the best text ───────────────────────────────────────
        if best_full_text:
            best_full_text = self._clean_text(best_full_text)
        
        # Extract sections from best text
        if best_full_text:
            best_nutrition = self._extract_section(
                best_full_text, 
                self.NUTRITION_ANCHORS,
                "nutrition"
            )
            
            best_ingredients = self._extract_section(
                best_full_text,
                self.INGREDIENTS_ANCHORS,
                "ingredients"
            )
        
        logger.info(f"OCR Debug: Best mode={self.debug_info['best_mode']}, "
                   f"Score={best_score:.1f}, Anchors={self.debug_info['anchors_found']}")
        logger.debug(f"OCR Full Text Preview: {best_full_text[:1000]}")
        
        return {
            "nutrition_text": best_nutrition or best_full_text,
            "ingredients_text": best_ingredients or best_full_text,
            "full_text": best_full_text,
            "debug_info": self.debug_info,
            "ocr_source": "tesseract",
        }
    
    def _score_attempt(self, text: str, confidence: float, word_count: int) -> float:
        """
        Score an OCR attempt based on confidence, text length, and anchor words.
        """
        text_len = len(text)
        score = confidence * 0.4
        score += min(word_count, 50) * 0.5
        
        text_upper = text.upper()
        anchors_found = sum(1 for a in self.NUTRITION_ANCHORS + self.INGREDIENTS_ANCHORS 
                          if a.upper() in text_upper)
        score += anchors_found * 5
        
        if text_len <= 20 or confidence <= 40:
            score *= 0.5
        
        return score
    
    # ── OCR Text Cleaning ─────────────────────────────────────────────
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize OCR text with comprehensive error correction.
        Fixes common OCR misreadings of nutrition label text.
        """
        if not text:
            return ""
        
        # ── Character-level fixes ─────────────────────────────────────
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
        
        # ── kcal fixes ────────────────────────────────────────────────
        text = text.replace('kcaI', 'kcal')
        text = text.replace('KcaI', 'Kcal')
        text = text.replace('kcai', 'kcal')
        
        # ── Nutrient name corrections ─────────────────────────────────
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
        text = re.sub(r'(\d)\s*\}', r'\1)', text)
        text = re.sub(r'\{\s*(\d)', r'(\1', text)
        text = re.sub(r'\[\s*-', '<', text)
        
        # ── "Less than" / "Not more than" normalization ───────────────
        text = re.sub(r'/\s*(\d)', r'< \1', text)
        text = re.sub(r'[<]\s*0(\d)', r'< 0.\1', text)
        
        # ── Whitespace cleanup ────────────────────────────────────────
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    # ── Preprocessing Modes ───────────────────────────────────────────
    
    def _preprocess_standard(self, image_data: bytes) -> np.ndarray:
        """Standard preprocessing"""
        return self.preprocessor.preprocess_for_display(image_data)
    
    def _preprocess_enhanced(self, image_data: bytes) -> np.ndarray:
        """Enhanced preprocessing with denoising"""
        img = self.preprocessor._load_image(image_data)
        gray = self.preprocessor._to_grayscale(img)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # CLAHE with stronger settings
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Resize 2x
        h, w = enhanced.shape[:2]
        resized = cv2.resize(enhanced, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            resized, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        return binary
    
    def _preprocess_high_contrast(self, image_data: bytes) -> np.ndarray:
        """High contrast mode for light backgrounds"""
        img = self.preprocessor._load_image(image_data)
        gray = self.preprocessor._to_grayscale(img)
        
        # Resize first
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # Heavy CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(resized)
        
        # Otsu threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_inverted(self, image_data: bytes) -> np.ndarray:
        """Inverted preprocessing for dark backgrounds"""
        img = self.preprocessor._load_image(image_data)
        gray = self.preprocessor._to_grayscale(img)
        
        # Resize
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        # Invert
        inverted = cv2.bitwise_not(enhanced)
        
        # Threshold
        _, binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_color_isolated(self, image_data: bytes) -> np.ndarray:
        """
        Preprocessing for WHITE TEXT on COLORED backgrounds (red, blue, etc.)
        Uses LAB color space to isolate light text from dark/colored backgrounds.
        """
        img = self.preprocessor._load_image(image_data)
        
        # Resize first for better detail
        h, w = img.shape[:2]
        img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # Convert to LAB color space (L channel is lightness)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(l_channel)
        
        # Adaptive Threshold
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, -10  # Negative C to pick up lighter text
        )
        
        # Clean up noise
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def _preprocess_morphological(self, image_data: bytes) -> np.ndarray:
        """
        Morphological preprocessing to clean up noisy text.
        """
        img = self.preprocessor._load_image(image_data)
        gray = self.preprocessor._to_grayscale(img)
        
        # Resize
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # Bilateral filter to reduce noise while keeping edges
        filtered = cv2.bilateralFilter(resized, 9, 75, 75)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        
        # Otsu's thresholding
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Connect broken parts
        kernel = np.ones((2, 1), np.uint8)
        connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return connected
    
    def _preprocess_denoised(self, image_data: bytes) -> np.ndarray:
        """
        Color-preserving denoised preprocessing.
        Uses fastNlMeansDenoisingColored to keep color information,
        then converts to grayscale with CLAHE for OCR.
        """
        img = self.preprocessor._load_image(image_data)
        
        # Color-preserving denoising (from user's NutriLensOCR)
        denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # Convert to grayscale
        gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Resize 2x
        h, w = enhanced.shape[:2]
        resized = cv2.resize(enhanced, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            resized, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        return binary
    
    def _preprocess_sharpened(self, image_data: bytes) -> np.ndarray:
        """
        Sharpened preprocessing using unsharp mask kernel.
        Good for images that are slightly out of focus.
        """
        img = self.preprocessor._load_image(image_data)
        
        # Sharpening kernel (from user's NutriLensOCR)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        
        # Convert to grayscale
        gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
        
        # Resize 2x
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        # Otsu threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    # ── Section Extraction ────────────────────────────────────────────
    
    def _extract_section(
        self, 
        full_text: str,
        anchors: List[str],
        section_type: str
    ) -> str:
        """
        Extract a specific section using anchor keywords
        """
        text_upper = full_text.upper()
        
        for anchor in anchors:
            anchor_upper = anchor.upper()
            if anchor_upper in text_upper:
                idx = text_upper.find(anchor_upper)
                section = full_text[idx:]
                section = self._find_section_end(section, section_type)
                
                if len(section) > 15:  # Reduced minimum
                    return section
        
        # Return full text if no anchor found
        return full_text
    
    def _find_section_end(self, text: str, section_type: str) -> str:
        """Find where the section ends based on common patterns"""
        lines = text.split('\n')
        result_lines = []
        
        if section_type == "nutrition":
            end_markers = ["INGREDIENTS", "CONTAINS:", "STORAGE", "DIRECTIONS", 
                          "BEST BEFORE", "MFG", "MANUFACTURED", "ALLERGEN"]
        else:
            end_markers = ["NUTRITION", "STORAGE", "DIRECTIONS", "BEST BEFORE", 
                          "ALLERGEN", "MFG", "MANUFACTURED"]
        
        for line in lines:
            line_upper = line.upper().strip()
            
            if any(marker in line_upper for marker in end_markers):
                if len(result_lines) > 0:
                    break
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def extract_nutrition_only(self, image_data: bytes) -> str:
        """Extract only nutrition section from image"""
        result = self.extract_from_image(image_data)
        return result["nutrition_text"]
    
    def extract_ingredients_only(self, image_data: bytes) -> str:
        """Extract only ingredients section from image"""
        result = self.extract_from_image(image_data)
        return result["ingredients_text"]
    
    def get_debug_info(self) -> Dict:
        """Return debug information from last extraction"""
        return self.debug_info
