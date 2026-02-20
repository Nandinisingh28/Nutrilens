"""
NutriLens Backend - Image Preprocessing Service

OpenCV-based image preprocessing for OCR optimization.
Multi-strategy pipeline that handles colored backgrounds (red, blue, etc.)
"""

import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class ImagePreprocessor:
    """Image preprocessing for nutrition label OCR.
    
    Uses multiple preprocessing strategies to handle different label types,
    including labels with colored backgrounds where standard grayscale
    conversion loses critical text information.
    """
    
    # Target dimensions for processing
    TARGET_WIDTH = 1200
    MIN_WIDTH = 800
    MAX_WIDTH = 2000
    
    def __init__(self):
        pass
    
    def preprocess(self, image_bytes: bytes) -> Tuple[np.ndarray, dict]:
        """
        Preprocess image for OCR using the BEST strategy.
        Tries multiple approaches and selects the one most likely
        to produce good OCR results.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (processed image array, metadata dict)
        """
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        original_height, original_width = img.shape[:2]
        img = self._resize(img)
        
        metadata = {
            "original_width": original_width,
            "original_height": original_height,
            "processed_width": img.shape[1],
            "processed_height": img.shape[0],
        }
        
        # Try multiple strategies and pick the best
        strategies = [
            ("grayscale", self._strategy_grayscale),
            ("lab_color", self._strategy_lab_color),
            ("high_contrast", self._strategy_high_contrast),
            ("inverted", self._strategy_inverted),
        ]
        
        best_result = None
        best_score = -1
        best_name = ""
        
        for name, strategy_fn in strategies:
            try:
                result = strategy_fn(img)
                score = self._score_image(result)
                logger.debug(f"Preprocessing strategy '{name}' scored {score:.1f}")
                if score > best_score:
                    best_score = score
                    best_result = result
                    best_name = name
            except Exception as e:
                logger.debug(f"Strategy '{name}' failed: {e}")
        
        if best_result is None:
            # Absolute fallback
            best_result = self._strategy_grayscale(img)
            best_name = "grayscale_fallback"
        
        metadata["preprocessing_strategy"] = best_name
        metadata["preprocessing_score"] = round(best_score, 1)
        logger.debug(f"Best preprocessing: {best_name} (score={best_score:.1f})")
        
        return best_result, metadata
    
    def preprocess_all_strategies(self, image_bytes: bytes) -> List[Tuple[str, np.ndarray]]:
        """
        Return ALL preprocessed versions for multi-config OCR.
        Used by OCR service to try each against multiple Tesseract configs.
        
        Returns:
            List of (strategy_name, processed_image) tuples
        """
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        img = self._resize(img)
        
        results = []
        strategies = [
            ("grayscale", self._strategy_grayscale),
            ("lab_color", self._strategy_lab_color),
            ("high_contrast", self._strategy_high_contrast),
            ("inverted", self._strategy_inverted),
        ]
        
        for name, strategy_fn in strategies:
            try:
                result = strategy_fn(img)
                results.append((name, result))
            except Exception as e:
                logger.debug(f"Strategy '{name}' failed: {e}")
        
        return results
    
    # ── Preprocessing strategies ──────────────────────────────────────
    
    def _strategy_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Standard grayscale pipeline (good for white/light backgrounds)."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        kernel = np.ones((1, 1), np.uint8)
        return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    def _strategy_lab_color(self, img: np.ndarray) -> np.ndarray:
        """LAB color-space pipeline — best for colored backgrounds (red, blue, etc.).
        
        The L (lightness) channel separates brightness from color,
        so dark text on a red background stays dark in the L channel
        while a standard grayscale conversion would lose the contrast.
        """
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        
        # Upscale 2x for better detail
        h, w = l_channel.shape[:2]
        l_channel = cv2.resize(l_channel, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(l_channel)
        
        # Adaptive threshold picks up text even with uneven lighting
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 5
        )
        
        # Clean small noise
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def _strategy_high_contrast(self, img: np.ndarray) -> np.ndarray:
        """High contrast with Otsu's threshold — good for sharp text."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(resized)
        
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def _strategy_inverted(self, img: np.ndarray) -> np.ndarray:
        """Inverted pipeline — for white/light text on dark backgrounds."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        h, w = gray.shape[:2]
        resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        inverted = cv2.bitwise_not(enhanced)
        _, binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    # ── Helpers ───────────────────────────────────────────────────────
    
    def _score_image(self, binary_img: np.ndarray) -> float:
        """Score a preprocessed binary image on how much text-like content it has.
        
        Uses edge density in a reasonable range as a proxy for readable text.
        Too little = blank, too much = noise.
        """
        # Resize to standard size for consistent scoring
        h, w = binary_img.shape[:2]
        small = cv2.resize(binary_img, (400, int(400 * h / w)), interpolation=cv2.INTER_AREA)
        
        edges = cv2.Canny(small, 50, 150)
        edge_ratio = np.count_nonzero(edges) / edges.size
        
        # Sweet spot for text: 2-20% edge density
        if edge_ratio < 0.01:
            return edge_ratio * 100  # Too blank
        elif edge_ratio > 0.30:
            return max(0, 30 - (edge_ratio - 0.30) * 200)  # Too noisy
        else:
            return 10 + edge_ratio * 100  # Good range
    
    def _resize(self, img: np.ndarray) -> np.ndarray:
        """Resize image to optimal dimensions for OCR."""
        height, width = img.shape[:2]
        
        if width < self.MIN_WIDTH:
            scale = self.TARGET_WIDTH / width
            new_width = self.TARGET_WIDTH
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        elif width > self.MAX_WIDTH:
            scale = self.TARGET_WIDTH / width
            new_width = self.TARGET_WIDTH
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
    
    def preprocess_for_regions(self, image_bytes: bytes) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess image and return both color and binary versions.
        
        Returns:
            Tuple of (color image, binary image)
        """
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        img = self._resize(img)
        binary, _ = self.preprocess(image_bytes)
        
        return img, binary
    
    def to_pil(self, cv_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL Image."""
        if len(cv_image.shape) == 2:
            return Image.fromarray(cv_image)
        else:
            return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


# Singleton instance
image_preprocessor = ImagePreprocessor()
