from rest_framework.routers import DefaultRouter

from .viewsets import (
    AuthViewSet, BookmarkViewSet, BusinessViewSet, CategoryViewSet,
    ReviewViewSet, TagViewSet, AIReviewViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')
router.register('businesses', BusinessViewSet, basename='business')
router.register('reviews', ReviewViewSet, basename='review')
router.register('bookmarks', BookmarkViewSet, basename='bookmark')
router.register('auth', AuthViewSet, basename='auth')
router.register('ai-reviews', AIReviewViewSet, basename='ai-review')

urlpatterns = router.urls
