"""
Area coverage import task — wraps the import pipeline with Celery retry logic.
"""
import logging

from celery import shared_task

logger = logging.getLogger('api')


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    reject_on_worker_lost=True,
    ignore_result=True,
)
def ensure_area_covered_task(self, lat: float, lng: float):
    """
    Import businesses from Google Places for the given coordinates.

    This wraps services.ensure_area_covered() with Celery retry logic.
    Called from BusinessViewSet.vector_search() via:
        ensure_area_covered_task.delay(lat, lng)
    """
    from ..services import ensure_area_covered  # deferred import to avoid circular imports

    try:
        logger.info("Celery task: ensure_area_covered(%.4f, %.4f)", lat, lng)
        ensure_area_covered(lat, lng)
        logger.info("Celery task: area coverage complete for (%.4f, %.4f)", lat, lng)
    except Exception as exc:
        logger.warning(
            "Celery task: ensure_area_covered failed (attempt %d/3): %s",
            self.request.retries + 1, exc,
        )
        raise self.retry(exc=exc)
