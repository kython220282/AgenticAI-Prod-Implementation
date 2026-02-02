"""
AgentExecution model for detailed execution logs and metrics.
"""

from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Integer, Text, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from src.api.models.base import Base


class AgentExecution(Base):
    """Detailed execution log for agent runs."""
    
    __tablename__ = "agent_executions"
    
    # Agent relationship
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    agent = relationship("Agent", back_populates="executions")
    
    # Task relationship
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    task = relationship("Task", back_populates="executions")
    
    # Input and output data
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    
    # Execution status
    status = Column(String(50), nullable=True, index=True)
    
    # Performance metrics
    duration_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 4), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSONB, default={}, nullable=False)
    
    def __repr__(self) -> str:
        return f"<AgentExecution(agent_id={self.agent_id}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all data."""
        data = super().to_dict()
        data['input_data'] = self.input_data or {}
        data['output_data'] = self.output_data or {}
        data['metadata'] = self.metadata or {}
        if self.cost_usd is not None:
            data['cost_usd'] = float(self.cost_usd)
        return data
