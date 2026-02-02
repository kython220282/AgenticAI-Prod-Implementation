"""
Integration tests for health endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    async def test_basic_health(self, client: AsyncClient):
        """Test basic health endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "redis" in data
    
    async def test_liveness_check(self, client: AsyncClient):
        """Test liveness check endpoint."""
        response = await client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await client.get("/metrics")
        
        assert response.status_code == 200
        # Prometheus metrics are plain text
        assert "fastapi" in response.text.lower() or "python" in response.text.lower()
