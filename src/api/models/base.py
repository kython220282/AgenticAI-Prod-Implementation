"""
Base model for SQLAlchemy models.

Provides common functionality for all models including:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Soft delete support
- Common utility methods
"""

from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr


class BaseModel:
    """Base model with common fields and methods."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"


Base = declarative_base(cls=BaseModel)
