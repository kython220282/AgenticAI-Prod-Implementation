"""
SQLAlchemy database models.

This package contains all database models for the application:
- User: User accounts and authentication
- Agent: Agent definitions and configurations
- Task: Task records and execution history
- AgentExecution: Detailed execution logs
- Embedding: Vector embeddings storage
- APIKey: API key management
"""

from src.api.models.base import Base
from src.api.models.user import User
from src.api.models.agent import Agent
from src.api.models.task import Task, TaskStatus
from src.api.models.execution import AgentExecution
from src.api.models.embedding import Embedding
from src.api.models.api_key import APIKey

__all__ = [
    "Base",
    "User",
    "Agent",
    "Task",
    "TaskStatus",
    "AgentExecution",
    "Embedding",
    "APIKey",
]
