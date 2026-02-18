"""
Celery tasks package.

Tasks are the bridge between Django views and background processing.
"""
from .import_task import ensure_area_covered_task
from .email import send_verification_email_task, send_password_reset_email_task

__all__ = [
    'ensure_area_covered_task',
    'send_verification_email_task',
    'send_password_reset_email_task',
]
