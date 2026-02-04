"""
NutriLens Backend - Image Utilities

Image preprocessing for better OCR results.
"""

import os
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


def preprocess_image(image_path: str) -> Optional[str]:
    """
    Preprocess image for better OCR results.
    
    Applies:
    - Grayscale conversion
    - Noise reduction
    - Contrast enhancement
    - Binarization
    
    Args:
        image_path: Path to input image
    
    Returns:
        Path to processed image, or None if processing fails
    """
    try:
        import cv2
        import numpy as np
        
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding for better text detection
        binary = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Save processed image
        input_path = Path(image_path)
        output_path = input_path.parent / f"processed_{input_path.name}"
        
        cv2.imwrite(str(output_path), denoised)
        
        logger.info(f"Image preprocessed: {output_path}")
        
        return str(output_path)
        
    except ImportError:
        logger.warning("OpenCV not available, skipping preprocessing")
        return None
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return None


def resize_image(
    image_path: str,
    max_width: int = 1200,
    max_height: int = 1600,
) -> Optional[str]:
    """
    Resize image while maintaining aspect ratio.
    
    Args:
        image_path: Path to input image
        max_width: Maximum width
        max_height: Maximum height
    
    Returns:
        Path to resized image
    """
    try:
        from PIL import Image
        
        image = Image.open(image_path)
        
        # Calculate new size maintaining aspect ratio
        width, height = image.size
        
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save
        input_path = Path(image_path)
        output_path = input_path.parent / f"resized_{input_path.name}"
        
        image.save(str(output_path), quality=95)
        
        logger.info(f"Image resized: {output_path}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return None


def rotate_image(image_path: str, angle: int) -> Optional[str]:
    """
    Rotate image by specified angle.
    
    Args:
        image_path: Path to input image
        angle: Rotation angle in degrees
    
    Returns:
        Path to rotated image
    """
    try:
        from PIL import Image
        
        image = Image.open(image_path)
        rotated = image.rotate(angle, expand=True)
        
        input_path = Path(image_path)
        output_path = input_path.parent / f"rotated_{input_path.name}"
        
        rotated.save(str(output_path), quality=95)
        
        logger.info(f"Image rotated {angle}°: {output_path}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Image rotation failed: {e}")
        return None
