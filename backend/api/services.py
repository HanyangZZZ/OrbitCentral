"""
Auto-import service: when a user searches from a new location, fetch nearby
small businesses from Google Places, classify them with AI, generate semantic
tags, consolidate tags via OpenAI, and generate embeddings.

Design goals:
  • Cheapest OpenAI model (gpt-4o-mini for classification, text-embedding-3-small)
  • Concurrent workers for Google API, AI classification, and embeddings
  • google_place_id as unique identifier — never duplicate
  • Tag consolidation via GPT — "patio" → "outdoor-seating", "wifi-available" → "wifi"
  • Tags baked into business embedding for vibe search
"""
import json
import logging
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai
import requests
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db import close_old_connections

from .models import Business, Category, SearchedArea, Tag

logger = logging.getLogger('api')

# ── Config ─────────────────────────────────────────────────────────────────────
SEARCH_RADIUS_KM = 5.0
PLACES_ENDPOINT = 'https://places.googleapis.com/v1/places:searchNearby'

FIELD_MASK = ','.join([
    'places.id', 'places.displayName', 'places.formattedAddress',
    'places.location', 'places.rating', 'places.userRatingCount',
    'places.types', 'places.primaryType', 'places.editorialSummary',
    'places.websiteUri', 'places.internationalPhoneNumber',
    'places.photos', 'places.businessStatus', 'places.priceLevel',
])

PRICE_LEVEL_MAP = {
    'PRICE_LEVEL_FREE': 0, 'PRICE_LEVEL_INEXPENSIVE': 1,
    'PRICE_LEVEL_MODERATE': 2, 'PRICE_LEVEL_EXPENSIVE': 3,
    'PRICE_LEVEL_VERY_EXPENSIVE': 4,
}

# Types that typically represent small businesses
SMALL_BIZ_TYPES = [
    # Food & drink
    'cafe', 'bakery', 'bar', 'restaurant', 'book_store', 'florist',
    'ice_cream_shop', 'coffee_shop', 'brunch_restaurant',
    'ramen_restaurant', 'sushi_restaurant', 'pizza_restaurant',
    'sandwich_shop', 'seafood_restaurant', 'thai_restaurant',
    'indian_restaurant', 'mexican_restaurant', 'italian_restaurant',
    'korean_restaurant', 'vietnamese_restaurant', 'liquor_store',
    # Personal care & wellness
    'hair_care', 'beauty_salon', 'spa', 'barber_shop', 'nail_salon',
    # Retail & crafts
    'art_gallery', 'clothing_store', 'pet_store', 'jewelry_store',
    'bicycle_store', 'gift_shop', 'furniture_store', 'home_goods_store',
    'shoe_store', 'sporting_goods_store',
    # Services & repair
    'car_repair', 'electrician', 'locksmith', 'plumber',
    'shoe_repair', 'tailor', 'laundry', 'dry_cleaning',
    'electronics_store', 'cell_phone_store',
    # Other local businesses
    'gym', 'yoga_studio', 'dance_studio', 'music_school',
    'photographer', 'printing_service', 'travel_agency',
    'veterinary_care', 'pet_grooming',
]


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════

# In-memory lock to prevent concurrent imports for the same area
import threading as _threading
_import_locks: dict[str, _threading.Lock] = {}
_locks_lock = _threading.Lock()


def _get_area_lock(lat: float, lng: float) -> _threading.Lock:
    """Get or create a lock for a specific area (rounded to 2 decimals)."""
    key = f"{lat:.2f},{lng:.2f}"
    with _locks_lock:
        if key not in _import_locks:
            _import_locks[key] = _threading.Lock()
        return _import_locks[key]


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

        # Step 2: Filter out places already in DB
        existing_pids = set(
            Business.objects.filter(
                google_place_id__in=[p.get('id', '') for p in raw_places]
            ).values_list('google_place_id', flat=True)
        )
        new_places = [p for p in raw_places if p.get('id', '') and p['id'] not in existing_pids]
        logger.info("Google returned %d places, %d are new", len(raw_places), len(new_places))

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
        # Do NOT mark area as searched — allow retry on next request
        return 0
    finally:
        area_lock.release()


# ═══════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _is_area_covered_fast(lat: float, lng: float) -> bool:
    """Fast PostGIS check: is user within any SearchedArea's radius?"""
    user_point = Point(lng, lat, srid=4326)
    # Single query: annotate each area with distance, check if within its radius
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


def _generate_grid(lat: float, lng: float, radius_km: float, step_km: float = 2.0):
    """Grid of (lat, lng) within radius_km, spaced step_km apart."""
    points = []
    km_per_deg_lat = 111.32
    km_per_deg_lng = 111.32 * math.cos(math.radians(lat))
    steps = int(radius_km / step_km)
    for dy in range(-steps, steps + 1):
        for dx in range(-steps, steps + 1):
            p_lat = lat + (dy * step_km) / km_per_deg_lat
            p_lng = lng + (dx * step_km) / km_per_deg_lng
            if math.sqrt((dy * step_km) ** 2 + (dx * step_km) ** 2) <= radius_km:
                points.append((p_lat, p_lng))
    return points


def _fetch_google_places(lat: float, lng: float, api_key: str) -> list[dict]:
    """Fetch places from Google Places API across a grid of points and types.
    Uses concurrent workers for parallel fetching."""
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': FIELD_MASK,
    }

    grid = _generate_grid(lat, lng, SEARCH_RADIUS_KM, step_km=2.5)
    seen_ids: set[str] = set()
    all_places: list[dict] = []
    lock = __import__('threading').Lock()

    # Broad set of types to cover food, retail, services, and repair
    search_types = [
        'cafe', 'restaurant', 'bar', 'bakery',
        'beauty_salon', 'book_store', 'florist',
        'hair_care', 'spa', 'clothing_store',
        'car_repair', 'electrician', 'locksmith',
        'gym', 'art_gallery', 'pet_store',
        'jewelry_store', 'furniture_store', 'laundry',
        'veterinary_care',
    ]

    # Build all (type, grid_point) tasks
    tasks = [(biz_type, g_lat, g_lng) for biz_type in search_types for (g_lat, g_lng) in grid]

    def _fetch_one(biz_type, g_lat, g_lng):
        body = {
            'maxResultCount': 20,
            'includedTypes': [biz_type],
            'locationRestriction': {
                'circle': {
                    'center': {'latitude': g_lat, 'longitude': g_lng},
                    'radius': 2500.0,
                },
            },
        }
        try:
            resp = requests.post(PLACES_ENDPOINT, json=body, headers=headers, timeout=15)
        except Exception as e:
            logger.warning("Google Places request error: %s", e)
            return []
        if resp.status_code == 429:
            time.sleep(2)
            return []
        if resp.status_code != 200:
            return []
        return resp.json().get('places', [])

    # 8 concurrent workers for Google API calls
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_fetch_one, t, la, ln): (t, la, ln)
                   for (t, la, ln) in tasks}
        for future in as_completed(futures):
            try:
                places = future.result()
                for place in places:
                    pid = place.get('id', '')
                    with lock:
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            all_places.append(place)
            except Exception as e:
                logger.warning("Google fetch worker error: %s", e)

    logger.info("Fetched %d unique places from Google (%d API calls, 8 workers)",
                len(all_places), len(tasks))
    return all_places


def _load_category_list() -> tuple[str, dict[str, int]]:
    """
    Build a formatted category list from the DB and a slug→id map.
    Returns (prompt_text, slug_map).
    """
    parents = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    lines = []
    all_valid_names = []
    slug_map: dict[str, int] = {}  # slug → category id
    for p in parents:
        children = list(p.children.all())
        child_names = [c.name for c in children]
        lines.append(f"- {p.name}: {', '.join(child_names)}")
        all_valid_names.append(p.name)
        all_valid_names.extend(child_names)
        slug_map[p.slug] = p.id
        for c in children:
            slug_map[c.slug] = c.id
    lines.append(f"\nVALID NAMES (use exactly one of these): {', '.join(all_valid_names)}")
    return '\n'.join(lines), slug_map


def _load_popular_tags(min_usage: int = 3, limit: int = 120) -> str:
    """Load existing popular tags from DB to encourage AI reuse."""
    from django.db.models import Count
    popular = (
        Tag.objects
        .annotate(usage=Count('businesses'))
        .filter(usage__gte=min_usage)
        .order_by('-usage')
        .values_list('name', flat=True)[:limit]
    )
    return ', '.join(f'"{t}"' for t in popular)


def _ai_classify_and_tag(client: openai.OpenAI, places: list[dict]) -> list[dict]:
    """
    Use gpt-4o-mini to classify businesses as small/independent, assign a
    category, and generate descriptive tags.
    Processes batches of 10 concurrently with 20 workers.
    """
    # Load categories dynamically from DB
    category_prompt, category_slug_map = _load_category_list()

    # Load existing popular tags so the AI reuses them
    existing_tags_str = _load_popular_tags()

    results = []
    batch_size = 10
    batches = [places[i:i + batch_size] for i in range(0, len(places), batch_size)]

    def _classify_batch(batch):
        batch_info = []
        for p in batch:
            batch_info.append({
                'id': p.get('id', ''),
                'name': p.get('displayName', {}).get('text', ''),
                'types': p.get('types', []),
                'primary_type': p.get('primaryType', ''),
                'address': p.get('formattedAddress', ''),
                'description': p.get('editorialSummary', {}).get('text', ''),
                'rating': p.get('rating', 0),
                'rating_count': p.get('userRatingCount', 0),
            })

        system_prompt = """You are a local business analyst. You classify businesses and generate descriptive tags.
Respond ONLY with a JSON object: {"results": [...]}. No extra text."""

        # Build the existing tags instruction
        existing_tags_block = ""
        if existing_tags_str:
            existing_tags_block = f"""
   REUSE these existing tags whenever they fit (STRONGLY PREFERRED over inventing new ones):
   {existing_tags_str}
   You may create a NEW tag only if none of the above apply. Keep new tags short (1-2 words)."""

        user_prompt = f"""For each business below, provide:

1. **is_small** (boolean): true = small, independent, locally-owned business. false = chain, franchise (McDonald's, Starbucks, Tim Hortons, Subway, Pizza Pizza, Walmart, Costco, etc.), big-box store, supermarket chain, bank, or large corporation.

2. **category** (string): Pick the BEST-FIT subcategory from this list:
{category_prompt}
Return the exact subcategory name (e.g. "Restaurants", "Beauty", "Auto"). If none fit well, return the parent category name.
You MUST use one of the exact names listed above. Do NOT invent new category names.

3. **tags** (array of strings): Generate 3-5 descriptive tags that help users DISCOVER this business.
   Tags should describe WHAT the business offers or its VIBE — not how good it is.
   Use short, reusable lowercase-hyphenated words (1-2 words max).
   GOOD tags (specific, searchable): "cozy", "pet-friendly", "wifi", "outdoor-seating", "vegan", "craft-beer", "late-night", "romantic", "artisan", "family-friendly", "takeout", "delivery", "organic", "brunch", "live-music", "quiet", "upscale", "casual", "trendy", "vintage", "handmade", "locally-sourced", "hidden-gem", "walk-in", "by-appointment", "sushi", "espresso", "yoga", "tattoo", "florist"
   BAD tags (NEVER use these kinds): "high-quality", "expert", "professional", "reliable", "trusted", "best", "great-service", "compassionate", "customer-satisfaction", "premium", "holistic", "athletic", "active", "awaiting-reviews", "basic-service", "children-friendly"
   RULE: A tag must answer "What can I find here?" or "What's the vibe?" — NOT "How good is it?"
   Do NOT generate tags about quality, ratings, expertise, or generic descriptors.{existing_tags_block}
   Every business should get at least 3 tags.

Return JSON: {{"results": [{{"id": "...", "is_small": true/false, "category": "...", "tags": [...]}}]}}

Businesses:
{json.dumps(batch_info, ensure_ascii=False)}"""

        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                response_format={'type': 'json_object'},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if isinstance(parsed, list):
                ai_results = parsed
            elif isinstance(parsed, dict):
                ai_results = parsed.get('results', parsed.get('businesses', parsed.get('data', [])))
            else:
                ai_results = []
        except Exception as e:
            logger.error("AI classification error: %s", e)
            ai_results = [{'id': p.get('id', ''), 'is_small': True, 'category': '', 'tags': []} for p in batch]

        # Merge AI results with place data
        ai_map = {r['id']: r for r in ai_results if isinstance(r, dict) and 'id' in r}
        batch_results = []
        for p in batch:
            pid = p.get('id', '')
            ai = ai_map.get(pid, {'is_small': True, 'category': '', 'tags': []})
            batch_results.append({
                'place': p,
                'is_small': ai.get('is_small', True),
                'category': ai.get('category', ''),
                'tags': ai.get('tags', [])[:5],
            })
        return batch_results

    # 20 concurrent workers for AI classification
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_classify_batch, b): i for i, b in enumerate(batches)}
        indexed_results = {}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                indexed_results[idx] = future.result()
            except Exception as e:
                logger.error("AI classify worker error: %s", e)
                indexed_results[idx] = [
                    {'place': p, 'is_small': True, 'category': '', 'tags': []}
                    for p in batches[idx]
                ]
        # Reassemble in order
        for i in range(len(batches)):
            results.extend(indexed_results.get(i, []))

    return results, category_slug_map


def _normalize_tag(name: str) -> str:
    """Normalize tag to a canonical short form before vector dedup."""
    clean = name.lower().strip()
    # Remove filler suffixes that produce duplicate concepts
    _STRIP_SUFFIXES = [
        '-atmosphere', '-ambiance', '-ambience', '-setting', '-vibes', '-vibe',
        '-experience', '-style', '-inspired', '-oriented', '-based', '-focused',
        '-options', '-menu', '-selection', '-offerings',
    ]
    for suffix in _STRIP_SUFFIXES:
        if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
            clean = clean[:len(clean) - len(suffix)]
            break
    return clean


def _resolve_tags(client: openai.OpenAI, tag_names: list[str]) -> dict[str, Tag]:
    """
    Resolve raw AI-generated tags into a compact canonical set using
    OpenAI-powered consolidation instead of vector cosine similarity.

    Why this beats vector dedup:
      - Cosine similarity only catches near-identical strings
        ("cozy" ≈ "cozy-spot" but misses "patio" ≈ "outdoor-seating")
      - GPT understands semantic equivalence: "wifi-available" → "wifi",
        "brake-repair" → "auto-repair", "patio" → "outdoor-seating"
      - One cheap API call (~$0.008) consolidates ALL tags at once

    Strategy:
      1. Normalize + blocklist filter (fast, no API cost)
      2. Load existing tags from DB
      3. Send candidates + existing tags to GPT-4o-mini for consolidation
      4. Create Tag objects for genuinely new canonical tags
      5. Generate vector embeddings for new tags (kept for user search)

    Returns a dict mapping original tag name → Tag model instance.
    """
    if not tag_names:
        return {}

    # ── Step 0: blocklist + normalize ──────────────────────────────────────
    BLOCKLIST = frozenset({
        'local', 'unique', 'quality', 'professional', 'reliable',
        'popular', 'convenient', 'friendly', 'community', 'affordable',
        'modern', 'traditional', 'diverse', 'authentic', 'creative',
        'welcoming', 'specialty', 'essential', 'trusted', 'established',
        'neighborhood', 'neighbourhood', 'accessible', 'custom', 'curated',
        'premium', 'fresh', 'homemade', 'healthy', 'natural', 'expert',
        'personalized', 'innovative', 'comfortable', 'spacious',
        'clean', 'fast', 'small-batch', 'independent', 'new',
        'service', 'quick', 'refined', 'hearty', 'flexible',
        'gift', 'gifts', 'gear', 'indoor', 'relaxed', 'fast-service',
        'multi-service', 'customer-favorite', 'local-favorite',
        'concierge', 'organization', 'restoration',
        'adorable', 'whimsical', 'simple', 'flavored', 'experienced',
        'quick-service', 'cultural', 'detailed', 'luxurious', 'elegant',
        'classic', 'stylish', 'chic', 'lovely', 'pleasant', 'warm',
        'bright', 'cozy-spot', 'nice', 'good', 'great', 'best',
        'delicious', 'tasty', 'yummy', 'savory', 'flavorful',
        'efficient', 'dependable', 'unique-finds', 'local-business',
        'skilled', 'dedicated', 'reputable', 'responsive', 'thorough',
        # generic service/quality descriptors
        'basic-service', 'expert-service', 'customer-satisfaction',
        'compassionate', 'active', 'durable', 'replacement',
        'satisfaction', 'comprehensive', 'attentive', 'exceptional',
        'specialized', 'certified', 'licensed', 'insured',
        'consultation', 'assessment', 'estimate', 'diagnosis',
        'maintenance', 'installation', 'inspection',
        # more generic descriptors
        'high-rated', 'customer-service', 'premium-quality', 'caring',
        'expert-repair', 'premier', 'fine', 'programs', 'rental',
        'high-rating', 'awaiting-reviews', 'active-lifestyle',
        'basic-services', 'expert-advice', 'high-quality',
        'holistic', 'athletic', 'food-delivery',
    })

    def _is_blocked(norm: str) -> bool:
        """Check if a normalized tag should be blocked (handles plurals)."""
        if norm in BLOCKLIST:
            return True
        # Check singular form (strip trailing 's')
        if norm.endswith('s') and not norm.endswith('ss') and norm[:-1] in BLOCKLIST:
            return True
        # Check compound singular: "basic-services" → "basic-service"
        if '-' in norm:
            parts = norm.rsplit('-', 1)
            singular = parts[0] + '-' + parts[1].rstrip('s') if parts[1].endswith('s') and not parts[1].endswith('ss') else None
            if singular and singular in BLOCKLIST:
                return True
        return False

    filtered_names: list[str] = []
    norm_map: dict[str, str] = {}   # original_name → normalized
    unique_norms: set[str] = set()

    for name in tag_names:
        norm = _normalize_tag(name)
        if not _is_blocked(norm) and len(norm) >= 2 and norm.count('-') <= 1:
            filtered_names.append(name)
            norm_map[name] = norm
            unique_norms.add(norm)

    if not unique_norms:
        return {}

    sorted_norms = sorted(unique_norms)
    blocked_count = len(tag_names) - len(filtered_names)
    logger.info("Tags: %d raw → %d filtered → %d unique (blocked %d)",
                len(tag_names), len(filtered_names), len(sorted_norms), blocked_count)

    # ── Step 1: load existing tags from DB ─────────────────────────────────
    existing_tags = list(Tag.objects.values_list('name', flat=True))

    # ── Step 2: OpenAI consolidation ───────────────────────────────────────
    consolidation = _consolidate_tags_with_ai(client, sorted_norms, existing_tags)
    # consolidation: {candidate_name: canonical_name}

    # Post-consolidation: filter canonical values through blocklist
    # (AI might create canonical names like "premium" that we'd normally block)
    for candidate, canonical in list(consolidation.items()):
        if _is_blocked(canonical) and canonical != candidate:
            consolidation[candidate] = candidate  # revert to original
        elif _is_blocked(canonical) and _is_blocked(candidate):
            del consolidation[candidate]  # drop both

    canonical_names = set(consolidation.values())
    merged_count = len(sorted_norms) - len(canonical_names)
    logger.info("AI consolidation: %d candidates → %d canonical (%d merged)",
                len(sorted_norms), len(canonical_names), merged_count)

    # ── Step 3: get-or-create Tag objects ──────────────────────────────────
    # Fetch all existing tags that are referenced
    existing_objs = {t.name: t for t in Tag.objects.filter(name__in=canonical_names)}
    new_tag_names = [n for n in canonical_names if n not in existing_objs]

    # Create new tags (no embedding yet)
    new_tags_created = []
    for name in new_tag_names:
        tag, created = Tag.objects.get_or_create(name=name)
        existing_objs[name] = tag
        if created:
            new_tags_created.append(tag)

    # ── Step 4: generate embeddings for new tags ──────────────────────────
    needs_embedding = [t for t in new_tags_created if t.embedding is None]
    if needs_embedding:
        embed_names = [t.name for t in needs_embedding]
        try:
            resp = client.embeddings.create(
                model='text-embedding-3-small',
                input=embed_names,
            )
            for i, item in enumerate(resp.data):
                needs_embedding[i].embedding = item.embedding
                needs_embedding[i].save(update_fields=['embedding'])
        except Exception as e:
            logger.error("Tag embedding error: %s", e)

    logger.info("Tags resolved: %d new created, %d total in DB",
                len(new_tags_created), Tag.objects.count())

    # ── Step 5: map original names → Tag objects ──────────────────────────
    result: dict[str, Tag] = {}
    for original_name in filtered_names:
        norm = norm_map[original_name]
        canonical = consolidation.get(norm, norm)
        tag = existing_objs.get(canonical)
        if tag:
            result[original_name] = tag

    return result


def _consolidate_tags_with_ai(
    client: openai.OpenAI,
    candidate_tags: list[str],
    existing_tags: list[str],
) -> dict[str, str]:
    """
    Consolidate candidate tags into a smaller canonical set using GPT-4o-mini.
    Processes in batches of ~100 for better accuracy (large single calls produce
    mostly identity mappings because the output JSON is too large).

    Each batch's canonical tags become part of the reference set for the next batch,
    enabling cross-batch dedup.

    Returns {candidate: canonical_name} for every candidate.
    """
    BATCH_SIZE = 100

    FORBIDDEN_CANONICALS = frozenset({
        'vibe', 'food', 'art', 'services', 'health', 'beauty', 'cuisine',
        'drinks', 'quality', 'business', 'space', 'location', 'shopping',
        'healthcare', 'treatments', 'grooming', 'auto', 'entertainment',
        'dining', 'wellness', 'fitness', 'lifestyle', 'retail', 'culture',
        'recreation', 'hospitality', 'maintenance', 'personal-care',
        'food-and-drink', 'arts-and-crafts', 'health-and-wellness',
        'event', 'restaurant', 'local-service', 'community',
    })

    all_mappings: dict[str, str] = {}
    # Reference set grows as each batch's canonical tags are added
    reference_tags = set(existing_tags)

    # Sort alphabetically so morphological variants end up in the same batch
    sorted_candidates = sorted(candidate_tags)
    total_batches = (len(sorted_candidates) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        batch = sorted_candidates[start:start + BATCH_SIZE]

        batch_mappings = _consolidate_batch(
            client, batch, sorted(reference_tags), batch_idx + 1, total_batches,
        )

        # Post-processing: revert forbidden super-category canonicals
        for candidate, canonical in list(batch_mappings.items()):
            if canonical in FORBIDDEN_CANONICALS:
                if candidate in FORBIDDEN_CANONICALS:
                    del batch_mappings[candidate]  # drop entirely
                else:
                    batch_mappings[candidate] = candidate  # revert to original

        all_mappings.update(batch_mappings)
        # Add new canonical tags to the reference set for subsequent batches
        reference_tags.update(batch_mappings.values())

    merged = sum(1 for c, v in all_mappings.items() if c != v)
    canonical_count = len(set(all_mappings.values()))
    logger.info("AI consolidation: %d candidates → %d canonical (%d merged) in %d batches",
                len(candidate_tags), canonical_count, merged, total_batches)
    return all_mappings


def _consolidate_batch(
    client: openai.OpenAI,
    batch_candidates: list[str],
    reference_tags: list[str],
    batch_num: int,
    total_batches: int,
) -> dict[str, str]:
    """Consolidate a single batch of ~100 candidates against the reference tags."""
    ref_str = ', '.join(reference_tags) if reference_tags else '(none yet)'
    cand_str = ', '.join(batch_candidates)

    system = (
        "You consolidate tags for a local business discovery app. "
        "You AGGRESSIVELY merge synonyms, near-duplicates, and compounds into the "
        "EXISTING reference set. You keep genuinely distinct concepts. "
        "Output ONLY JSON."
    )

    user = f"""Map each CANDIDATE tag to the best REFERENCE tag, or keep as-is ONLY if truly unique.

MERGE AGGRESSIVELY:
1. Morphological variants → pick ONE:  relaxing→relaxation, artisanal→artisan, cozy→cozy (not coziness)
2. Compounds → base:  handmade-glass→handmade, custom-care→custom, canadian-cuisine→canadian
3. Near-synonyms:  comfy→cozy, hip→trendy, laid-back→casual, eatery→restaurant, doggy→pet-friendly
4. Same service:  nail-art→nail-care, hair-salon→hair-care, brake-repair→auto-repair, patio→outdoor-seating
5. If a REFERENCE tag already covers this concept, USE IT. Prefer existing reference tags.

KEEP SEPARATE only when truly different user search intents (cozy≠trendy, japanese≠italian, wifi≠delivery).

NEVER output: vibe, food, art, services, health, beauty, cuisine, drinks, business, space, shopping, auto, lifestyle

REFERENCE TAGS ({len(reference_tags)}):
[{ref_str}]

CANDIDATES (batch {batch_num}/{total_batches}, {len(batch_candidates)} tags):
[{cand_str}]

Return JSON: {{"mappings": {{"candidate": "canonical", ...}}}}
Every candidate MUST appear as key. Prefer mapping to reference tags."""

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            response_format={'type': 'json_object'},
            temperature=0.1,
        )
        parsed = json.loads(response.choices[0].message.content)
        mappings = parsed.get('mappings', {})

        for tag in batch_candidates:
            if tag not in mappings:
                mappings[tag] = tag

        batch_merged = sum(1 for c, v in mappings.items() if c != v)
        logger.info("  Batch %d/%d: %d candidates → %d merged",
                     batch_num, total_batches, len(batch_candidates), batch_merged)
        return mappings

    except Exception as e:
        logger.error("Batch %d consolidation error: %s — identity fallback", batch_num, e)
        return {t: t for t in batch_candidates}


def _create_businesses(classified: list[dict], tag_map: dict[str, Tag],
                       category_slug_map: dict[str, int],
                       google_api_key: str) -> list[int]:
    """Create Business records from classified places, assign tags + categories.
    Return new IDs.  Uses bulk_create for efficiency."""
    # Build a name→id lookup for categories (case-insensitive)
    cat_name_map: dict[str, int] = {}
    for cat in Category.objects.all():
        cat_name_map[cat.name.lower()] = cat.id
        cat_name_map[cat.slug] = cat.id

    # Prepare all Business objects
    to_create: list[Business] = []
    tag_assignments: list[tuple[int, list[str]]] = []  # (index, tag_names)

    existing_pids = set(
        Business.objects.filter(
            google_place_id__in=[item['place'].get('id', '') for item in classified]
        ).values_list('google_place_id', flat=True)
    )

    for item in classified:
        place = item['place']
        tags = item.get('tags', [])
        google_id = place.get('id', '')

        if not google_id or google_id in existing_pids:
            continue

        loc = place.get('location', {})
        p_lat = loc.get('latitude')
        p_lng = loc.get('longitude')
        location = Point(p_lng, p_lat, srid=4326) if p_lat and p_lng else None

        display_name = place.get('displayName', {}).get('text', '')
        editorial = place.get('editorialSummary', {}).get('text', '')
        photos = place.get('photos', [])
        photo_refs = [p.get('name', '') for p in photos if p.get('name')] if photos else None

        price_str = place.get('priceLevel', '')
        price_level = PRICE_LEVEL_MAP.get(price_str)

        image_url = None
        if photo_refs:
            image_url = (
                f'https://places.googleapis.com/v1/{photo_refs[0]}/media'
                f'?maxHeightPx=400&key={google_api_key}'
            )

        # Resolve category from AI response
        ai_cat_name = (item.get('category', '') or '').strip()
        category_id = None
        if ai_cat_name:
            # 1. Exact match (case-insensitive)
            category_id = cat_name_map.get(ai_cat_name.lower())
            if not category_id:
                # 2. Slug match
                from django.utils.text import slugify
                category_id = cat_name_map.get(slugify(ai_cat_name))
            if not category_id:
                # 3. Keyword fallback for common AI variations
                _KEYWORD_FALLBACK = {
                    # Food & Drink variations
                    'cafe': 'restaurants', 'cafes': 'restaurants',
                    'coffee': 'restaurants', 'coffee shop': 'restaurants',
                    'coffee house': 'restaurants', 'tea house': 'restaurants',
                    'bar': 'restaurants', 'bars': 'restaurants',
                    'pub': 'restaurants', 'pubs': 'restaurants',
                    'bakery': 'sweets', 'pastry': 'sweets',
                    'dessert': 'sweets', 'ice cream': 'sweets',
                    'ice cream shop': 'sweets', 'candy': 'sweets',
                    'brunch': 'restaurants', 'brunch restaurant': 'restaurants',
                    'diner': 'restaurants', 'bistro': 'restaurants',
                    'pizzeria': 'restaurants', 'deli': 'restaurants',
                    'food truck': 'restaurants', 'catering': 'restaurants',
                    'juice bar': 'restaurants', 'smoothie': 'restaurants',
                    'wine bar': 'restaurants', 'brewery': 'restaurants',
                    # Retail variations
                    'bookstore': 'gifts & hobbies', 'books': 'gifts & hobbies',
                    'book store': 'gifts & hobbies', 'toy store': 'gifts & hobbies',
                    'gift shop': 'gifts & hobbies', 'hobby': 'gifts & hobbies',
                    'craft store': 'gifts & hobbies', 'art supply': 'gifts & hobbies',
                    'clothing': 'apparel & accessories', 'fashion': 'apparel & accessories',
                    'shoe store': 'apparel & accessories', 'boutique': 'apparel & accessories',
                    'jewelry': 'apparel & accessories', 'jewelry store': 'apparel & accessories',
                    'furniture': 'home', 'furniture store': 'home',
                    'home goods': 'home', 'home decor': 'home',
                    'hardware store': 'home', 'garden center': 'home',
                    'electronics store': 'electronics', 'phone store': 'electronics',
                    'computer store': 'electronics', 'cell phone': 'electronics',
                    'pet store': 'pet care', 'pet shop': 'pet care',
                    'pet supply': 'pet care', 'pet supplies': 'pet care',
                    # Personal Services variations
                    'salon': 'beauty', 'hair salon': 'beauty',
                    'barber': 'beauty', 'barber shop': 'beauty',
                    'nail': 'beauty', 'nail salon': 'beauty',
                    'spa': 'beauty', 'day spa': 'beauty',
                    'skincare': 'beauty', 'esthetician': 'beauty',
                    'skin care': 'beauty', 'skin': 'beauty',
                    'waxing': 'beauty', 'lash': 'beauty',
                    'tattoo': 'beauty', 'piercing': 'beauty',
                    'wellness center': 'health', 'wellness': 'health',
                    'veterinary': 'pet care', 'veterinary care': 'pet care',
                    'vet': 'pet care', 'animal hospital': 'pet care',
                    'pet grooming': 'pet care', 'dog grooming': 'pet care',
                    'gym': 'recreation', 'fitness': 'recreation',
                    'fitness center': 'recreation', 'yoga': 'recreation',
                    'yoga studio': 'recreation', 'martial arts': 'recreation',
                    'dance studio': 'recreation', 'swimming pool': 'recreation',
                    'sports club': 'recreation', 'sports': 'recreation',
                    'sports activity location': 'recreation',
                    'pilates': 'recreation', 'crossfit': 'recreation',
                    'clinic': 'health', 'dentist': 'health',
                    'pharmacy': 'health', 'optometrist': 'health',
                    'chiropractor': 'health', 'physiotherapy': 'health',
                    'massage': 'health', 'acupuncture': 'health',
                    'school': 'education', 'tutoring': 'education',
                    'music school': 'education', 'language school': 'education',
                    'driving school': 'education', 'training center': 'education',
                    # Home Services variations
                    'mechanic': 'auto', 'auto repair': 'auto',
                    'car repair': 'auto', 'car wash': 'auto',
                    'tire shop': 'auto', 'body shop': 'auto',
                    'auto body': 'auto', 'oil change': 'auto',
                    'tailor': 'maintenance', 'tailor shop': 'maintenance',
                    'shoe repair': 'maintenance', 'locksmith': 'maintenance',
                    'electrician': 'maintenance', 'plumber': 'maintenance',
                    'plumbing': 'maintenance', 'electrical': 'maintenance',
                    'handyman': 'maintenance', 'repair': 'maintenance',
                    'appliance repair': 'maintenance',
                    'laundry': 'cleaning', 'dry cleaning': 'cleaning',
                    'dry cleaner': 'cleaning', 'carpet cleaning': 'cleaning',
                    'maid service': 'cleaning', 'janitorial': 'cleaning',
                    # Entertainment variations
                    'gallery': 'arts', 'art gallery': 'arts',
                    'museum': 'arts', 'theater': 'arts',
                    'theatre': 'arts', 'music venue': 'arts',
                    'concert': 'arts', 'photography': 'arts',
                    'photo studio': 'arts', 'photographer': 'arts',
                    'florist': 'retail', 'flower shop': 'retail',
                    'bowling': 'recreation', 'arcade': 'recreation',
                    'sporting goods': 'recreation', 'bicycle store': 'recreation',
                    'bicycle': 'recreation', 'bike shop': 'recreation',
                    'escape room': 'recreation', 'amusement': 'recreation',
                    'nightlife': 'entertainment', 'nightclub': 'entertainment',
                    'karaoke': 'entertainment', 'comedy club': 'entertainment',
                    'chocolate shop': 'sweets', 'chocolate': 'sweets',
                    'service': 'home services',
                }
                fallback = _KEYWORD_FALLBACK.get(ai_cat_name.lower())
                if fallback:
                    category_id = cat_name_map.get(fallback)
            if not category_id:
                # 4. Partial match — if AI response contains a known category name
                ai_lower = ai_cat_name.lower()
                for cat_name_key, cat_id in cat_name_map.items():
                    if len(cat_name_key) > 2 and cat_name_key in ai_lower:
                        category_id = cat_id
                        break
                if not category_id:
                    logger.debug("Unknown category '%s' from AI — skipping", ai_cat_name)

        biz = Business(
            google_place_id=google_id,
            name=display_name,
            description=editorial or None,
            address=place.get('formattedAddress', ''),
            location=location,
            category_id=category_id,
            phone=place.get('internationalPhoneNumber', '') or None,
            website_url=place.get('websiteUri', '') or None,
            google_types=place.get('types', []) or None,
            price_level=price_level,
            photo_references=photo_refs,
            business_status=place.get('businessStatus', '') or None,
            avg_rating=place.get('rating', 0) or 0,
            user_rating_count=place.get('userRatingCount', 0) or 0,
            onboarding_status='discovered',
            image_url=image_url,
        )
        to_create.append(biz)
        tag_assignments.append((len(to_create) - 1, tags))

    if not to_create:
        return []

    # Bulk create all businesses at once (ignore_conflicts for safety)
    created = Business.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=100)

    # Re-fetch IDs for successfully created records
    created_pids = [b.google_place_id for b in to_create]
    id_map = dict(
        Business.objects.filter(google_place_id__in=created_pids)
        .values_list('google_place_id', 'id')
    )

    # Assign tags via bulk M2M through model
    ThroughModel = Business.tags.through
    through_records = []
    for idx, tag_names in tag_assignments:
        biz = to_create[idx]
        biz_id = id_map.get(biz.google_place_id)
        if not biz_id:
            continue
        for tag_name in tag_names:
            tag_obj = tag_map.get(tag_name)
            if tag_obj:
                through_records.append(ThroughModel(business_id=biz_id, tag_id=tag_obj.id))

    if through_records:
        ThroughModel.objects.bulk_create(through_records, ignore_conflicts=True, batch_size=500)

    created_ids = [id_map[pid] for pid in created_pids if pid in id_map]
    logger.info("Bulk-created %d businesses", len(created_ids))
    return created_ids


def _generate_embeddings(client: openai.OpenAI, business_ids: list[int]):
    """
    Generate embeddings for businesses with tags baked into the text.
    Uses 4 concurrent workers to process batches in parallel.
    """
    if not business_ids:
        return

    businesses = list(
        Business.objects.filter(id__in=business_ids)
        .select_related('category', 'category__parent')
        .prefetch_related('tags')
    )

    batch_size = 100
    batches = [businesses[i:i + batch_size] for i in range(0, len(businesses), batch_size)]

    def _embed_batch(batch):
        close_old_connections()  # ensure fresh DB connection in thread
        texts = []
        for biz in batch:
            tag_str = ', '.join(t.name for t in biz.tags.all())
            cat_str = ''
            if biz.category:
                if biz.category.parent:
                    cat_str = f"{biz.category.parent.name} > {biz.category.name}"
                else:
                    cat_str = biz.category.name
            text = f"{biz.name}."
            if cat_str:
                text += f" Category: {cat_str}."
            if biz.description:
                text += f" {biz.description}"
            if tag_str:
                text += f" Tags: {tag_str}."
            if biz.address:
                text += f" Located at {biz.address}"
            texts.append(text.strip())

        try:
            response = client.embeddings.create(
                model='text-embedding-3-small',
                input=texts,
            )
            for j, item in enumerate(response.data):
                Business.objects.filter(id=batch[j].id).update(embedding=item.embedding)
        except Exception as e:
            logger.error("Embedding generation error: %s", e)

    # 4 concurrent workers for embedding generation
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_embed_batch, b) for b in batches]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error("Embedding worker error: %s", e)
