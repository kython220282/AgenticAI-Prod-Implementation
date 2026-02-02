"""
Unit tests for authentication functionality.
"""

import pytest
from httpx import AsyncClient

from src.api.auth import create_access_token, verify_password, hash_password


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuth:
    """Test authentication functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
    
    def test_verify_password_invalid(self):
        """Test password verification with wrong password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert not verify_password("WrongPassword", hashed)
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication API endpoints."""
    
    async def test_register_user(self, client: AsyncClient, test_user_data: dict):
        """Test user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
    
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user_data: dict
    ):
        """Test registration with duplicate email."""
        # Register first user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register again with same email
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
    
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful login."""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(
        self,
        client: AsyncClient,
        test_user_data: dict
    ):
        """Test login with invalid credentials."""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    async def test_get_current_user(
        self,
        authenticated_client: tuple[AsyncClient, dict]
    ):
        """Test getting current user info."""
        client, _ = authenticated_client
        
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
    
    async def test_logout(self, authenticated_client: tuple[AsyncClient, dict]):
        """Test logout."""
        client, _ = authenticated_client
        
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200
