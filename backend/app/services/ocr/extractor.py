"""
OCR Text Extraction with Enhanced Sensitivity and Debug Logging
"""
import pytesseract
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import logging

from app.services.ocr.preprocessor import ImagePreprocessor

# Configure debug logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OCRExtractor:
    """
    Extracts text from food label images using keyword-anchored regions.
    Enhanced with multiple preprocessing modes and debug output.
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
    # Added character whitelist for ingredients to reduce noise
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
    
    def extract_from_image(self, image_data: bytes) -> Dict[str, str]:
        """
        Extract both nutrition and ingredients text from an image
        Uses multiple preprocessing strategies for best results.
        """
        self.debug_info = {
            'preprocessing_modes': [],
            'texts_extracted': [],
            'anchors_found': [],
            'best_mode': None,
            'raw_texts': []
        }
        
        best_nutrition = ""
        best_ingredients = ""
        best_full_text = ""
        best_word_count = 0
        
        # Try multiple preprocessing approaches
        preprocessing_modes = [
            ('enhanced', self._preprocess_enhanced),
            ('standard', self._preprocess_standard),
            ('high_contrast', self._preprocess_high_contrast),
            ('inverted', self._preprocess_inverted),
            ('color_isolated', self._preprocess_color_isolated),
            ('morphological', self._preprocess_morphological),
        ]
        
        for mode_name, preprocess_func in preprocessing_modes:
            try:
                processed = preprocess_func(image_data)
                
                # Try multiple Tesseract configs
                for config in self.TESSERACT_CONFIGS[:3]:  # Limit to top 3
                    try:
                        full_text = pytesseract.image_to_string(processed, config=config)
                        word_count = len(full_text.split())
                        
                        self.debug_info['raw_texts'].append({
                            'mode': mode_name,
                            'config': config,
                            'word_count': word_count,
                            'preview': full_text[:500] if full_text else ""
                        })
                        
                        # Keep the best result (most words extracted)
                        if word_count > best_word_count:
                            best_word_count = word_count
                            best_full_text = full_text
                            self.debug_info['best_mode'] = f"{mode_name} + {config}"
                            
                            # Log anchors found
                            text_upper = full_text.upper()
                            found_anchors = [a for a in self.NUTRITION_ANCHORS + self.INGREDIENTS_ANCHORS 
                                           if a.upper() in text_upper]
                            self.debug_info['anchors_found'] = found_anchors
                            
                    except Exception as e:
                        logger.debug(f"OCR failed with config {config}: {e}")
                        
            except Exception as e:
                logger.debug(f"Preprocessing mode {mode_name} failed: {e}")
        
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
                   f"Words={best_word_count}, Anchors={self.debug_info['anchors_found']}")
        logger.debug(f"OCR Full Text Preview: {best_full_text[:1000]}")
        
        return {
            "nutrition_text": best_nutrition or best_full_text,
            "ingredients_text": best_ingredients or best_full_text,
            "full_text": best_full_text,
            "debug_info": self.debug_info
        }
    
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
        Improved with adaptive thresholding for uneven lighting.
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
        
        # Invert -> Adaptive Threshold -> Invert back
        # This is more robust than fixed threshold
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
        Optimized for better character separation.
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
        
        # Very mild morphological operations
        # Connect broken parts
        kernel = np.ones((2, 1), np.uint8)  # Vertical connection
        connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return connected
    
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
