"""
Celery application configuration for asynchronous task processing.

This module sets up Celery for background job processing including:
- Agent execution
- Long-running computations
- Scheduled tasks
- Batch processing
"""

from celery import Celery
from celery.schedules import crontab
import os

from src.api.config import get_settings

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "agenticai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        "agenticai.tasks.agent.*": {"queue": "agents"},
        "agenticai.tasks.ml.*": {"queue": "ml"},
        "agenticai.tasks.data.*": {"queue": "data"},
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Cleanup old tasks every day at 2 AM
    "cleanup-old-tasks": {
        "task": "agenticai.tasks.maintenance.cleanup_old_tasks",
        "schedule": crontab(hour=2, minute=0),
    },
    # Health check every 5 minutes
    "health-check": {
        "task": "agenticai.tasks.maintenance.health_check",
        "schedule": crontab(minute="*/5"),
    },
    # Update metrics every hour
    "update-metrics": {
        "task": "agenticai.tasks.monitoring.update_metrics",
        "schedule": crontab(minute=0),
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "src.api.tasks.agent",
    "src.api.tasks.ml",
    "src.api.tasks.data",
    "src.api.tasks.maintenance",
    "src.api.tasks.monitoring",
])


# Task decorators for common patterns
def agent_task(func):
    """Decorator for agent execution tasks."""
    return celery_app.task(
        name=f"agenticai.tasks.agent.{func.__name__}",
        bind=True,
        max_retries=3,
        default_retry_delay=60,
    )(func)


def ml_task(func):
    """Decorator for ML/computation tasks."""
    return celery_app.task(
        name=f"agenticai.tasks.ml.{func.__name__}",
        bind=True,
        time_limit=7200,  # 2 hours for ML tasks
        soft_time_limit=7000,
    )(func)


def data_task(func):
    """Decorator for data processing tasks."""
    return celery_app.task(
        name=f"agenticai.tasks.data.{func.__name__}",
        bind=True,
        max_retries=5,
        default_retry_delay=30,
    )(func)


if __name__ == "__main__":
    celery_app.start()
