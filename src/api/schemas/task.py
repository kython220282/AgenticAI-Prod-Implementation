"""
Task schemas for task management and tracking.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
import enum

from src.api.schemas.common import BaseSchema, PaginatedResponse


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """Base task schema."""
    
    title: str = Field(min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: int = Field(default=1, ge=0, le=3, description="Task priority (0-3)")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    agent_id: Optional[uuid.UUID] = Field(default=None, description="Agent to execute the task")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Research quantum computing",
                "description": "Find latest developments in quantum computing",
                "priority": 2,
                "agent_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=0, le=3)
    status: Optional[TaskStatus] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseSchema):
    """Task response schema."""
    
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: int
    agent_id: Optional[uuid.UUID] = None
    owner_id: uuid.UUID
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    celery_task_id: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Research quantum computing",
                "description": "Find latest developments",
                "status": "completed",
                "priority": 2,
                "agent_id": "660e8400-e29b-41d4-a716-446655440000",
                "owner_id": "770e8400-e29b-41d4-a716-446655440000",
                "result": {"findings": "..."},
                "started_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T10:05:00Z",
                "created_at": "2024-01-01T09:55:00Z",
                "updated_at": "2024-01-01T10:05:00Z"
            }
        }
    )


class TaskListResponse(PaginatedResponse[TaskResponse]):
    """Paginated list of tasks."""
    pass


class TaskProgressResponse(BaseModel):
    """Task progress response for async tasks."""
    
    task_id: uuid.UUID = Field(description="Task ID")
    status: TaskStatus = Field(description="Current status")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(default=None, description="Progress message")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result if completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "progress": 65,
                "message": "Processing data...",
                "result": None,
                "error": None
            }
        }
    )
