"""
Management command: import nearby businesses from Google Places API (New).

Fetches all available fields (atmosphere, amenities, hours, reviews) in a
single Nearby Search call per batch, downloads the first photo to GCS, and
stores the public URL — the Google API is never called again for the same
business.

Usage:
    python manage.py import_places --lat=-33.8688 --lng=151.2093
    python manage.py import_places --lat=-33.8688 --lng=151.2093 --radius=3000
    python manage.py import_places --lat=-33.8688 --lng=151.2093 --types=restaurant,cafe
    python manage.py import_places --lat=-33.8688 --lng=151.2093 --embed
"""
import os
import time

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from api.services.google_places import FIELD_MASK, PLACES_ENDPOINT
from api.services.businesses import PRICE_LEVEL_MAP
from api.services.images import _download_and_store_images


def _extract_reviews(place: dict) -> list[dict] | None:
    """Extract review data from a Google Places response dict."""
    reviews_raw = place.get('reviews', [])
    if not reviews_raw:
        return None
    return [
        {
            'author': r.get('authorAttribution', {}).get('displayName', ''),
            'rating': r.get('rating'),
            'text': r.get('text', {}).get('text', ''),
            'time': r.get('publishTime', ''),
        }
        for r in reviews_raw
    ] or None


class Command(BaseCommand):
    help = 'Import nearby businesses from Google Places API (New) and optionally generate embeddings.'

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=float, required=True, help='Center latitude')
        parser.add_argument('--lng', type=float, required=True, help='Center longitude')
        parser.add_argument('--radius', type=float, default=5000.0,
                            help='Search radius in metres (default 5000, max 50000)')
        parser.add_argument('--types', type=str, default='',
                            help='Comma-separated Google Place types to include, e.g. "restaurant,cafe"')
        parser.add_argument('--max-results', type=int, default=20,
                            help='Max results per request (1–20, default 20)')
        parser.add_argument('--embed', action='store_true',
                            help='Auto-generate OpenAI embeddings for newly imported businesses')
        parser.add_argument('--category', type=str, default='',
                            help='Assign imported businesses to this category slug (created if missing)')

    def handle(self, *args, **options):
        api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'GOOGLE_PLACES_API_KEY is not set. Add it to your .env file.'
            ))
            return

        lat = options['lat']
        lng = options['lng']
        radius = min(options['radius'], 50000.0)
        max_results = min(options['max_results'], 20)

        # Build request body
        body = {
            'maxResultCount': max_results,
            'locationRestriction': {
                'circle': {
                    'center': {'latitude': lat, 'longitude': lng},
                    'radius': radius,
                },
            },
        }
        if options['types']:
            body['includedTypes'] = [t.strip() for t in options['types'].split(',') if t.strip()]

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': FIELD_MASK,
        }

        self.stdout.write(f'Searching Google Places within {radius}m of ({lat}, {lng})...')

        resp = requests.post(PLACES_ENDPOINT, json=body, headers=headers, timeout=30)
        if resp.status_code != 200:
            self.stderr.write(self.style.ERROR(
                f'Google Places API error {resp.status_code}: {resp.text}'
            ))
            return

        places = resp.json().get('places', [])
        self.stdout.write(f'Found {len(places)} places from Google.')

        if not places:
            return

        # Resolve category if provided
        category = None
        if options['category']:
            from api.models import Category
            category, created = Category.objects.get_or_create(
                slug=options['category'],
                defaults={'name': options['category'].replace('-', ' ').title()},
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')

        # Import places
        from api.models import Business

        created_count = 0
        updated_count = 0
        new_ids = []

        for place in places:
            google_id = place.get('id', '')
            if not google_id:
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

            opening_hours = place.get('regularOpeningHours') or place.get('currentOpeningHours')

            defaults = {
                'name': display_name,
                'description': editorial or None,
                'address': place.get('formattedAddress', ''),
                'location': location,
                'phone': place.get('internationalPhoneNumber', '') or None,
                'website_url': place.get('websiteUri', '') or None,
                'google_types': place.get('types', []) or None,
                'price_level': price_level,
                'photo_references': photo_refs,
                'business_status': place.get('businessStatus', '') or None,
                'avg_rating': place.get('rating', 0) or 0,
                'user_rating_count': place.get('userRatingCount', 0) or 0,
                # Extended Google Places data (fetched once, stored forever)
                'opening_hours': opening_hours,
                'google_maps_uri': place.get('googleMapsUri', '') or None,
                'reviews_data': _extract_reviews(place),
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

            if category:
                defaults['category'] = category

            # image_url is NOT set here — GCS pipeline handles it below

            biz, was_created = Business.objects.update_or_create(
                google_place_id=google_id,
                defaults=defaults,
            )

            if was_created:
                created_count += 1
                new_ids.append(biz.id)
                self.stdout.write(f'  + {display_name}')
            else:
                updated_count += 1
                self.stdout.write(f'  ~ {display_name} (updated)')

        self.stdout.write(self.style.SUCCESS(
            f'Import done. Created: {created_count}, Updated: {updated_count}'
        ))

        # ── Download images to GCS bucket ────────────────────────────────
        if new_ids:
            self.stdout.write('Downloading images to GCS...')
            _download_and_store_images(new_ids, api_key)
            self.stdout.write(self.style.SUCCESS('Image pipeline complete.'))

        # ── Optionally generate embeddings for new imports ───────────────
        if options['embed'] and new_ids:
            self._generate_embeddings(new_ids)

    def _generate_embeddings(self, business_ids: list[int]):
        """Generate OpenAI embeddings for the given business IDs."""
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

        self.stdout.write(f'Generating embeddings for {len(businesses)} new businesses...')

        texts = [
            f"{name}. {desc or ''} Located at {addr or ''}".strip()
            for _, name, desc, addr in businesses
        ]

        try:
            response = client.embeddings.create(
                model='text-embedding-3-small',
                input=texts,
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'OpenAI API error: {e}'))
            return

        for j, item in enumerate(response.data):
            biz_id = businesses[j][0]
            Business.objects.filter(id=biz_id).update(embedding=item.embedding)

        self.stdout.write(self.style.SUCCESS(
            f'Embeddings generated for {len(businesses)} businesses.'
        ))
