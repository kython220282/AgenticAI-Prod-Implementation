"""
Celery tasks package.

Organizes background tasks into modules:
- agent: Agent execution tasks
- ml: Machine learning tasks
- data: Data processing tasks
- maintenance: System maintenance tasks
- monitoring: Monitoring and metrics tasks
"""

from src.api.celery_app import celery_app

__all__ = ["celery_app"]
