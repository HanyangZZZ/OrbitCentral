"""
ReviewViewSet — CRUD for user-submitted reviews + vote action.
"""
import base64
import logging
import uuid

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Review, ReviewVote
from ..pagination import ReviewCursorPagination
from ..permissions import IsEmailVerified, IsOwnerOrReadOnly
from ..serializers import ReviewSerializer

logger = logging.getLogger('api')


class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD for user-submitted reviews.

    - **List** (public):   GET /api/reviews/?business=<id>
    - **Create** (auth):   POST /api/reviews/  {business, rating, description, photo?}
    - **Retrieve** (public): GET /api/reviews/<id>/
    - **Update** (owner):  PATCH /api/reviews/<id>/
    - **Delete** (owner):  DELETE /api/reviews/<id>/

    The optional `photo` field accepts a base64-encoded image (with or without
    data-URI prefix). The image is uploaded to GCS and the public URL is stored
    in `image_url`.
    """
    serializer_class = ReviewSerializer
    pagination_class = ReviewCursorPagination
    filterset_fields = ['business', 'user', 'rating']
    ordering_fields = ['rating', 'created_at']

    def get_permissions(self):
        """Read operations are public; votes require auth+verified; writes require ownership."""
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        if self.action == 'vote':
            return [permissions.IsAuthenticated(), IsEmailVerified()]
        return [permissions.IsAuthenticated(), IsEmailVerified(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        return Review.objects.select_related('user', 'business').prefetch_related('votes').all()

    def perform_create(self, serializer):
        photo_b64 = serializer.validated_data.pop('photo', None)
        image_url = self._upload_photo(photo_b64, serializer.validated_data.get('business'))
        serializer.save(user=self.request.user, image_url=image_url)

    def perform_update(self, serializer):
        photo_b64 = serializer.validated_data.pop('photo', None)
        if photo_b64:
            image_url = self._upload_photo(photo_b64, serializer.instance.business)
            serializer.save(image_url=image_url)
        else:
            serializer.save()

    # ── Vote action ───────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='vote')
    def vote(self, request, pk=None):
        """
        Toggle a helpfulness vote on a review.

        POST /api/reviews/<id>/vote/  {"vote_type": "useful"}

        vote_type must be one of: useful, funny, cool.
        If the vote already exists, it is removed (toggle off).
        """
        review = self.get_object()

        if review.user == request.user:
            return Response(
                {'detail': 'You cannot vote on your own review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vote_type = request.data.get('vote_type', '').strip().lower()
        valid_types = {vt[0] for vt in ReviewVote.VOTE_TYPES}
        if vote_type not in valid_types:
            return Response(
                {'detail': f'vote_type must be one of: {", ".join(sorted(valid_types))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = ReviewVote.objects.filter(
            user=request.user, review=review, vote_type=vote_type,
        ).first()

        if existing:
            existing.delete()
            return Response({'status': 'removed', 'vote_type': vote_type})

        ReviewVote.objects.create(
            user=request.user, review=review, vote_type=vote_type,
        )
        return Response(
            {'status': 'added', 'vote_type': vote_type},
            status=status.HTTP_201_CREATED,
        )

    # ── Photo upload helper ─────────────────────────────────────────────
    @staticmethod
    def _upload_photo(photo_b64: str | None, business) -> str | None:
        """Decode base64 photo and upload to GCS. Returns public URL or None."""
        if not photo_b64:
            return None

        try:
            from django.conf import settings as django_settings
            from ..services import _get_gcs_client

            # Strip optional data-URI prefix
            if ',' in photo_b64:
                photo_b64 = photo_b64.split(',', 1)[1]
            image_bytes = base64.b64decode(photo_b64)

            # Reject uploads > 5 MB
            if len(image_bytes) > 5 * 1024 * 1024:
                logger.warning('Review photo rejected: %d bytes exceeds 5 MB limit', len(image_bytes))
                return None

            # Determine extension from first bytes
            if image_bytes[:3] == b'\xff\xd8\xff':
                ext = 'jpg'
                content_type = 'image/jpeg'
            elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                ext = 'png'
                content_type = 'image/png'
            elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
                ext = 'webp'
                content_type = 'image/webp'
            else:
                ext = 'jpg'
                content_type = 'image/jpeg'

            filename = f'{uuid.uuid4().hex}.{ext}'
            biz_id = business.id if hasattr(business, 'id') else business
            gcs_path = f'reviews/{biz_id}/{filename}'

            bucket_name = getattr(django_settings, 'GCS_BUCKET_NAME', 'orbit-media-prod')
            client = _get_gcs_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(image_bytes, content_type=content_type)
            blob.cache_control = 'public, max-age=31536000'
            blob.patch()

            public_url = getattr(django_settings, 'GCS_PUBLIC_URL', f'https://storage.googleapis.com/{bucket_name}')
            return f'{public_url}/{gcs_path}'

        except Exception as exc:
            logger.warning('Review photo upload failed: %s', exc)
            return None
