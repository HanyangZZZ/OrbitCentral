from rest_framework.routers import DefaultRouter

from .viewsets import (
    AutomationLogViewSet,
    BookmarkViewSet,
    BusinessViewSet,
    CategoryViewSet,
    ReviewViewSet,
    RewardViewSet,
    UserCouponViewSet,
    UserProfileViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('profiles', UserProfileViewSet, basename='profile')
router.register('categories', CategoryViewSet, basename='category')
router.register('businesses', BusinessViewSet, basename='business')
router.register('reviews', ReviewViewSet, basename='review')
router.register('bookmarks', BookmarkViewSet, basename='bookmark')
router.register('rewards', RewardViewSet, basename='reward')
router.register('coupons', UserCouponViewSet, basename='coupon')
router.register('automation-logs', AutomationLogViewSet, basename='automation-log')

urlpatterns = router.urls
