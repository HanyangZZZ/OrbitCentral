"""
Google Places API — config constants, grid generation, and place fetching.
"""
import logging
import math
import time
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logger = logging.getLogger('api')

# ── Config ─────────────────────────────────────────────────────────────────────
SEARCH_RADIUS_KM = 5.0
PLACES_ENDPOINT = 'https://places.googleapis.com/v1/places:searchNearby'

# Request ALL useful fields from Google Places — cost is per request, not per field.
FIELD_MASK = ','.join([
    'places.id', 'places.displayName', 'places.formattedAddress',
    'places.location', 'places.rating', 'places.userRatingCount',
    'places.types', 'places.primaryType', 'places.editorialSummary',
    'places.websiteUri', 'places.internationalPhoneNumber',
    'places.photos', 'places.businessStatus', 'places.priceLevel',
    # Extended fields (atmosphere / amenities / hours / reviews)
    'places.currentOpeningHours', 'places.regularOpeningHours',
    'places.googleMapsUri', 'places.reviews',
    'places.accessibilityOptions', 'places.paymentOptions',
    'places.parkingOptions',
    'places.dineIn', 'places.takeout', 'places.delivery',
    'places.reservable', 'places.servesBreakfast', 'places.servesLunch',
    'places.servesDinner', 'places.servesBrunch',
    'places.servesBeer', 'places.servesWine',
    'places.outdoorSeating', 'places.liveMusic',
    'places.goodForChildren', 'places.goodForGroups',
    'places.allowsDogs', 'places.restroom',
])

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
    lock = threading.Lock()

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
