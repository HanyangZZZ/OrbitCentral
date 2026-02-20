"""
Google Geocoding — reverse-geocode (lat, lng) → city + province.

Uses the Google Maps Geocoding API with the same API key as Google Places.
Docs: https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding
"""
import logging
import os

import requests

logger = logging.getLogger('api')

GEOCODING_ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'


def reverse_geocode(lat: float, lng: float) -> dict:
    """
    Convert coordinates to a city and province/state.

    Returns:
        {
            "city": "Toronto",
            "province": "Ontario",
            "province_code": "ON",
            "country": "Canada",
            "country_code": "CA",
            "formatted_address": "Toronto, ON, Canada",
        }

    Raises ValueError if no locality result is found.
    Raises RuntimeError on API errors.
    """
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
    if not api_key:
        raise RuntimeError('GOOGLE_PLACES_API_KEY is not set')

    params = {
        'latlng': f'{lat},{lng}',
        'key': api_key,
        'result_type': 'locality',        # city-level results only
        'language': 'en',
    }

    resp = requests.get(GEOCODING_ENDPOINT, params=params, timeout=10)
    data = resp.json()

    status = data.get('status')
    if status not in ('OK', 'ZERO_RESULTS'):
        error_msg = data.get('error_message', status)
        logger.error('Geocoding API error: %s — %s', status, error_msg)
        raise RuntimeError(f'Geocoding API error: {error_msg}')

    results = data.get('results', [])
    if not results:
        raise ValueError(f'No locality found for coordinates ({lat}, {lng})')

    # Parse address components from the first (most relevant) result
    components = results[0].get('address_components', [])
    city = province = province_code = country = country_code = None

    for comp in components:
        types = comp.get('types', [])
        if 'locality' in types:
            city = comp['long_name']
        elif 'administrative_area_level_1' in types:
            province = comp['long_name']
            province_code = comp['short_name']
        elif 'country' in types:
            country = comp['long_name']
            country_code = comp['short_name']

    if not city:
        # Fallback: some areas use sublocality or administrative_area_level_2
        for comp in components:
            types = comp.get('types', [])
            if 'sublocality' in types or 'administrative_area_level_2' in types:
                city = comp['long_name']
                break

    return {
        'city': city,
        'province': province,
        'province_code': province_code,
        'country': country,
        'country_code': country_code,
        'formatted_address': results[0].get('formatted_address', ''),
    }
