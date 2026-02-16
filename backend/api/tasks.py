"""
Celery tasks for the API app.

Tasks are the bridge between Django views and background processing.
Instead of running expensive operations in request threads, views call
`task_name.delay(args)` which queues the work for a Celery worker.

Current tasks:
  - ensure_area_covered_task: Imports businesses from Google Places for an
    area that hasn't been imported yet. Called automatically during search
    when the user provides lat/lng coordinates.
"""
import logging

from celery import shared_task

logger = logging.getLogger('api')


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,       # seconds between retries
    acks_late=True,               # acknowledge after completion (crash-safe)
    reject_on_worker_lost=True,   # retry if the worker dies mid-task
    ignore_result=True,           # we don't need the return value
)
def ensure_area_covered_task(self, lat: float, lng: float):
    """
    Import businesses from Google Places for the given coordinates.

    This wraps services.ensure_area_covered() with Celery retry logic.
    If the import fails (e.g., rate limit, network error), it retries
    up to 3 times with 30-second delays.

    Called from BusinessViewSet.vector_search() via:
        ensure_area_covered_task.delay(lat, lng)
    """
    from .services import ensure_area_covered  # import inside task to avoid circular imports

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
