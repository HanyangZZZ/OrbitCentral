"""
ViewSets package — DRF API endpoints.
"""
from .tags import TagViewSet
from .categories import CategoryViewSet
from .businesses import BusinessViewSet
from .reviews import ReviewViewSet
from .bookmarks import BookmarkViewSet
from .auth import AuthViewSet
from .ai_reviews import AIReviewViewSet

__all__ = [
    'TagViewSet', 'CategoryViewSet', 'BusinessViewSet',
    'ReviewViewSet', 'BookmarkViewSet', 'AuthViewSet',
    'AIReviewViewSet',
]
