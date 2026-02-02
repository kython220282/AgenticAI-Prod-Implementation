"""
Authentication schemas for login, registration, and token management.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    }


class RegisterRequest(BaseModel):
    """User registration schema."""
    
    email: EmailStr = Field(description="User email address")
    username: str = Field(min_length=3, max_length=100, description="Unique username")
    password: str = Field(min_length=8, description="User password")
    full_name: Optional[str] = Field(default=None, max_length=255, description="Full name")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "username": "newuser123",
                "password": "SecurePassword123!",
                "full_name": "John Doe"
            }
        }
    }


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    
    refresh_token: str = Field(description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    
    email: EmailStr = Field(description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    
    token: str = Field(description="Reset token from email")
    new_password: str = Field(min_length=8, description="New password")
