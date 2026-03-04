"""
Application Configuration
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "nutrilens"
    mysql_password: str = "nutrilens_secret_2024"
    mysql_database: str = "nutrilens_db"
    
    # JWT
    jwt_secret_key: str = "nutrilens_jwt_super_secret_key_2024_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # File uploads
    upload_dir: str = "/app/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Email (Gmail SMTP)
    smtp_email: str = ""        # Your Gmail address
    smtp_password: str = ""     # Gmail App Password (not your regular password)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    # Frontend URL (for reset links)
    frontend_url: str = "http://localhost:3000"
    
    # OCR
    ocr_provider: str = "ocr_space"  # "ocr_space" or "tesseract"
    ocr_space_api_key: str = ""      # Free key from https://ocr.space/ocrapi/freekey
    
    @property
    def database_url(self) -> str:
        """Construct MySQL database URL"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
