"""
Rate Limiting Middleware

Implements request rate limiting using Redis.
"""

import time
import hashlib
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis

from ..config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    
    Uses Redis for distributed rate limiting with sliding window algorithm.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.enabled = settings.RATE_LIMIT_ENABLED
        
        if self.enabled:
            try:
                self.redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
            except Exception:
                # Fallback to in-memory if Redis not available
                self.enabled = False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        if not self.enabled:
            return await call_next(request)
        
        # Get client identifier (IP or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(client_id)
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {reset_time} seconds.",
                    "retry_after": reset_time
                },
                headers={
                    "X-RateLimit-Limit": str(settings.API_RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + reset_time),
                    "Retry-After": str(reset_time)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.API_RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get user ID from auth
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            (is_allowed, remaining_requests, reset_in_seconds)
        """
        if not self.redis_client:
            return True, settings.API_RATE_LIMIT_PER_MINUTE, 60
        
        try:
            key = f"ratelimit:{client_id}:minute"
            current_time = int(time.time())
            window_start = current_time - 60
            
            # Use sorted set for sliding window
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, 60)
            
            results = await pipe.execute()
            current_count = results[1]
            
            limit = settings.API_RATE_LIMIT_PER_MINUTE
            is_allowed = current_count < limit
            remaining = max(0, limit - current_count - 1)
            
            return is_allowed, remaining, 60
        
        except Exception:
            # Fail open - allow request if Redis is down
            return True, settings.API_RATE_LIMIT_PER_MINUTE, 60
