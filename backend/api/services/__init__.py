"""
Services package — auto-import pipeline, GCS helpers, AI classification.

Public API:
    ensure_area_covered(lat, lng)   — import businesses for an unsearched area
    _get_gcs_client()               — lazy-initialized GCS client
"""
from .gcs import _get_gcs_client
from .import_pipeline import ensure_area_covered

__all__ = ['ensure_area_covered', '_get_gcs_client']
