"""Authentication Routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any

from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)

router = APIRouter()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User data response."""
    user_id: str
    email: str
    full_name: str
    roles: list


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user data
    """
    # In production, save to database
    # For now, return mock response
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user (mock)
    user_id = "usr_" + user_data.email.split("@")[0]
    
    return {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "roles": ["user"]
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> Dict[str, Any]:
    """
    User login endpoint.
    
    Args:
        credentials: User login credentials
        
    Returns:
        JWT tokens
    """
    # In production, verify against database
    # For now, accept any credentials for demo
    
    # Create tokens
    token_data = {
        "sub": "usr_demo",
        "email": credentials.email,
        "roles": ["user"],
        "permissions": ["read", "write"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New access token
    """
    try:
        payload = decode_token(refresh_token)
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new tokens
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }
        
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        User information
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": "Demo User",  # Would come from database
        "roles": current_user.get("roles", [])
    }


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    User logout endpoint.
    
    In a production system, you would:
    - Blacklist the token
    - Remove from Redis cache
    - Clear session data
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    # In production, blacklist the token
    return {"message": "Successfully logged out"}
