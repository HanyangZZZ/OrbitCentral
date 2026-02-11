"""
DRF ViewSets — one per resource.

Each ViewSet provides list / create / retrieve / update / partial_update / destroy
automatically via ModelViewSet.  Filtering, search, ordering, and pagination are
configured per-ViewSet and rely on the global defaults in settings.REST_FRAMEWORK.
"""
import logging

from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import (
    AutomationLog,
    Bookmark,
    Business,
    Category,
    Review,
    Reward,
    User,
    UserCoupon,
    UserProfile,
)
from .serializers import (
    AutomationLogSerializer,
    BookmarkSerializer,
    BusinessSerializer,
    CategorySerializer,
    ReviewSerializer,
    RewardSerializer,
    UserCouponSerializer,
    UserProfileSerializer,
    UserSerializer,
)

logger = logging.getLogger('api')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('-created_at')
    serializer_class = UserSerializer
    filterset_fields = ['role', 'is_verified_human']
    search_fields = ['email']
    ordering_fields = ['created_at', 'email']


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    filterset_fields = ['high_contrast', 'keyboard_only_nav']
    search_fields = ['display_name', 'user__email']

    def create(self, request, *args, **kwargs):
        """Upsert: if a profile already exists for this user, update it."""
        user_pk = request.data.get('user')
        if user_pk:
            try:
                instance = UserProfile.objects.get(pk=user_pk)
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                logger.info("Profile updated for user %s", user_pk)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except UserProfile.DoesNotExist:
                pass
        return super().create(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    search_fields = ['name', 'slug']


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = (
        Business.objects
        .select_related('owner', 'category')
        .order_by('-avg_rating', 'name')
    )
    serializer_class = BusinessSerializer
    filterset_fields = ['category', 'owner', 'onboarding_status']
    search_fields = ['name', 'contact_email', 'google_place_id']
    ordering_fields = ['avg_rating', 'review_count', 'name', 'created_at']


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = (
        Review.objects
        .select_related('user', 'business')
        .order_by('-created_at')
    )
    serializer_class = ReviewSerializer
    filterset_fields = ['business', 'user', 'rating', 'is_visible']
    search_fields = ['content']
    ordering_fields = ['created_at', 'rating', 'ai_fraud_score']


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = (
        Bookmark.objects
        .select_related('user', 'business')
        .order_by('-created_at')
    )
    serializer_class = BookmarkSerializer
    filterset_fields = ['user', 'business']


class RewardViewSet(viewsets.ModelViewSet):
    queryset = (
        Reward.objects
        .select_related('provider_business', 'trigger_business')
        .order_by('-id')
    )
    serializer_class = RewardSerializer
    filterset_fields = ['provider_business', 'trigger_business', 'reward_type']
    search_fields = ['title']
    ordering_fields = ['expiry_date', 'discount_val']


class UserCouponViewSet(viewsets.ModelViewSet):
    queryset = (
        UserCoupon.objects
        .select_related('user', 'reward')
        .order_by('-id')
    )
    serializer_class = UserCouponSerializer
    filterset_fields = ['user', 'reward', 'status']


class AutomationLogViewSet(viewsets.ModelViewSet):
    queryset = (
        AutomationLog.objects
        .select_related('business')
        .order_by('-logged_at')
    )
    serializer_class = AutomationLogSerializer
    filterset_fields = ['business', 'action_type', 'status']
    ordering_fields = ['logged_at']
