"""
NutriLens Backend - FileAsset Model

File storage entity for label images and avatars.
"""

from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class FileKind(str, Enum):
    """File type categories."""
    LABEL_IMAGE = "label_image"
    INGREDIENTS_IMAGE = "ingredients_image"
    NUTRITION_IMAGE = "nutrition_image"
    AVATAR = "avatar"


class FileAsset(Base):
    """File asset model for stored files."""
    
    __tablename__ = "file_assets"
    
    # Ownership
    owner_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="files",
        foreign_keys=[owner_user_id],
    )
    
    # File metadata
    kind: Mapped[FileKind] = mapped_column(
        SQLEnum(FileKind),
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<FileAsset {self.id} - {self.kind}>"
