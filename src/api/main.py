"""
FastAPI Main Application

This module defines the main FastAPI application with:
- API routes and endpoints
- Middleware configuration
- Exception handlers
- Startup/shutdown events
- Health checks
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.auth import AuthMiddleware
from .routes import agents, health, auth, tasks
from .database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Agentic AI API...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Agentic AI API...")
    await close_db()
    logger.info("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Agentic AI API",
    description="Production-ready API for intelligent autonomous agent systems",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan
)

# ==========================================
# MIDDLEWARE CONFIGURATION
# ==========================================

# CORS - Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"]
)

# GZip - Compress responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host - Prevent host header attacks
if settings.APP_ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# ==========================================
# PROMETHEUS METRICS
# ==========================================
if settings.PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("📊 Prometheus metrics enabled at /metrics")

# ==========================================
# EXCEPTION HANDLERS
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.APP_DEBUG else "An unexpected error occurred",
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": str(exc)
        }
    )


# ==========================================
# ROUTES
# ==========================================

# Health check endpoints
app.include_router(health.router, prefix="/health", tags=["Health"])

# Authentication endpoints
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])

# Agent management endpoints
app.include_router(agents.router, prefix=f"{settings.API_PREFIX}/agents", tags=["Agents"])

# Task management endpoints
app.include_router(tasks.router, prefix=f"{settings.API_PREFIX}/tasks", tags=["Tasks"])


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    API root endpoint.
    
    Returns basic API information and available endpoints.
    """
    return {
        "name": "Agentic AI API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.APP_ENV,
        "docs": f"{settings.API_PREFIX}/docs" if settings.APP_DEBUG else None,
        "health": "/health",
        "endpoints": {
            "agents": f"{settings.API_PREFIX}/agents",
            "tasks": f"{settings.API_PREFIX}/tasks",
            "auth": f"{settings.API_PREFIX}/auth"
        }
    }


# ==========================================
# STARTUP MESSAGE
# ==========================================

@app.on_event("startup")
async def startup_message():
    """Display startup information."""
    logger.info("=" * 60)
    logger.info("🤖 AGENTIC AI - Production API")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Host: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"Debug Mode: {settings.APP_DEBUG}")
    logger.info(f"API Prefix: {settings.API_PREFIX}")
    logger.info(f"CORS Enabled: {len(settings.CORS_ORIGINS)} origins")
    logger.info(f"Rate Limiting: {settings.RATE_LIMIT_ENABLED}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
