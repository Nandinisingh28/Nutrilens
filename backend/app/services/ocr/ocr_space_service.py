"""
OCR.space Cloud OCR Service
Free OCR API — 500 requests/day, no payment required.
Uses Engine 2 with isTable=true for best nutrition label accuracy.
"""
import requests
import base64
import logging
import io
from typing import Optional

logger = logging.getLogger(__name__)


class OCRSpaceOCR:
    """
    OCR.space API client for text extraction from images.
    
    Features:
        - Engine 2: optimized for structured text / tables
        - isTable mode: preserves line-by-line table structure
        - 500 free requests/day
        - Auto-compresses images to stay under 1MB free-tier limit
    """
    
    API_URL = "https://api.ocr.space/parse/image"
    MAX_IMAGE_SIZE = 500_000  # ~500KB to stay under 1MB limit & process faster in cloud
    
    def __init__(self, api_key: str = ""):
        """
        Initialize OCR.space client.
        
        Args:
            api_key: Free API key from https://ocr.space/ocrapi/freekey
        """
        self.api_key = api_key
        self._available = bool(api_key)
        if not api_key:
            logger.warning("OCR.space API key not configured — will use Tesseract fallback")
    
    @property
    def is_available(self) -> bool:
        """Check if OCR.space is configured and available."""
        return self._available
    
    def _compress_image(self, image_bytes: bytes) -> bytes:
        """
        Compress and resize image to stay under 1MB free-tier limit.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Compressed JPEG bytes
        """
        try:
            from PIL import Image
            
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if needed (JPEG doesn't support alpha)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 2000px on longest side)
            max_dimension = 2000
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                logger.debug(f"Resized image to {new_size}")
            
            # Compress as JPEG with decreasing quality until under limit
            for quality in [85, 70, 55, 40]:
                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=quality, optimize=True)
                compressed = buf.getvalue()
                if len(compressed) <= self.MAX_IMAGE_SIZE:
                    logger.debug(f"Compressed to {len(compressed)} bytes (quality={quality})")
                    return compressed
            
            # Last resort: resize more aggressively
            ratio = 0.5
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=40, optimize=True)
            compressed = buf.getvalue()
            logger.debug(f"Aggressively compressed to {len(compressed)} bytes")
            return compressed
            
        except Exception as e:
            logger.warning(f"Image compression failed: {e}, using original")
            return image_bytes
    
    def detect_text(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract text from an image using OCR.space API.
        
        Args:
            image_bytes: Raw image bytes (JPEG/PNG)
            
        Returns:
            Extracted text string, or None if failed
        """
        if not self._available:
            logger.info("OCR.space not available (no API key)")
            return None
        
        try:
            # Compress image to stay under 1MB free-tier limit
            original_size = len(image_bytes)
            if original_size > self.MAX_IMAGE_SIZE:
                logger.info(f"Image too large ({original_size} bytes), compressing...")
                image_bytes = self._compress_image(image_bytes)
            
            # Base64 encode the image
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine image type
            img_type = "image/jpeg"
            if image_bytes[:4] == b'\x89PNG':
                img_type = "image/png"
            
            payload = {
                'apikey': self.api_key,
                'base64Image': f"data:{img_type};base64,{img_b64}",
                'OCREngine': '2',          # Engine 2: better for tables
                'isTable': 'true',         # Preserve table structure
                'scale': 'true',           # Auto-scale for better accuracy
                'detectOrientation': 'true',
                'language': 'eng',
            }
            
            logger.info(f"Sending image to OCR.space API ({len(image_bytes)} bytes, Engine 2, isTable=true)...")
            
            response = requests.post(
                self.API_URL,
                data=payload,
                timeout=20  # Fast-fail Free Tier timeout
            )
            
            if response.status_code != 200:
                logger.error(f"OCR.space HTTP error: {response.status_code}")
                return None
            
            result = response.json()
            
            # Check for API-level errors
            if result.get('IsErroredOnProcessing', False):
                error_msg = result.get('ErrorMessage', ['Unknown error'])
                logger.error(f"OCR.space processing error: {error_msg}")
                return None
            
            # Extract text from all parsed results
            parsed_results = result.get('ParsedResults', [])
            if not parsed_results:
                logger.warning("OCR.space returned no parsed results")
                return None
            
            # Combine text from all parsed results
            all_text = []
            for pr in parsed_results:
                text = pr.get('ParsedText', '')
                if text:
                    all_text.append(text.strip())
            
            combined_text = '\n'.join(all_text)
            
            if combined_text:
                logger.info(f"OCR.space extracted {len(combined_text)} chars of text")
                logger.debug(f"OCR.space text preview: {combined_text[:200]}...")
            else:
                logger.warning("OCR.space returned empty text")
                return None
            
            return combined_text
            
        except requests.exceptions.Timeout:
            logger.error("OCR.space request timed out (60s)")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("OCR.space connection failed — check internet connectivity")
            return None
        except Exception as e:
            logger.error(f"OCR.space unexpected error: {e}")
            return None
