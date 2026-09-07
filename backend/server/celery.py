"""
Celery application configuration for OrbitCentral.

This module creates the Celery app and configures it to:
  1. Read settings from Django's settings (CELERY_* namespace)
  2. Auto-discover tasks from all installed Django apps

Usage:
  - Workers are started via: celery -A server worker -l info
  - Beat (scheduler) via: celery -A server beat -l info
  - Flower (monitoring) via: celery -A server flower

The app is imported in server/__init__.py so Django loads it on startup.
"""
import os

from celery import Celery

# Default to production settings; overridden by DJANGO_SETTINGS_MODULE env var
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.production')

app = Celery('server')

# Read config from Django settings, using the CELERY_ namespace.
# e.g. CELERY_BROKER_URL in settings → broker_url in Celery.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in all INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Simple debug task — prints the request info."""
    print(f'Request: {self.request!r}')
