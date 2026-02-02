"""Routes package initialization"""

from .health import router as health_router
from .auth import router as auth_router
from .agents import router as agents_router
from .tasks import router as tasks_router

__all__ = [
    "health",
    "auth",
    "agents",
    "tasks"
]
