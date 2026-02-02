"""
Common schemas used across the API.
"""

from typing import Any, Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Maximum items returned")
    has_more: bool = Field(description="Whether more items exist")
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(description="Response message")
    detail: Optional[str] = Field(default=None, description="Additional details")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    id: uuid.UUID = Field(description="Unique identifier")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(description="Service status (healthy/unhealthy)")
    version: str = Field(description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Optional[dict[str, bool]] = Field(default=None, description="Status of dependent services")
