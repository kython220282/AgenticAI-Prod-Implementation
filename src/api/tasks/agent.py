"""
Agent execution tasks for Celery.

Handles asynchronous agent execution, including:
- Single agent tasks
- Multi-agent collaborations
- Long-running agent workflows
"""

from typing import Dict, Any
import asyncio
from celery import Task

from src.api.celery_app import agent_task
from src.core.factory import AgentFactory
from src.core.protocols import AgentType


class AgentExecutionTask(Task):
    """Base task for agent execution with progress tracking."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        print(f"Task {task_id} failed: {exc}")
        # TODO: Send notification, log to database, etc.
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        print(f"Task {task_id} completed successfully")
        # TODO: Update database, send notification, etc.


@agent_task
def execute_agent_async(
    self,
    agent_type: str,
    task_description: str,
    config: Dict[str, Any] = None,
    user_id: str = None,
) -> Dict[str, Any]:
    """
    Execute an agent asynchronously.
    
    Args:
        agent_type: Type of agent to execute
        task_description: Task for the agent to perform
        config: Agent configuration
        user_id: ID of user who initiated the task
        
    Returns:
        Result dictionary with agent output
    """
    try:
        # Update task state
        self.update_state(
            state="PROCESSING",
            meta={"current": 0, "total": 100, "status": "Initializing agent..."}
        )
        
        # Create agent
        factory = AgentFactory()
        agent = factory.create_agent(
            agent_type=AgentType[agent_type.upper()],
            config=config or {}
        )
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={"current": 30, "total": 100, "status": "Executing task..."}
        )
        
        # Execute task (run async in sync context)
        result = asyncio.run(agent.execute(task_description))
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={"current": 90, "total": 100, "status": "Finalizing results..."}
        )
        
        return {
            "success": True,
            "result": result,
            "agent_type": agent_type,
            "user_id": user_id,
        }
        
    except Exception as e:
        # Retry on failure
        raise self.retry(exc=e, countdown=60, max_retries=3)


@agent_task
def execute_multi_agent_async(
    self,
    agent_configs: list[Dict[str, Any]],
    task_description: str,
    user_id: str = None,
) -> Dict[str, Any]:
    """
    Execute multiple agents collaboratively.
    
    Args:
        agent_configs: List of agent configurations
        task_description: Shared task description
        user_id: ID of user who initiated the task
        
    Returns:
        Combined results from all agents
    """
    try:
        results = []
        total_agents = len(agent_configs)
        
        for idx, config in enumerate(agent_configs):
            # Update progress
            self.update_state(
                state="PROCESSING",
                meta={
                    "current": int((idx / total_agents) * 100),
                    "total": 100,
                    "status": f"Processing agent {idx + 1}/{total_agents}..."
                }
            )
            
            # Execute agent
            result = execute_agent_async.apply_async(
                kwargs={
                    "agent_type": config["type"],
                    "task_description": task_description,
                    "config": config.get("config", {}),
                    "user_id": user_id,
                }
            ).get()
            
            results.append(result)
        
        return {
            "success": True,
            "results": results,
            "total_agents": total_agents,
            "user_id": user_id,
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)


@agent_task
def batch_agent_execution(
    self,
    agent_type: str,
    tasks: list[str],
    config: Dict[str, Any] = None,
    user_id: str = None,
) -> Dict[str, Any]:
    """
    Execute an agent on multiple tasks in batch.
    
    Args:
        agent_type: Type of agent to use
        tasks: List of task descriptions
        config: Agent configuration
        user_id: ID of user who initiated the task
        
    Returns:
        List of results for each task
    """
    try:
        results = []
        total_tasks = len(tasks)
        
        factory = AgentFactory()
        agent = factory.create_agent(
            agent_type=AgentType[agent_type.upper()],
            config=config or {}
        )
        
        for idx, task in enumerate(tasks):
            # Update progress
            self.update_state(
                state="PROCESSING",
                meta={
                    "current": int((idx / total_tasks) * 100),
                    "total": 100,
                    "status": f"Processing task {idx + 1}/{total_tasks}..."
                }
            )
            
            # Execute task
            result = asyncio.run(agent.execute(task))
            results.append({
                "task": task,
                "result": result,
                "success": True,
            })
        
        return {
            "success": True,
            "results": results,
            "total_tasks": total_tasks,
            "user_id": user_id,
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
