"""
Management command: import nearby businesses from Google Places API (New).

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

PLACES_ENDPOINT = 'https://places.googleapis.com/v1/places:searchNearby'

FIELD_MASK = ','.join([
    'places.id',
    'places.displayName',
    'places.formattedAddress',
    'places.location',
    'places.rating',
    'places.userRatingCount',
    'places.types',
    'places.primaryType',
    'places.editorialSummary',
    'places.websiteUri',
    'places.internationalPhoneNumber',
    'places.photos',
    'places.businessStatus',
    'places.priceLevel',
])

PRICE_LEVEL_MAP = {
    'PRICE_LEVEL_FREE': 0,
    'PRICE_LEVEL_INEXPENSIVE': 1,
    'PRICE_LEVEL_MODERATE': 2,
    'PRICE_LEVEL_EXPENSIVE': 3,
    'PRICE_LEVEL_VERY_EXPENSIVE': 4,
}


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
            }

            if category:
                defaults['category'] = category

            # Use first photo as image_url placeholder (via Places Photos API)
            if photo_refs:
                defaults['image_url'] = (
                    f'https://places.googleapis.com/v1/{photo_refs[0]}/media'
                    f'?maxHeightPx=400&key={api_key}'
                )

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
