"""
User model for authentication and authorization.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from src.api.models.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    # Basic information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Role
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # API key for programmatic access
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    
    # Login tracking
    last_login = Column(DateTime, nullable=True)
    login_count = Column(String, default="0")
    
    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        try:
            self.login_count = str(int(self.login_count) + 1)
        except (ValueError, TypeError):
            self.login_count = "1"
