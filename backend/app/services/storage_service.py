"""
NutriLens Backend - Storage Service

File storage management (local and cloud-ready).
"""

import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Service for file storage operations."""
    
    def __init__(self):
        self.storage_type = "local"  # Can be extended to "s3", "gcs", etc.
        self.base_path = Path(settings.UPLOAD_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "images").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)
    
    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        subfolder: str = "images",
    ) -> str:
        """
        Save a file to storage.
        
        Args:
            file_content: File content as bytes
            filename: Name to save file as
            subfolder: Subfolder within storage
        
        Returns:
            Full path to saved file
        """
        folder = self.base_path / subfolder
        folder.mkdir(exist_ok=True)
        
        file_path = folder / filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        
        return str(file_path)
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Get file content from storage.
        
        Args:
            file_path: Path to file
        
        Returns:
            File content as bytes, or None if not found
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        with open(path, "rb") as f:
            return f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if deleted, False otherwise
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        try:
            os.remove(path)
            logger.info(f"File deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def copy_file(
        self,
        source_path: str,
        dest_filename: str,
        subfolder: str = "images",
    ) -> str:
        """
        Copy a file within storage.
        
        Args:
            source_path: Source file path
            dest_filename: Destination filename
            subfolder: Destination subfolder
        
        Returns:
            Path to copied file
        """
        dest_folder = self.base_path / subfolder
        dest_folder.mkdir(exist_ok=True)
        
        dest_path = dest_folder / dest_filename
        
        shutil.copy2(source_path, dest_path)
        
        logger.info(f"File copied: {source_path} -> {dest_path}")
        
        return str(dest_path)
    
    def get_file_url(self, file_path: str) -> str:
        """
        Get URL for accessing a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            URL to access file
        """
        # For local storage, return relative path
        # For cloud storage, would return signed URL
        rel_path = Path(file_path).relative_to(self.base_path)
        return f"/uploads/{rel_path}"
