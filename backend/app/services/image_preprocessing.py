"""
NutriLens Backend - Image Preprocessing Service

OpenCV-based image preprocessing for OCR optimization.
"""

import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class ImagePreprocessor:
    """Image preprocessing for nutrition label OCR."""
    
    # Target dimensions for processing
    TARGET_WIDTH = 1200
    MIN_WIDTH = 800
    MAX_WIDTH = 2000
    
    def __init__(self):
        pass
    
    def preprocess(self, image_bytes: bytes) -> Tuple[np.ndarray, dict]:
        """
        Preprocess image for OCR.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (processed image array, metadata dict)
        """
        # Load image
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        original_height, original_width = img.shape[:2]
        
        metadata = {
            "original_width": original_width,
            "original_height": original_height,
        }
        
        # Step 1: Resize if needed
        img = self._resize(img)
        metadata["processed_width"] = img.shape[1]
        metadata["processed_height"] = img.shape[0]
        
        # Step 2: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Step 3: Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Step 4: Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Step 5: Adaptive thresholding for better text extraction
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Step 6: Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        logger.debug(f"Image preprocessed: {original_width}x{original_height} -> {img.shape[1]}x{img.shape[0]}")
        
        return cleaned, metadata
    
    def _resize(self, img: np.ndarray) -> np.ndarray:
        """Resize image to optimal dimensions for OCR."""
        height, width = img.shape[:2]
        
        if width < self.MIN_WIDTH:
            # Scale up small images
            scale = self.TARGET_WIDTH / width
            new_width = self.TARGET_WIDTH
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        elif width > self.MAX_WIDTH:
            # Scale down large images
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
            # Grayscale
            return Image.fromarray(cv_image)
        else:
            # Color - convert BGR to RGB
            return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


# Singleton instance
image_preprocessor = ImagePreprocessor()
