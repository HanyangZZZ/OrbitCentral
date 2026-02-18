"""
Business creation — bulk-create Business records from classified Google Places data.
"""
import logging

from django.contrib.gis.geos import Point

from ..models import Business, Category, Tag

logger = logging.getLogger('api')

# ── Price level mapping ────────────────────────────────────────────────────────
PRICE_LEVEL_MAP = {
    'PRICE_LEVEL_FREE': 0, 'PRICE_LEVEL_INEXPENSIVE': 1,
    'PRICE_LEVEL_MODERATE': 2, 'PRICE_LEVEL_EXPENSIVE': 3,
    'PRICE_LEVEL_VERY_EXPENSIVE': 4,
}

# ── Keyword fallback for AI category variations ───────────────────────────────
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

        # Extract extended Google Places data
        opening_hours = place.get('regularOpeningHours') or place.get('currentOpeningHours')
        reviews_raw = place.get('reviews', [])
        reviews_data = [
            {
                'author': r.get('authorAttribution', {}).get('displayName', ''),
                'rating': r.get('rating'),
                'text': r.get('text', {}).get('text', ''),
                'time': r.get('publishTime', ''),
            }
            for r in (reviews_raw or [])
        ] or None

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
            google_rating=place.get('rating', 0) or 0,
            avg_rating=place.get('rating', 0) or 0,
            user_rating_count=place.get('userRatingCount', 0) or 0,
            onboarding_status='discovered',
            image_url=None,  # set by GCS pipeline in Step 6.5
            # Extended Google Places data
            opening_hours=opening_hours,
            google_maps_uri=place.get('googleMapsUri', '') or None,
            reviews_data=reviews_data,
            accessibility=place.get('accessibilityOptions') or None,
            payment_options=place.get('paymentOptions') or None,
            parking=place.get('parkingOptions') or None,
            dine_in=place.get('dineIn'),
            takeout=place.get('takeout'),
            delivery=place.get('delivery'),
            reservable=place.get('reservable'),
            serves_beer=place.get('servesBeer'),
            serves_wine=place.get('servesWine'),
            serves_breakfast=place.get('servesBreakfast'),
            serves_lunch=place.get('servesLunch'),
            serves_dinner=place.get('servesDinner'),
            serves_brunch=place.get('servesBrunch'),
            outdoor_seating=place.get('outdoorSeating'),
            live_music=place.get('liveMusic'),
            good_for_children=place.get('goodForChildren'),
            good_for_groups=place.get('goodForGroups'),
            allows_dogs=place.get('allowsDogs'),
            restroom=place.get('restroom'),
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
