"""
Pydantic schemas for request/response validation and documentation.

This package contains all API schemas organized by domain:
- auth: Authentication schemas
- agent: Agent schemas
- task: Task schemas  
- user: User schemas
- common: Common/shared schemas
"""

from src.api.schemas.common import *
from src.api.schemas.user import *
from src.api.schemas.agent import *
from src.api.schemas.task import *
from src.api.schemas.auth import *

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    
    # Agent
    "AgentBase",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentExecuteRequest",
    "AgentExecuteResponse",
    
    # Task
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RegisterRequest",
]
