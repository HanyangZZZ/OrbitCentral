"""
BusinessViewSet — CRUD + weighted vector search + stats.
"""
import logging
import os

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Avg, Count, F, FloatField, Value
from pgvector.django import CosineDistance
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Business, SearchedArea, Tag
from ..serializers import BusinessSearchSerializer, BusinessSerializer, TagSerializer
from ..tasks import ensure_area_covered_task

logger = logging.getLogger('api')

# ── Scoring weights ────────────────────────────────────────────────────────────
WEIGHT_VIBE = 0.70
WEIGHT_PROXIMITY = 0.15
WEIGHT_RATING = 0.15

# Proximity decay: score = 1 / (1 + distance_km / PROXIMITY_SCALE)
PROXIMITY_SCALE_KM = 5.0


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = (
        Business.objects
        .select_related('category')
        .order_by('-avg_rating', 'name')
    )
    serializer_class = BusinessSerializer
    filterset_fields = ['category', 'onboarding_status']
    search_fields = ['name', 'contact_email', 'google_place_id']
    ordering_fields = ['avg_rating', 'review_count', 'name', 'created_at']

    # ── Weighted search: GET /api/businesses/search/ ──────────────────────
    @action(detail=False, methods=['get'], url_path='search')
    def vector_search(self, request):
        """
        Semantic search with weighted scoring.

        Query params
        ────────────
        q        — natural-language search query (required)
        lat, lng — user's current location (optional; enables proximity scoring)
        category — category id to filter by (optional)
        sort     — override sort: "distance" | "rating" (optional; default = weighted)
        limit    — max results, 1–50 (default 10)
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'detail': 'Query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = min(int(request.query_params.get('limit', 10)), 50)
        sort_mode = request.query_params.get('sort', '').lower()
        category_id = request.query_params.get('category')
        tag_ids = request.query_params.getlist('tag')
        if len(tag_ids) == 1 and ',' in tag_ids[0]:
            tag_ids = tag_ids[0].split(',')

        # Parse user location
        user_point = None
        lat_str = request.query_params.get('lat')
        lng_str = request.query_params.get('lng')
        if lat_str and lng_str:
            try:
                user_point = Point(float(lng_str), float(lat_str), srid=4326)
            except (ValueError, TypeError):
                pass

        # ── Step 0: auto-import businesses if area not yet covered ───────
        if user_point:
            ensure_area_covered_task.delay(float(lat_str), float(lng_str))

        # ── Step 1: generate query embedding ─────────────────────────────
        try:
            query_embedding = self._get_embedding(query)
        except Exception as e:
            logger.error("Embedding generation failed: %s", e)
            return Response(
                {'detail': 'Embedding service unavailable.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ── Step 2: base queryset – annotate similarity ──────────────────
        qs = (
            Business.objects
            .select_related('category')
            .prefetch_related('tags')
            .filter(embedding__isnull=False)
            .annotate(similarity=1 - CosineDistance(F('embedding'), query_embedding))
        )

        if category_id:
            qs = qs.filter(category_id=category_id)

        if tag_ids:
            for tid in tag_ids:
                try:
                    qs = qs.filter(tags__id=int(tid))
                except (ValueError, TypeError):
                    pass

        # ── Step 3: annotate distance if user location is provided ───────
        if user_point:
            qs = qs.annotate(distance_m=Distance('location', user_point))
        else:
            qs = qs.annotate(distance_m=Value(None, output_field=FloatField()))

        # ── Step 4: sort / score ─────────────────────────────────────────
        if sort_mode == 'distance':
            if not user_point:
                return Response(
                    {'detail': 'lat and lng are required when sort=distance.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.order_by('distance_m')[:limit]
            results = self._annotate_results(qs, user_point, score_mode=None)

        elif sort_mode == 'rating':
            qs = qs.order_by('-avg_rating', '-review_count')[:limit]
            results = self._annotate_results(qs, user_point, score_mode=None)

        else:
            qs = qs.order_by('-similarity')[:limit * 3]
            results = self._annotate_results(qs, user_point, score_mode='weighted')
            results.sort(key=lambda r: r.score or 0, reverse=True)
            results = results[:limit]

        serializer = BusinessSearchSerializer(results, many=True)
        return Response(serializer.data)

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _get_embedding(text: str) -> list[float]:
        """Call OpenAI embeddings API. Raises on failure."""
        import openai

        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.embeddings.create(
            model='text-embedding-3-small',
            input=text,
        )
        return response.data[0].embedding

    @staticmethod
    def _annotate_results(qs, user_point, score_mode):
        """
        Convert QuerySet rows into dicts with distance_km and optional score.
        """
        results = []
        for biz in qs:
            similarity = float(biz.similarity) if biz.similarity else 0.0

            if biz.distance_m is not None:
                distance_km = biz.distance_m.m / 1000.0
            else:
                distance_km = None

            if score_mode == 'weighted':
                vibe_score = max(similarity, 0.0)

                if distance_km is not None:
                    proximity_score = 1.0 / (1.0 + distance_km / PROXIMITY_SCALE_KM)
                else:
                    proximity_score = 0.0

                rating_score = float(biz.avg_rating) / 5.0 if biz.avg_rating else 0.0

                score = (
                    WEIGHT_VIBE * vibe_score
                    + WEIGHT_PROXIMITY * proximity_score
                    + WEIGHT_RATING * rating_score
                )
            else:
                score = None

            biz.distance_km = distance_km
            biz.score = score
            results.append(biz)

        return results

    # ── Stats: GET /api/businesses/stats/ ─────────────────────────────────
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Return database stats for the frontend dashboard."""
        total = Business.objects.count()
        with_embeddings = Business.objects.filter(embedding__isnull=False).count()
        with_tags = Business.objects.filter(tags__isnull=False).distinct().count()
        tag_count = Tag.objects.count()
        searched_areas = SearchedArea.objects.count()
        avg_rating = Business.objects.aggregate(avg=Avg('avg_rating'))['avg']

        top_tags = list(
            Tag.objects.annotate(c=Count('businesses'))
            .order_by('-c')
            .values('id', 'name', 'c')[:15]
        )

        return Response({
            'total_businesses': total,
            'with_embeddings': with_embeddings,
            'with_tags': with_tags,
            'tag_count': tag_count,
            'searched_areas': searched_areas,
            'avg_rating': round(float(avg_rating or 0), 2),
            'top_tags': top_tags,
        })
