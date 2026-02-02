"""
Agent model for storing agent definitions and configurations.
"""

from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from src.api.models.base import Base


class Agent(Base):
    """Agent model for storing agent configurations."""
    
    __tablename__ = "agents"
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration stored as JSONB
    config = Column(JSONB, default={}, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Owner relationship
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
    
    # Relationships
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Agent(name={self.name}, type={self.type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with config."""
        data = super().to_dict()
        data['config'] = self.config or {}
        return data
