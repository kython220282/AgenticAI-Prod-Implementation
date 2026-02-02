"""
APIKey model for programmatic API access.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from src.api.models.base import Base


class APIKey(Base):
    """API key for programmatic access."""
    
    __tablename__ = "api_keys"
    
    # Key hash (never store raw key)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Key information
    name = Column(String(255), nullable=True)
    prefix = Column(String(16), nullable=True)  # Store first few chars for identification
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="api_keys")
    
    # Permissions and scopes
    scopes = Column(JSONB, default=[], nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(String, default="0")
    
    # Rate limiting (requests per minute)
    rate_limit = Column(String, nullable=True)
    
    def __repr__(self) -> str:
        return f"<APIKey(name={self.name}, prefix={self.prefix})>"
    
    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if key is valid and active."""
        return self.is_active and not self.is_expired() and not self.is_deleted
    
    def record_usage(self) -> None:
        """Record key usage."""
        self.last_used_at = datetime.utcnow()
        try:
            self.usage_count = str(int(self.usage_count) + 1)
        except (ValueError, TypeError):
            self.usage_count = "1"
    
    def has_scope(self, scope: str) -> bool:
        """Check if key has specific scope."""
        if not self.scopes:
            return False
        return scope in self.scopes or "*" in self.scopes
