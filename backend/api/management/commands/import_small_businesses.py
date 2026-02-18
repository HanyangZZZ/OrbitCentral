"""
Bulk-import ~500 small, independent businesses around a location from Google Places.

Filters out chains, malls, big-box stores, supermarkets, and franchises.
Fetches all atmosphere/amenity/review data in a single Nearby Search call,
downloads the first photo to GCS, and stores the public URL.

Usage:
    python manage.py import_small_businesses --lat=43.6532 --lng=-79.3832
    python manage.py import_small_businesses --lat=43.6532 --lng=-79.3832 --target=500 --embed
"""
import math
import os
import time

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from api.services.google_places import FIELD_MASK, PLACES_ENDPOINT, SMALL_BIZ_TYPES
from api.services.businesses import PRICE_LEVEL_MAP
from api.services.images import _download_and_store_images

# ── Types to REJECT (big-box, institutional, etc.) ───────────────────────────
EXCLUDED_TYPES = {
    'shopping_mall', 'department_store', 'supermarket', 'grocery_or_supermarket',
    'convenience_store', 'gas_station', 'car_dealer', 'car_rental', 'car_repair',
    'car_wash', 'parking', 'hospital', 'school', 'university', 'church',
    'city_hall', 'courthouse', 'embassy', 'fire_station', 'police',
    'post_office', 'library', 'museum', 'airport', 'bus_station',
    'subway_station', 'train_station', 'transit_station', 'bank',
    'atm', 'insurance_agency', 'real_estate_agency', 'travel_agency',
    'movie_theater', 'stadium', 'amusement_park', 'zoo',
    'drugstore', 'pharmacy', 'dentist', 'doctor', 'physiotherapist',
    'veterinary_care', 'funeral_home', 'cemetery', 'storage',
    'moving_company', 'laundry', 'locksmith', 'plumber', 'electrician',
    'roofing_contractor', 'painter', 'general_contractor',
}

# ── Chain / franchise names to filter out (case-insensitive substring match) ─
CHAIN_BLOCKLIST = [
    'mcdonalds', "mcdonald's", 'burger king', 'wendy', 'subway',
    'starbucks', 'tim horton', 'tims', 'second cup',
    'pizza hut', 'domino', 'papa john', 'little caesars', 'pizza pizza',
    'kfc', 'popeyes', 'chick-fil-a', 'taco bell', 'chipotle',
    'five guys', 'a&w', 'harvey',
    'walmart', 'costco', 'target', 'dollarama', 'dollar tree',
    'no frills', 'nofrills', 'loblaws', 'sobeys', 'metro',
    'food basics', 'freshco', 'real canadian superstore', 'superstore',
    'shoppers drug mart', 'rexall', 'pharmasave',
    'winners', 'marshalls', 'homesense', 'value village',
    'canadian tire', 'home depot', 'home hardware', 'lowes', "lowe's",
    'best buy', 'staples', 'the source',
    'gap', 'old navy', 'h&m', 'zara', 'uniqlo', 'forever 21',
    'sephora', 'bath & body works', 'bath and body works',
    'ikea', 'structube',
    'scotiabank', 'td bank', 'rbc', 'bmo', 'cibc',
    'bell', 'rogers', 'telus', 'fido', 'koodo', 'virgin',
    'goodlife', 'fit4less', 'planet fitness', 'anytime fitness',
    'timmies', 'mary brown', 'swiss chalet', 'east side mario',
    'boston pizza', 'montana', 'the keg', 'milestones', 'earls',
    'jack astor', 'cactus club', 'joey', 'moxie',
    'panera', 'panda express', 'olive garden', 'red lobster',
    'denny', 'ihop', 'waffle house', 'applebee',
    'dunkin', 'krispy kreme', 'baskin robbins', 'dairy queen',
    '7-eleven', '7 eleven', 'circle k', 'shell', 'esso', 'petro-canada',
    'cf ', 'eaton centre', 'yorkdale', 'scarborough town',
]


def _is_chain(name: str) -> bool:
    """Return True if the name matches a known chain / franchise."""
    lower = name.lower()
    return any(chain in lower for chain in CHAIN_BLOCKLIST)


def _has_excluded_type(types: list[str]) -> bool:
    """Return True if any of the place's types are in the excluded set."""
    return bool(set(types or []) & EXCLUDED_TYPES)


def _generate_grid(center_lat: float, center_lng: float, radius_km: float, step_km: float):
    """
    Generate a grid of (lat, lng) points within `radius_km` of the center,
    spaced `step_km` apart. This helps cover more area since each API call
    only returns max 20 results in a small radius.
    """
    points = []
    km_per_deg_lat = 111.32
    km_per_deg_lng = 111.32 * math.cos(math.radians(center_lat))

    steps = int(radius_km / step_km)
    for dy in range(-steps, steps + 1):
        for dx in range(-steps, steps + 1):
            lat = center_lat + (dy * step_km) / km_per_deg_lat
            lng = center_lng + (dx * step_km) / km_per_deg_lng
            # Only include points within the radius
            dist = math.sqrt((dy * step_km) ** 2 + (dx * step_km) ** 2)
            if dist <= radius_km:
                points.append((lat, lng))
    return points


class Command(BaseCommand):
    help = 'Bulk-import small independent businesses from Google Places API.'

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=float, required=True, help='Center latitude')
        parser.add_argument('--lng', type=float, required=True, help='Center longitude')
        parser.add_argument('--radius', type=float, default=8.0,
                            help='Search radius in km (default 8)')
        parser.add_argument('--target', type=int, default=500,
                            help='Target number of businesses (default 500)')
        parser.add_argument('--embed', action='store_true',
                            help='Auto-generate embeddings after import')

    def handle(self, *args, **options):
        api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'GOOGLE_PLACES_API_KEY is not set. Add it to your .env file.'
            ))
            return

        lat = options['lat']
        lng = options['lng']
        radius_km = options['radius']
        target = options['target']

        from api.models import Business

        # Generate grid of search points
        grid = _generate_grid(lat, lng, radius_km, step_km=1.5)
        self.stdout.write(f'Generated {len(grid)} grid points within {radius_km}km of ({lat}, {lng})')
        self.stdout.write(f'Target: {target} small businesses')
        self.stdout.write(f'Using {len(SMALL_BIZ_TYPES)} business types')

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': FIELD_MASK,
        }

        seen_place_ids = set(
            Business.objects.exclude(google_place_id__isnull=True)
            .values_list('google_place_id', flat=True)
        )
        self.stdout.write(f'Already have {len(seen_place_ids)} businesses with google_place_id')

        created_count = 0
        skipped_chain = 0
        skipped_type = 0
        skipped_dup = 0
        api_calls = 0
        new_ids = []

        # Iterate through types, then grid points
        for biz_type in SMALL_BIZ_TYPES:
            if created_count >= target:
                break

            for (g_lat, g_lng) in grid:
                if created_count >= target:
                    break

                body = {
                    'maxResultCount': 20,
                    'includedTypes': [biz_type],
                    'locationRestriction': {
                        'circle': {
                            'center': {'latitude': g_lat, 'longitude': g_lng},
                            'radius': 1500.0,  # 1.5 km per point
                        },
                    },
                }

                try:
                    resp = requests.post(PLACES_ENDPOINT, json=body, headers=headers, timeout=30)
                    api_calls += 1
                except Exception as e:
                    self.stderr.write(f'  Request error: {e}')
                    continue

                if resp.status_code != 200:
                    # Skip errors (rate limit, etc.) gracefully
                    if resp.status_code == 429:
                        self.stdout.write('  Rate limited — sleeping 30s...')
                        time.sleep(30)
                    continue

                places = resp.json().get('places', [])

                for place in places:
                    google_id = place.get('id', '')
                    if not google_id or google_id in seen_place_ids:
                        skipped_dup += 1
                        continue

                    seen_place_ids.add(google_id)

                    display_name = place.get('displayName', {}).get('text', '')
                    types = place.get('types', [])

                    # Filter: skip chains
                    if _is_chain(display_name):
                        skipped_chain += 1
                        continue

                    # Filter: skip excluded types
                    if _has_excluded_type(types):
                        skipped_type += 1
                        continue

                    # Filter: skip very high rating counts (likely chains) — >5000 reviews
                    rating_count = place.get('userRatingCount', 0) or 0
                    if rating_count > 5000:
                        skipped_chain += 1
                        continue

                    loc = place.get('location', {})
                    p_lat = loc.get('latitude')
                    p_lng = loc.get('longitude')
                    location = Point(p_lng, p_lat, srid=4326) if p_lat and p_lng else None

                    editorial = place.get('editorialSummary', {}).get('text', '')
                    photos = place.get('photos', [])
                    photo_refs = [p.get('name', '') for p in photos if p.get('name')] if photos else None

                    price_str = place.get('priceLevel', '')
                    price_level = PRICE_LEVEL_MAP.get(price_str)

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

                    defaults = {
                        'name': display_name,
                        'description': editorial or None,
                        'address': place.get('formattedAddress', ''),
                        'location': location,
                        'phone': place.get('internationalPhoneNumber', '') or None,
                        'website_url': place.get('websiteUri', '') or None,
                        'google_types': types or None,
                        'price_level': price_level,
                        'photo_references': photo_refs,
                        'business_status': place.get('businessStatus', '') or None,
                        'avg_rating': place.get('rating', 0) or 0,
                        'user_rating_count': rating_count,
                        'onboarding_status': 'discovered',
                        # Extended Google Places data (fetched once, stored forever)
                        'opening_hours': opening_hours,
                        'google_maps_uri': place.get('googleMapsUri', '') or None,
                        'reviews_data': reviews_data,
                        'accessibility': place.get('accessibilityOptions') or None,
                        'payment_options': place.get('paymentOptions') or None,
                        'parking': place.get('parkingOptions') or None,
                        'dine_in': place.get('dineIn'),
                        'takeout': place.get('takeout'),
                        'delivery': place.get('delivery'),
                        'reservable': place.get('reservable'),
                        'serves_beer': place.get('servesBeer'),
                        'serves_wine': place.get('servesWine'),
                        'serves_breakfast': place.get('servesBreakfast'),
                        'serves_lunch': place.get('servesLunch'),
                        'serves_dinner': place.get('servesDinner'),
                        'serves_brunch': place.get('servesBrunch'),
                        'outdoor_seating': place.get('outdoorSeating'),
                        'live_music': place.get('liveMusic'),
                        'good_for_children': place.get('goodForChildren'),
                        'good_for_groups': place.get('goodForGroups'),
                        'allows_dogs': place.get('allowsDogs'),
                        'restroom': place.get('restroom'),
                    }

                    # image_url is NOT set here — GCS pipeline handles it below

                    biz, was_created = Business.objects.update_or_create(
                        google_place_id=google_id,
                        defaults=defaults,
                    )

                    if was_created:
                        created_count += 1
                        new_ids.append(biz.id)
                        if created_count % 50 == 0:
                            self.stdout.write(f'  Progress: {created_count}/{target} created')

                # Respect rate limits — small delay between API calls
                time.sleep(0.3)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. API calls: {api_calls}\n'
            f'  Created:        {created_count}\n'
            f'  Skipped (chain): {skipped_chain}\n'
            f'  Skipped (type):  {skipped_type}\n'
            f'  Skipped (dup):   {skipped_dup}'
        ))

        # ── Download images to GCS bucket ────────────────────────────────
        if new_ids:
            self.stdout.write(f'Downloading images to GCS for {len(new_ids)} businesses...')
            _download_and_store_images(new_ids, api_key)
            self.stdout.write(self.style.SUCCESS('Image pipeline complete.'))

        # ── Generate embeddings ──────────────────────────────────────────
        if options['embed'] and new_ids:
            self._generate_embeddings(new_ids, api_key)

    def _generate_embeddings(self, business_ids: list[int], places_api_key: str):
        """Batch-generate OpenAI embeddings for the given business IDs."""
        import openai
        from api.models import Business

        api_key = os.environ.get('OPENAI_API_KEY', '')
        if not api_key:
            self.stderr.write(self.style.WARNING(
                'OPENAI_API_KEY not set — skipping embedding generation.'
            ))
            return

        client = openai.OpenAI(api_key=api_key)
        businesses = list(
            Business.objects.filter(id__in=business_ids)
            .values_list('id', 'name', 'description', 'address')
        )

        total = len(businesses)
        self.stdout.write(f'\nGenerating embeddings for {total} new businesses...')

        batch_size = 100
        updated = 0

        for i in range(0, total, batch_size):
            batch = businesses[i:i + batch_size]
            texts = [
                f"{name}. {desc or ''} Located at {addr or ''}".strip()
                for _, name, desc, addr in batch
            ]

            try:
                response = client.embeddings.create(
                    model='text-embedding-3-small',
                    input=texts,
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'OpenAI API error: {e}'))
                time.sleep(5)
                continue

            for j, item in enumerate(response.data):
                biz_id = batch[j][0]
                Business.objects.filter(id=biz_id).update(embedding=item.embedding)
                updated += 1

            self.stdout.write(f'  Embedded {min(i + batch_size, total)}/{total}')
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f'Embeddings generated for {updated} businesses.'))
