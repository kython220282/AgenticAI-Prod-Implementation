"""Task Management Routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ..auth import get_current_user

router = APIRouter()


# ==========================================
# ENUMS & MODELS
# ==========================================

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    """Create task request."""
    agent_id: str
    task_type: str = Field(..., min_length=1)
    input_data: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)
    timeout_seconds: Optional[int] = Field(default=300, ge=1, le=3600)


class TaskResponse(BaseModel):
    """Task response."""
    task_id: str
    agent_id: str
    task_type: str
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error: Optional[str]
    priority: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    user_id: str


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new asynchronous task.
    
    Args:
        task_data: Task configuration
        current_user: Authenticated user
        
    Returns:
        Created task data
    """
    import uuid
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    
    # In production, queue this task with Celery
    
    return {
        "task_id": task_id,
        "agent_id": task_data.agent_id,
        "task_type": task_data.task_type,
        "status": TaskStatus.PENDING,
        "input_data": task_data.input_data,
        "output_data": None,
        "error": None,
        "priority": task_data.priority,
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "user_id": current_user["user_id"]
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get task status and result.
    
    Args:
        task_id: Task identifier
        current_user: Authenticated user
        
    Returns:
        Task data
    """
    # In production, query from database or Celery result backend
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List tasks for the current user.
    
    Args:
        current_user: Authenticated user
        agent_id: Optional filter by agent
        status: Optional filter by status
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of tasks
    """
    # In production, query from database
    return []


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Cancel a pending or running task.
    
    Args:
        task_id: Task identifier
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    # In production, revoke Celery task
    return {"message": f"Task {task_id} cancelled"}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
    """
    Delete task record.
    
    Args:
        task_id: Task identifier
        current_user: Authenticated user
    """
    # In production, delete from database
    pass
