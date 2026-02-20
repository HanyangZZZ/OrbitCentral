"""
Custom token authentication with expiry and cookie support.

Tokens older than TOKEN_TTL_HOURS (default 72h) are rejected and deleted.
Supports reading the token from:
  1. Authorization: Token <key> header (standard DRF)
  2. auth_token cookie (HttpOnly, Secure — for auto-login)
"""
import os

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Configurable via environment — default 72 hours (3 days)
TOKEN_TTL_HOURS = int(os.environ.get('TOKEN_TTL_HOURS', 72))

# Cookie name for auth token
AUTH_COOKIE_NAME = 'auth_token'
# Cookie max age in seconds (matches token TTL)
AUTH_COOKIE_MAX_AGE = TOKEN_TTL_HOURS * 3600


class ExpiringTokenAuthentication(TokenAuthentication):
    """Drop-in replacement for DRF TokenAuthentication with a TTL and cookie support."""

    def authenticate(self, request):
        # Try standard header-based auth first
        auth = super().authenticate(request)
        if auth is not None:
            return auth

        # Fall back to cookie-based auth
        token_key = request.COOKIES.get(AUTH_COOKIE_NAME)
        if token_key:
            return self.authenticate_credentials(token_key)

        return None

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        if TOKEN_TTL_HOURS > 0:
            elapsed = timezone.now() - token.created
            if elapsed.total_seconds() > TOKEN_TTL_HOURS * 3600:
                token.delete()
                raise AuthenticationFailed('Token has expired. Please log in again.')

        return user, token
