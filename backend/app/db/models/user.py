"""
NutriLens Backend - User Model

User entity for authentication and profile management.
"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.file_asset import FileAsset
    from app.db.models.scan import Scan


class User(Base):
    """User model for authentication and profiles."""
    
    __tablename__ = "users"
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Profile
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_file_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("file_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    goal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    avatar: Mapped[Optional["FileAsset"]] = relationship(
        "FileAsset",
        foreign_keys=[avatar_file_id],
        lazy="joined",
    )
    scans: Mapped[list["Scan"]] = relationship(
        "Scan",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    files: Mapped[list["FileAsset"]] = relationship(
        "FileAsset",
        back_populates="owner",
        foreign_keys="FileAsset.owner_user_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
