"""
BusinessViewSet — CRUD + weighted vector search + stats + photo proxy + AI personalization.
"""
import logging
import os

import requests as http_requests
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Avg, Count, F, FloatField, Value
from django.http import HttpResponse, HttpResponseRedirect
from pgvector.django import CosineDistance
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models import Business, SearchedArea, Tag
from ..permissions import IsEmailVerified
from ..serializers import BusinessSearchSerializer, BusinessSerializer, TagSerializer
from ..services.geocoding import reverse_geocode
from ..services.personalization import gather_user_profile, generate_search_query
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
        .prefetch_related('tags')
        .order_by('-avg_rating', 'name')
    )
    serializer_class = BusinessSerializer
    filterset_fields = ['category', 'onboarding_status']
    search_fields = ['name', 'contact_email', 'google_place_id']
    ordering_fields = ['avg_rating', 'review_count', 'name', 'created_at']

    def get_permissions(self):
        """
        Read-only endpoints (list, retrieve, search, stats) are public.
        Write endpoints (create, update, delete) require admin.
        Personalized requires auth + verified email.
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        if self.action == 'personalized':
            return [permissions.IsAuthenticated(), IsEmailVerified()]
        return [IsAuthenticatedOrReadOnly()]

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

        try:
            limit = min(int(request.query_params.get('limit', 10)), 50)
        except (ValueError, TypeError):
            limit = 10
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

    # ── AI Personalized: GET /api/businesses/personalized/ ────────────────
    @action(detail=False, methods=['get'], url_path='personalized')
    def personalized(self, request):
        """
        AI-personalized business recommendations.

        Analyzes the user's recent reviews and bookmarks with GPT-4.1,
        generates a search query capturing their taste, then runs it
        through the standard weighted-vibe search pipeline.

        Query params
        ────────────
        lat, lng — user location (optional but recommended for proximity scoring)
        limit    — max results, 1–20 (default 5)
        """
        try:
            limit = min(int(request.query_params.get('limit', 5)), 20)
        except (ValueError, TypeError):
            limit = 5

        # Parse user location
        user_point = None
        lat_str = request.query_params.get('lat')
        lng_str = request.query_params.get('lng')
        if lat_str and lng_str:
            try:
                user_point = Point(float(lng_str), float(lat_str), srid=4326)
            except (ValueError, TypeError):
                pass

        # ── Step 1: gather user profile from reviews + bookmarks ─────────
        profile_items = gather_user_profile(request.user)

        if not profile_items:
            return Response(
                {'detail': 'Not enough activity yet. Review or bookmark a few businesses first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Step 2: ask GPT-4.1 to generate a search query ──────────────
        try:
            ai_query = generate_search_query(profile_items)
        except Exception as exc:
            logger.error('AI personalization query generation failed: %s', exc)
            return Response(
                {'detail': 'AI service temporarily unavailable.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ── Step 3: generate embedding from the AI query ─────────────────
        try:
            query_embedding = self._get_embedding(ai_query)
        except Exception as exc:
            logger.error('Embedding generation failed for personalized search: %s', exc)
            return Response(
                {'detail': 'Embedding service unavailable.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ── Step 4: run the same weighted search pipeline ────────────────
        # Auto-import if location provided
        if user_point:
            ensure_area_covered_task.delay(float(lat_str), float(lng_str))

        qs = (
            Business.objects
            .select_related('category')
            .prefetch_related('tags')
            .filter(embedding__isnull=False)
            .annotate(similarity=1 - CosineDistance(F('embedding'), query_embedding))
        )

        # Exclude businesses the user already reviewed or bookmarked
        from ..models import Bookmark, Review
        reviewed_ids = set(
            Review.objects.filter(user=request.user).values_list('business_id', flat=True)
        )
        bookmarked_ids = set(
            Bookmark.objects.filter(user=request.user).values_list('business_id', flat=True)
        )
        exclude_ids = reviewed_ids | bookmarked_ids
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)

        if user_point:
            qs = qs.annotate(distance_m=Distance('location', user_point))
        else:
            qs = qs.annotate(distance_m=Value(None, output_field=FloatField()))

        # Weighted scoring (same as regular search)
        qs = qs.order_by('-similarity')[:limit * 3]
        results = self._annotate_results(qs, user_point, score_mode='weighted')
        results.sort(key=lambda r: r.score or 0, reverse=True)
        results = results[:limit]

        serializer = BusinessSearchSerializer(results, many=True)
        return Response({
            'query': ai_query,
            'profile_size': len(profile_items),
            'results': serializer.data,
        })

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

    # ── Geocode: GET /api/businesses/geocode/ ────────────────────────────
    @action(detail=False, methods=['get'], url_path='geocode')
    def geocode(self, request):
        """
        Reverse-geocode coordinates to city + province.
        Query params: ?lat=43.651&lng=-79.347
        """
        try:
            lat = float(request.query_params['lat'])
            lng = float(request.query_params['lng'])
        except (KeyError, ValueError, TypeError):
            return Response(
                {'detail': 'lat and lng query parameters are required (floats).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = reverse_geocode(lat, lng)
            return Response(result)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except RuntimeError as exc:
            logger.error('Geocode error: %s', exc)
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    # ── Photo proxy: GET /api/businesses/<id>/photo/ ─────────────────────
    @action(detail=True, methods=['get'], url_path='photo')
    def photo(self, request, pk=None):
        """
        Proxy a Google Places photo for this business.
        Query params:
          ?idx=0          — photo index (default: 0 = first)
          ?maxHeight=400  — max height in px (default 400)
        Returns 302 redirect to the resolved Google photo URL, or 404.
        """
        business = self.get_object()
        refs = business.photo_references or []

        idx = int(request.query_params.get('idx', 0))
        if idx < 0 or idx >= len(refs):
            return Response({'detail': 'No photo at this index.'}, status=status.HTTP_404_NOT_FOUND)

        max_height = int(request.query_params.get('maxHeight', 400))
        api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
        if not api_key:
            return Response({'detail': 'Photo service unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        photo_ref = refs[idx]
        url = f'https://places.googleapis.com/v1/{photo_ref}/media?maxHeightPx={max_height}&skipHttpRedirect=true'
        try:
            resp = http_requests.get(url, headers={'X-Goog-Api-Key': api_key}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                photo_url = data.get('photoUri')
                if photo_url:
                    return HttpResponseRedirect(photo_url)
        except Exception:
            pass

        return Response({'detail': 'Could not resolve photo.'}, status=status.HTTP_502_BAD_GATEWAY)
