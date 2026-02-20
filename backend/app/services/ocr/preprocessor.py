"""
Image Preprocessing for OCR
"""
import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple
import io


class ImagePreprocessor:
    """
    Preprocesses images for optimal OCR accuracy.
    Implements a multi-step pipeline including:
    - Grayscale conversion
    - Contrast enhancement (CLAHE)
    - Resize (2x upscaling)
    - Adaptive thresholding
    - Orientation detection and correction
    """
    
    def __init__(self):
        # CLAHE parameters for contrast enhancement
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
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
        Alternative deskew method using text line detection
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
