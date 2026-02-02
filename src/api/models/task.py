"""
Task model for tracking agent tasks and their execution.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import enum

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from src.api.models.base import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, enum.Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class Task(Base):
    """Task model for agent execution tracking."""
    
    __tablename__ = "tasks"
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    priority = Column(Integer, default=TaskPriority.NORMAL.value, nullable=False)
    
    # Agent relationship
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    agent = relationship("Agent", back_populates="tasks")
    
    # Owner relationship
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="tasks")
    
    # Results and error handling
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Celery task ID for async tracking
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Relationships
    executions = relationship("AgentExecution", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Task(title={self.title}, status={self.status})>"
    
    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.utcnow()
    
    def complete(self, result: Dict[str, Any]) -> None:
        """Mark task as completed with result."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """Mark task as failed with error message."""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
