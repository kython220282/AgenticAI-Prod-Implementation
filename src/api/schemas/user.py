"""
User schemas for user management and profile operations.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
import uuid

from src.api.schemas.common import BaseSchema, PaginatedResponse


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(description="User email address")
    username: str = Field(min_length=3, max_length=100, description="Username")
    full_name: Optional[str] = Field(default=None, max_length=255, description="Full name")
    is_active: bool = Field(default=True, description="Whether user is active")


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default="user", description="User role")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseSchema):
    """User response schema (excludes sensitive data)."""
    
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: str
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
                "role": "user",
                "last_login": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class UserListResponse(PaginatedResponse[UserResponse]):
    """Paginated list of users."""
    pass


class UserStatsResponse(BaseModel):
    """User statistics response."""
    
    total_agents: int = Field(description="Total number of agents owned")
    total_tasks: int = Field(description="Total number of tasks")
    completed_tasks: int = Field(description="Number of completed tasks")
    total_executions: int = Field(description="Total agent executions")
    total_tokens_used: int = Field(description="Total tokens consumed")
    total_cost_usd: float = Field(description="Total cost in USD")
