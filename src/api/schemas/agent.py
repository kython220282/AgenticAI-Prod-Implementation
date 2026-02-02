"""
Agent schemas for agent configuration and execution.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

from src.api.schemas.common import BaseSchema, PaginatedResponse


class AgentBase(BaseModel):
    """Base agent schema."""
    
    name: str = Field(min_length=1, max_length=255, description="Agent name")
    type: str = Field(min_length=1, max_length=50, description="Agent type")
    description: Optional[str] = Field(default=None, description="Agent description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    is_active: bool = Field(default=True, description="Whether agent is active")


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Research Assistant",
                "type": "research",
                "description": "Agent for conducting research tasks",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "is_active": True
            }
        }
    )


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class AgentResponse(BaseSchema):
    """Agent response schema."""
    
    name: str
    type: str
    description: Optional[str] = None
    config: Dict[str, Any]
    is_active: bool
    owner_id: uuid.UUID
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Research Assistant",
                "type": "research",
                "description": "Agent for conducting research tasks",
                "config": {"model": "gpt-4", "temperature": 0.7},
                "is_active": True,
                "owner_id": "660e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class AgentListResponse(PaginatedResponse[AgentResponse]):
    """Paginated list of agents."""
    pass


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent."""
    
    task: str = Field(min_length=1, description="Task description for the agent")
    async_execution: bool = Field(default=False, description="Execute asynchronously")
    config_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Temporary config overrides for this execution"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task": "Research the latest developments in quantum computing",
                "async_execution": True,
                "config_override": {"temperature": 0.5}
            }
        }
    )


class AgentExecuteResponse(BaseModel):
    """Response from agent execution."""
    
    execution_id: uuid.UUID = Field(description="Execution ID")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Execution result (sync only)")
    task_id: Optional[uuid.UUID] = Field(default=None, description="Task ID (async only)")
    status: str = Field(description="Execution status")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in milliseconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "execution_id": "770e8400-e29b-41d4-a716-446655440000",
                "result": {"answer": "Quantum computing advances..."},
                "status": "completed",
                "duration_ms": 1250
            }
        }
    )


class AgentStatsResponse(BaseModel):
    """Agent statistics response."""
    
    total_executions: int = Field(description="Total number of executions")
    successful_executions: int = Field(description="Number of successful executions")
    failed_executions: int = Field(description="Number of failed executions")
    average_duration_ms: float = Field(description="Average execution duration")
    total_tokens_used: int = Field(description="Total tokens consumed")
    total_cost_usd: float = Field(description="Total cost in USD")
    last_executed_at: Optional[datetime] = Field(default=None, description="Last execution timestamp")
