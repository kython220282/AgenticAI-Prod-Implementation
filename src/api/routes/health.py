"""Health Check Routes"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time
import psutil

router = APIRouter()

# Track startup time
startup_time = time.time()


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns service status and uptime.
    """
    uptime = time.time() - startup_time
    
    return {
        "status": "healthy",
        "service": "agenticai-api",
        "uptime_seconds": round(uptime, 2),
        "timestamp": time.time()
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/Docker.
    
    Returns whether service is ready to accept traffic.
    """
    # Add checks for dependencies (database, Redis, etc.)
    # For now, return ready if service is up
    
    return {
        "ready": True,
        "checks": {
            "api": "ok",
            # Add database, Redis checks here
        }
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/Docker.
    
    Returns whether service is alive (should not be restarted).
    """
    return {
        "alive": True,
        "timestamp": time.time()
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def system_metrics() -> Dict[str, Any]:
    """
    Get system resource metrics.
    
    Returns CPU, memory, and disk usage.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count()
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": disk.percent
        },
        "uptime_seconds": round(time.time() - startup_time, 2)
    }
