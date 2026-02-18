"""
BookmarkViewSet — CRUD + toggle/check/ids for user bookmarks.
"""
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Bookmark, Business
from ..permissions import IsEmailVerified
from ..serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    """
    CRUD for user bookmarks (saved businesses).

    - **List** (auth):      GET /api/bookmarks/
    - **Create** (auth):    POST /api/bookmarks/               {business, note?}
    - **Toggle** (auth):    POST /api/bookmarks/toggle/        {business}
    - **Check** (auth):     GET /api/bookmarks/check/?business=<id>
    - **IDs** (auth):       GET /api/bookmarks/ids/

    All actions require authentication + verified email.
    Users can only see/modify their own bookmarks.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('business')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """Toggle bookmark on/off for a business."""
        business_id = request.data.get('business')
        if not business_id:
            return Response(
                {'detail': 'business field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            business = Business.objects.get(pk=business_id)
        except Business.DoesNotExist:
            return Response(
                {'detail': 'Business not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user, business=business,
        )
        if not created:
            bookmark.delete()
            return Response({'status': 'removed', 'business': business_id})
        return Response(
            {'status': 'added', 'bookmark': BookmarkSerializer(bookmark).data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='check')
    def check(self, request):
        """Check if the current user has bookmarked a business."""
        business_id = request.query_params.get('business')
        if not business_id:
            return Response(
                {'detail': 'business query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        exists = Bookmark.objects.filter(
            user=request.user, business_id=business_id,
        ).exists()
        return Response({'bookmarked': exists, 'business': int(business_id)})

    @action(detail=False, methods=['get'], url_path='ids')
    def ids(self, request):
        """Return just the business IDs the user has bookmarked — lightweight for UI."""
        biz_ids = list(
            Bookmark.objects.filter(user=request.user)
            .values_list('business_id', flat=True)
        )
        return Response({'business_ids': biz_ids})
