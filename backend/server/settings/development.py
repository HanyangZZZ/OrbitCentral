"""
Development-specific settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '0.0.0.0']

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Browsable API available in dev
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Disable throttling in development
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []  # noqa: F405

# SQL query logging — change level to 'DEBUG' to see every query
LOGGING['loggers']['django.db.backends'] = {  # noqa: F405
    'handlers': ['console'],
    'level': 'WARNING',
    'propagate': False,
}
