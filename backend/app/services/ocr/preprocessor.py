"""
Image Preprocessing for OCR

Enhanced with image quality checking and Canny-edge-based deskew.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple, Dict
import io
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Preprocesses images for optimal OCR accuracy.
    Implements a multi-step pipeline including:
    - Image quality validation (resolution, sharpness, brightness, contrast)
    - Grayscale conversion
    - Contrast enhancement (CLAHE)
    - Resize (2x upscaling)
    - Adaptive thresholding
    - Orientation detection and correction (contour + Canny edge methods)
    """
    
    def __init__(self):
        # CLAHE parameters for contrast enhancement
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    # ── Image Quality Checking ─────────────────────────────────────────

    def check_quality(self, image_data: bytes) -> Dict:
        """
        Check image quality for OCR suitability.
        
        Checks:
        - Resolution >= 300x300
        - Laplacian variance > 50 (sharpness / blur detection)
        - Brightness mean in range 30-225
        - Standard deviation > 30 (contrast)
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with is_valid, score (0-100), issues list, and metrics
        """
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {"is_valid": False, "score": 0, "issues": ["Could not decode image"]}

            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness / Contrast
            mean_brightness = float(np.mean(gray))
            std_dev = float(np.std(gray))
            
            issues = []
            score = 100
            
            if width < 300 or height < 300:
                issues.append(f"Low resolution: {width}x{height} (min 300x300)")
                score -= 30
            
            if laplacian_var < 50:
                issues.append(f"Blurry image: score {laplacian_var:.1f} (min 50)")
                score -= 30
                
            if not (30 <= mean_brightness <= 225):
                issues.append(f"Poor lighting: brightness {mean_brightness:.1f} (range 30-225)")
                score -= 20
                
            if std_dev < 30:
                issues.append(f"Low contrast: {std_dev:.1f} (min 30)")
                score -= 20
            
            result = {
                "is_valid": len(issues) == 0,
                "score": max(0, score),
                "issues": issues,
                "metrics": {
                    "resolution": f"{width}x{height}",
                    "sharpness": round(laplacian_var, 2),
                    "brightness": round(mean_brightness, 1),
                    "contrast": round(std_dev, 1)
                }
            }
            
            if issues:
                logger.warning(f"Image quality issues: {issues}")
            else:
                logger.debug(f"Image quality OK: score={score}, sharpness={laplacian_var:.1f}")
                
            return result
            
        except Exception as e:
            return {"is_valid": False, "score": 0, "issues": [str(e)]}
    
    # ── Core Preprocessing Pipeline ────────────────────────────────────

    def preprocess(self, image_data: bytes) -> np.ndarray:
        """
        Full preprocessing pipeline for OCR
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed image as numpy array
        """
        # Load image
        img = self._load_image(image_data)
        
        # Convert to grayscale
        gray = self._to_grayscale(img)
        
        # Enhance contrast
        enhanced = self._enhance_contrast(gray)
        
        # Resize 2x
        resized = self._resize_2x(enhanced)
        
        # Apply adaptive thresholding
        thresholded = self._adaptive_threshold(resized)
        
        # Detect and correct orientation
        corrected = self._correct_orientation(thresholded)
        
        return corrected
    
    def preprocess_for_display(self, image_data: bytes) -> np.ndarray:
        """
        Light preprocessing that keeps image viewable
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Lightly processed image
        """
        img = self._load_image(image_data)
        gray = self._to_grayscale(img)
        enhanced = self._enhance_contrast(gray)
        resized = self._resize_2x(enhanced)
        return resized
    
    def _load_image(self, image_data: bytes) -> np.ndarray:
        """Load image from bytes"""
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img
    
    def _to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    def _enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """Apply CLAHE contrast enhancement"""
        return self.clahe.apply(gray)
    
    def _resize_2x(self, img: np.ndarray) -> np.ndarray:
        """Resize image to 2x for better OCR"""
        height, width = img.shape[:2]
        return cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
    
    def _adaptive_threshold(self, img: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding"""
        # Use Otsu's binarization
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def _correct_orientation(self, img: np.ndarray) -> np.ndarray:
        """
        Detect and correct image orientation using OpenCV.
        Uses the minimum area rectangle to detect skew.
        """
        try:
            # Find contours
            contours, _ = cv2.findContours(
                cv2.bitwise_not(img), 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            if not contours:
                return img
            
            # Get all contour points
            all_points = np.concatenate(contours)
            
            # Get minimum area rectangle
            rect = cv2.minAreaRect(all_points)
            angle = rect[2]
            
            # Correct angle
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90
            
            # Only rotate if significant skew detected
            if abs(angle) > 1.0:
                height, width = img.shape[:2]
                center = (width // 2, height // 2)
                
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    img, 
                    rotation_matrix, 
                    (width, height),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return rotated
            
            return img
            
        except Exception:
            # If orientation detection fails, return original
            return img
    
    def denoise(self, img: np.ndarray) -> np.ndarray:
        """Apply denoising (optional step)"""
        return cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    
    def deskew(self, img: np.ndarray) -> np.ndarray:
        """
        Deskew using text line detection (dark pixel coordinates).
        """
        coords = np.column_stack(np.where(img < 128))
        if len(coords) < 100:
            return img
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        if abs(angle) > 0.5:
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
        
        return img
    
    def deskew_canny(self, img: np.ndarray) -> np.ndarray:
        """
        Deskew using Canny edge detection for angle estimation.
        More robust than pixel-coordinate-based deskew for documents
        with complex backgrounds.
        """
        gray = self._to_grayscale(img) if len(img.shape) == 3 else img
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        coords = np.column_stack(np.where(edges > 0))
        
        if len(coords) == 0:
            return img
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        if abs(angle) > 0.5:
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
        
        return img
