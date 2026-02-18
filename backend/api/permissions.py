"""
Custom DRF permissions.
"""
from rest_framework import permissions


class IsEmailVerified(permissions.BasePermission):
    """
    Allows access only to users whose email has been verified.

    Returns a descriptive message so the frontend can prompt verification.
    """
    message = 'You must verify your email address before performing this action.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)
        return profile is not None and profile.email_verified


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only the object's owner can edit/delete it; anyone can read."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
