"""
Custom token authentication with expiry.

Tokens older than TOKEN_TTL_HOURS (default 72h) are rejected and deleted.
"""
import os

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Configurable via environment — default 72 hours (3 days)
TOKEN_TTL_HOURS = int(os.environ.get('TOKEN_TTL_HOURS', 72))


class ExpiringTokenAuthentication(TokenAuthentication):
    """Drop-in replacement for DRF TokenAuthentication with a TTL."""

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        if TOKEN_TTL_HOURS > 0:
            elapsed = timezone.now() - token.created
            if elapsed.total_seconds() > TOKEN_TTL_HOURS * 3600:
                token.delete()
                raise AuthenticationFailed('Token has expired. Please log in again.')

        return user, token
