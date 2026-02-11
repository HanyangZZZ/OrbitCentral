"""
Production-specific settings.
"""
import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# CORS — restrict to your frontend domain(s)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
CORS_ALLOW_ALL_ORIGINS = False

# ── Security hardening ─────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = bool(os.environ.get('SECURE_SSL_REDIRECT', False))

# JSON only (no browsable API)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
]

# Uncomment to require authentication on all endpoints by default:
# REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
#     'rest_framework.permissions.IsAuthenticated',
# ]
