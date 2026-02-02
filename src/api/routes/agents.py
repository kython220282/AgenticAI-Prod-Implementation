"""Agent Management Routes"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..auth import get_current_user

router = APIRouter()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class AgentCreate(BaseModel):
    """Create agent request."""
    name: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., pattern="^(autonomous|learning|reasoning|collaborative|llm)$")
    config: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class AgentUpdate(BaseModel):
    """Update agent request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|paused|stopped)$")


class AgentResponse(BaseModel):
    """Agent response."""
    agent_id: str
    name: str
    agent_type: str
    status: str
    config: Dict[str, Any]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    user_id: str


class AgentAction(BaseModel):
    """Agent action request."""
    observation: Any
    context: Optional[Dict[str, Any]] = None


class AgentActionResponse(BaseModel):
    """Agent action response."""
    action: Any
    reasoning: Optional[str]
    confidence: float
    metadata: Dict[str, Any]


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new agent.
    
    Args:
        agent_data: Agent configuration
        current_user: Authenticated user
        
    Returns:
        Created agent data
    """
    # In production, save to database
    import uuid
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    
    now = datetime.utcnow()
    
    return {
        "agent_id": agent_id,
        "name": agent_data.name,
        "agent_type": agent_data.agent_type,
        "status": "active",
        "config": agent_data.config,
        "description": agent_data.description,
        "created_at": now,
        "updated_at": now,
        "user_id": current_user["user_id"]
    }


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    List all agents for the current user.
    
    Args:
        current_user: Authenticated user
        agent_type: Optional filter by type
        status: Optional filter by status
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        List of agents
    """
    # In production, query from database with filters
    # Return mock data
    return []


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get agent by ID.
    
    Args:
        agent_id: Agent identifier
        current_user: Authenticated user
        
    Returns:
        Agent data
        
    Raises:
        HTTPException: If agent not found
    """
    # In production, query from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent {agent_id} not found"
    )


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update agent configuration.
    
    Args:
        agent_id: Agent identifier
        agent_data: Updated agent data
        current_user: Authenticated user
        
    Returns:
        Updated agent data
    """
    # In production, update in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent {agent_id} not found"
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
    """
    Delete an agent.
    
    Args:
        agent_id: Agent identifier
        current_user: Authenticated user
        
    Raises:
        HTTPException: If agent not found
    """
    # In production, delete from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent {agent_id} not found"
    )


@router.post("/{agent_id}/act", response_model=AgentActionResponse)
async def agent_action(
    agent_id: str,
    action_data: AgentAction,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Execute an action with the agent.
    
    Args:
        agent_id: Agent identifier
        action_data: Observation and context for agent
        current_user: Authenticated user
        
    Returns:
        Agent's action/response
    """
    # In production, load agent and execute action
    # This would integrate with the agent classes in src/agents/
    
    return {
        "action": "Demo response - agent would process this in production",
        "reasoning": "Mock reasoning",
        "confidence": 0.85,
        "metadata": {
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get agent statistics and metrics.
    
    Args:
        agent_id: Agent identifier
        current_user: Authenticated user
        
    Returns:
        Agent statistics
    """
    # In production, aggregate metrics from database
    return {
        "agent_id": agent_id,
        "total_actions": 0,
        "success_rate": 0.0,
        "average_confidence": 0.0,
        "total_tokens_used": 0,
        "total_cost": 0.0
    }
