"""ASGI config for server project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.production')

application = get_asgi_application()
