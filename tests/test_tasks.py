"""
Unit tests for task functionality.
"""

import pytest
from httpx import AsyncClient
import uuid


@pytest.mark.integration
@pytest.mark.asyncio
class TestTaskAPI:
    """Test task API endpoints."""
    
    async def test_create_task(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test task creation."""
        client, _ = authenticated_client
        
        response = await client.post("/api/v1/tasks", json=test_task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_task_data["title"]
        assert data["status"] == "pending"
        assert "id" in data
    
    async def test_list_tasks(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test listing tasks."""
        client, _ = authenticated_client
        
        # Create tasks
        await client.post("/api/v1/tasks", json=test_task_data)
        await client.post("/api/v1/tasks", json={**test_task_data, "title": "Task 2"})
        
        # List tasks
        response = await client.get("/api/v1/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 2
    
    async def test_get_task(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test getting a specific task."""
        client, _ = authenticated_client
        
        # Create task
        create_response = await client.post("/api/v1/tasks", json=test_task_data)
        task_id = create_response.json()["id"]
        
        # Get task
        response = await client.get(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == test_task_data["title"]
    
    async def test_update_task(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test updating a task."""
        client, _ = authenticated_client
        
        # Create task
        create_response = await client.post("/api/v1/tasks", json=test_task_data)
        task_id = create_response.json()["id"]
        
        # Update task
        update_data = {"title": "Updated Task Title", "priority": 2}
        response = await client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["priority"] == 2
    
    async def test_cancel_task(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test cancelling a task."""
        client, _ = authenticated_client
        
        # Create task
        create_response = await client.post("/api/v1/tasks", json=test_task_data)
        task_id = create_response.json()["id"]
        
        # Cancel task
        response = await client.delete(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    async def test_filter_tasks_by_status(
        self,
        authenticated_client: tuple[AsyncClient, dict],
        test_task_data: dict
    ):
        """Test filtering tasks by status."""
        client, _ = authenticated_client
        
        # Create tasks
        await client.post("/api/v1/tasks", json=test_task_data)
        
        # Filter by status
        response = await client.get("/api/v1/tasks?status=pending")
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "pending" for item in data["items"])
