"""
Google Cloud Storage helpers — lazy client, photo download, image upload.
"""
import logging
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from django.conf import settings
from google.cloud import storage as gcs_storage

logger = logging.getLogger('api')

# ── GCS client (lazy-initialized) ─────────────────────────────────────────────
_gcs_client = None


def _get_gcs_client():
    """Lazy-init GCS client. Uses Application Default Credentials."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = gcs_storage.Client()
    return _gcs_client


def _download_google_photo(photo_ref: str, api_key: str, max_height: int = 800) -> bytes | None:
    """Download a single photo from Google Places Photo API.
    Returns raw image bytes or None on failure."""
    url = (
        f'https://places.googleapis.com/v1/{photo_ref}/media'
        f'?maxHeightPx={max_height}&skipHttpRedirect=true'
    )
    headers = {'X-Goog-Api-Key': api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            photo_url = data.get('photoUri')
            if photo_url:
                img_resp = requests.get(photo_url, timeout=20)
                if img_resp.status_code == 200:
                    return img_resp.content
        # Fallback: direct redirect (some photos return image directly)
        if resp.headers.get('content-type', '').startswith('image/'):
            return resp.content
    except Exception as e:
        logger.warning("Photo download failed for %s: %s", photo_ref, e)
    return None


def _upload_image_to_gcs(business_id: int, image_bytes: bytes,
                         image_index: int = 1, content_type: str = 'image/jpeg') -> str:
    """Upload image bytes to GCS and return the public URL."""
    bucket_name = getattr(settings, 'GCS_BUCKET_NAME', 'orbit-media-prod')
    public_base = getattr(settings, 'GCS_PUBLIC_URL',
                          f'https://storage.googleapis.com/{bucket_name}')
    blob_path = f'businesses/{business_id}/{image_index}.jpg'
    try:
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_string(image_bytes, content_type=content_type)
        return f'{public_base}/{blob_path}'
    except Exception as e:
        logger.error("GCS upload failed for business %d: %s", business_id, e)
        return ''


def _download_and_upload_images(business_ids_photos: list[tuple[int, list[str]]],
                                api_key: str) -> dict[int, str]:
    """Download images from Google Places and upload to GCS.
    Takes list of (business_id, [photo_references]).
    Returns {business_id: public_image_url}.

    Downloads only the first photo per business to control costs.
    Uses 8 concurrent workers for parallel downloading.
    """
    results: dict[int, str] = {}
    if not business_ids_photos:
        return results

    lock = threading.Lock()

    def _process_one(biz_id: int, photo_refs: list[str]):
        if not photo_refs:
            return
        # Download first photo only
        img_bytes = _download_google_photo(photo_refs[0], api_key)
        if not img_bytes:
            return
        # Upload to GCS
        url = _upload_image_to_gcs(biz_id, img_bytes, image_index=1)
        if url:
            with lock:
                results[biz_id] = url

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(_process_one, biz_id, refs): biz_id
            for biz_id, refs in business_ids_photos
        }
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.warning("Image pipeline error: %s", e)

    logger.info("Downloaded & uploaded %d/%d business images to GCS",
                len(results), len(business_ids_photos))
    return results
