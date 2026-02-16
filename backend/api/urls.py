from rest_framework.routers import DefaultRouter

from .viewsets import BusinessViewSet, CategoryViewSet, TagViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')
router.register('businesses', BusinessViewSet, basename='business')

urlpatterns = router.urls
