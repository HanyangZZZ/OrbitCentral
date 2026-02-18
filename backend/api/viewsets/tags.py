"""
TagViewSet — read-only tag endpoints with text search and vector search.
"""
import logging

from django.db.models import Count
from pgvector.django import CosineDistance
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Tag
from ..serializers import TagSerializer

logger = logging.getLogger('api')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only tag endpoints with text search, vector search, and usage counts."""
    serializer_class = TagSerializer
    search_fields = ['name']

    def get_queryset(self):
        qs = Tag.objects.annotate(usage_count=Count('businesses')).order_by('-usage_count')

        # ?q= partial name search
        q = self.request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)

        # ?min_usage= filter out rarely-used tags
        min_usage = self.request.query_params.get('min_usage')
        if min_usage:
            try:
                qs = qs.filter(usage_count__gte=int(min_usage))
            except (ValueError, TypeError):
                pass

        return qs

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Vector-based semantic tag search: GET /api/tags/search/?q=...
        Embeds the query and finds the closest tags by cosine similarity.
        Falls back to text search if no embeddings exist or OpenAI fails.
        """
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'detail': 'q parameter required.'}, status=status.HTTP_400_BAD_REQUEST)

        limit = min(int(request.query_params.get('limit', 20)), 50)
        min_usage = request.query_params.get('min_usage')

        # Import here to avoid circular dependency
        from .businesses import BusinessViewSet

        try:
            query_embedding = BusinessViewSet._get_embedding(q)
        except Exception as exc:
            logger.warning('Tag vector search embedding failed, falling back to text: %s', exc)
            qs = Tag.objects.annotate(usage_count=Count('businesses')).filter(
                name__icontains=q
            ).order_by('-usage_count')[:limit]
            return Response(TagSerializer(qs, many=True).data)

        qs = (
            Tag.objects
            .annotate(usage_count=Count('businesses'))
            .filter(embedding__isnull=False)
            .annotate(similarity=1 - CosineDistance('embedding', query_embedding))
            .filter(similarity__gt=0.25)
            .order_by('-similarity')
        )

        if min_usage:
            try:
                qs = qs.filter(usage_count__gte=int(min_usage))
            except (ValueError, TypeError):
                pass

        results = qs[:limit]
        data = TagSerializer(results, many=True).data
        for item, obj in zip(data, results):
            item['similarity'] = round(float(obj.similarity), 4)
        return Response(data)
