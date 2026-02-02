"""
Authentication Middleware

Handles optional authentication for public/private endpoints.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..auth import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authentication handling.
    
    Extracts and validates JWT tokens, attaches user info to request.
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/health/",
        "/health/live",
        "/health/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with optional authentication.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Skip auth for login/register
        if "/auth/login" in request.url.path or "/auth/register" in request.url.path:
            return await call_next(request)
        
        # Try to extract and validate token
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                payload = decode_token(token)
                
                # Attach user info to request state
                request.state.user_id = payload.get("sub")
                request.state.user_email = payload.get("email")
                request.state.user_roles = payload.get("roles", [])
                request.state.authenticated = True
            
            except Exception:
                # Invalid token - endpoint will handle if auth is required
                request.state.authenticated = False
        else:
            request.state.authenticated = False
        
        return await call_next(request)
