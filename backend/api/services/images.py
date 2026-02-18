"""
Image pipeline — download from Google Places Photo API & upload to GCS.
"""
import logging

from ..models import Business
from .gcs import _download_and_upload_images

logger = logging.getLogger('api')


def _download_and_store_images(business_ids: list[int], google_api_key: str):
    """
    For each newly created business with photo_references,
    download the first image from Google Places Photo API and upload
    to the GCS bucket. Updates the business's image_url to the public
    GCS URL.
    """
    if not business_ids:
        return

    # Fetch businesses that have photo references
    businesses = list(
        Business.objects.filter(id__in=business_ids, photo_references__isnull=False)
        .exclude(photo_references=[])
        .values_list('id', 'photo_references')
    )

    if not businesses:
        logger.info("No businesses with photo_references to download")
        return

    # Build (business_id, [refs]) list
    biz_photo_pairs = [(biz_id, refs) for biz_id, refs in businesses if refs]

    # Download from Google & upload to GCS (8 concurrent workers)
    image_urls = _download_and_upload_images(biz_photo_pairs, google_api_key)

    # Bulk update image_url for all businesses that got images
    if image_urls:
        for biz_id, url in image_urls.items():
            Business.objects.filter(id=biz_id).update(image_url=url)
        logger.info("Updated image_url for %d businesses (GCS bucket)", len(image_urls))
