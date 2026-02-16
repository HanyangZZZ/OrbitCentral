"""
FBLC Django project package.

Import the Celery app here so it's loaded when Django starts.
This ensures @shared_task decorators in api/tasks.py register properly.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)