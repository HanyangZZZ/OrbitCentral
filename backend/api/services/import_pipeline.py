"""
Import pipeline — the orchestrator that ties all service modules together.

Public API:
    ensure_area_covered(lat, lng) → int   (number of new businesses created)
"""
import logging
import os
import time
import threading

import openai
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from ..models import Business, SearchedArea
from .google_places import SEARCH_RADIUS_KM, _fetch_google_places
from .classification import _ai_classify_and_tag
from .tags import _resolve_tags
from .businesses import _create_businesses
from .images import _download_and_store_images
from .embeddings import _generate_embeddings

logger = logging.getLogger('api')

# ── Per-area locking ───────────────────────────────────────────────────────────
_import_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_area_lock(lat: float, lng: float) -> threading.Lock:
    """Get or create a lock for a specific area (rounded to 2 decimals)."""
    key = f"{lat:.2f},{lng:.2f}"
    with _locks_lock:
        if key not in _import_locks:
            _import_locks[key] = threading.Lock()
        return _import_locks[key]


def _is_area_covered_fast(lat: float, lng: float) -> bool:
    """Fast PostGIS check: is user within any SearchedArea's radius?"""
    user_point = Point(lng, lat, srid=4326)
    return (
        SearchedArea.objects
        .annotate(d=Distance('center', user_point))
        .extra(where=['ST_Distance(center::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) <= radius_km * 1000'],
               params=[lng, lat])
        .exists()
    )


def _record_searched_area(lat: float, lng: float, count: int):
    return SearchedArea.objects.create(
        center=Point(lng, lat, srid=4326),
        radius_km=SEARCH_RADIUS_KM,
        business_count=count,
    )


def ensure_area_covered(lat: float, lng: float):
    """
    If the area around (lat, lng) hasn't been searched yet, import businesses
    from Google Places, classify with AI, generate tags, and create embeddings.
    Returns the number of new businesses created (0 if area was already covered).
    Area is only marked as searched after full success.
    """
    if _is_area_covered_fast(lat, lng):
        logger.info("Area (%.4f, %.4f) already covered — skipping import", lat, lng)
        return 0

    # Acquire per-area lock to prevent concurrent imports for the same location
    area_lock = _get_area_lock(lat, lng)
    if not area_lock.acquire(blocking=False):
        logger.info("Area (%.4f, %.4f) import already in progress — skipping", lat, lng)
        return 0

    try:
        # Re-check after acquiring lock (another thread may have finished)
        if _is_area_covered_fast(lat, lng):
            logger.info("Area (%.4f, %.4f) already covered — skipping import", lat, lng)
            return 0

        google_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if not google_key:
            logger.warning("GOOGLE_PLACES_API_KEY not set — cannot auto-import")
            return 0
        if not openai_key:
            logger.warning("OPENAI_API_KEY not set — cannot classify/tag")
            return 0

        t0 = time.time()
        logger.info("Auto-importing businesses around (%.4f, %.4f)...", lat, lng)

        # Step 1: Fetch places from Google (8 concurrent workers)
        t1 = time.time()
        raw_places = _fetch_google_places(lat, lng, google_key)
        logger.info("  Step 1 (Google fetch): %.1fs", time.time() - t1)
        if not raw_places:
            return 0

        # Step 2: Filter out places already in DB, cap at MAX_BUSINESSES_PER_IMPORT
        existing_pids = set(
            Business.objects.filter(
                google_place_id__in=[p.get('id', '') for p in raw_places]
            ).values_list('google_place_id', flat=True)
        )
        new_places = [p for p in raw_places if p.get('id', '') and p['id'] not in existing_pids]
        max_import = getattr(settings, 'MAX_BUSINESSES_PER_IMPORT', 100)
        if len(new_places) > max_import:
            logger.info("Capping import from %d to %d businesses", len(new_places), max_import)
            new_places = new_places[:max_import]
        logger.info("Google returned %d places, %d are new (capped at %d)",
                    len(raw_places), len(new_places), max_import)

        if not new_places:
            return 0

        # Step 3: AI classification + tag generation (20 concurrent workers)
        t3 = time.time()
        client = openai.OpenAI(api_key=openai_key)
        classified, category_slug_map = _ai_classify_and_tag(client, new_places)
        logger.info("  Step 3 (AI classify): %.1fs", time.time() - t3)

        # Step 4: Keep only small businesses
        small_businesses = [c for c in classified if c['is_small']]
        logger.info("AI classified %d/%d as small independent businesses",
                    len(small_businesses), len(classified))

        if not small_businesses:
            return 0

        # Step 5: Resolve tags (embed + dedup)
        t5 = time.time()
        all_tag_names = set()
        for biz in small_businesses:
            all_tag_names.update(biz.get('tags', []))
        tag_map = _resolve_tags(client, list(all_tag_names))
        logger.info("  Step 5 (tag resolve): %.1fs", time.time() - t5)

        # Step 6: Bulk create Business records + assign tags + categories
        t6 = time.time()
        created_ids = _create_businesses(small_businesses, tag_map,
                                         category_slug_map, google_key)
        logger.info("  Step 6 (bulk create): %.1fs", time.time() - t6)

        # Step 6.5: Download images from Google & upload to GCS bucket
        t65 = time.time()
        _download_and_store_images(created_ids, google_key)
        logger.info("  Step 6.5 (images → GCS): %.1fs", time.time() - t65)

        # Step 7: Generate embeddings (4 concurrent workers)
        t7 = time.time()
        _generate_embeddings(client, created_ids)
        logger.info("  Step 7 (embeddings): %.1fs", time.time() - t7)

        # Step 8: Mark area as searched ONLY after full success
        _record_searched_area(lat, lng, len(created_ids))

        total = time.time() - t0
        logger.info("Auto-import complete: %d new businesses in %.1fs", len(created_ids), total)
        return len(created_ids)

    except Exception as e:
        logger.error("Auto-import error: %s", e)
        return 0
    finally:
        area_lock.release()
