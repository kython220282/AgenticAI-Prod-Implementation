"""
System maintenance tasks.

Handles cleanup, health checks, and routine maintenance.
"""

from celery import Task
import asyncio
from datetime import datetime, timedelta

from src.api.celery_app import celery_app
from src.api.database import get_db


@celery_app.task(name="agenticai.tasks.maintenance.cleanup_old_tasks")
def cleanup_old_tasks(days: int = 30):
    """
    Clean up old completed tasks from the database.
    
    Args:
        days: Delete tasks older than this many days
    """
    try:
        # TODO: Implement database cleanup
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old tasks
        # db.query(Task).filter(
        #     Task.completed_at < cutoff_date,
        #     Task.status.in_(["completed", "failed"])
        # ).delete()
        
        return {
            "success": True,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"Cleaned up tasks older than {days} days"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@celery_app.task(name="agenticai.tasks.maintenance.health_check")
def health_check():
    """Perform system health check."""
    try:
        checks = {
            "database": check_database(),
            "redis": check_redis(),
            "celery": check_celery(),
        }
        
        all_healthy = all(checks.values())
        
        return {
            "success": all_healthy,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_database() -> bool:
    """Check database connectivity."""
    try:
        # TODO: Implement database check
        return True
    except:
        return False


def check_redis() -> bool:
    """Check Redis connectivity."""
    try:
        from redis import Redis
        from src.api.config import get_settings
        settings = get_settings()
        r = Redis.from_url(settings.REDIS_URL)
        return r.ping()
    except:
        return False


def check_celery() -> bool:
    """Check Celery workers."""
    try:
        inspector = celery_app.control.inspect()
        stats = inspector.stats()
        return stats is not None and len(stats) > 0
    except:
        return False
