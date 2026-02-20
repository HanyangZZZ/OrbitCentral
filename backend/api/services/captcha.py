"""
Google reCAPTCHA verification service.

Supports BOTH reCAPTCHA v2 (invisible / checkbox) and v3 (score-based).
Automatically detects the version from Google's response:
  - v2: response has 'success' but no 'score'  → pass/fail + optional challenge
  - v3: response has 'success' and 'score'      → score checked against threshold

Multi-layer verification flow:
  Layer 1 — Invisible: reCAPTCHA silently evaluates user behavior.
  Layer 2 — Challenge: If suspicious, Google shows image/click/drag challenge (v2).

Disabled gracefully when RECAPTCHA_SECRET_KEY is not set (dev/testing).
"""
import logging
import os

import requests

logger = logging.getLogger('api')

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_SCORE_THRESHOLD = float(os.environ.get('RECAPTCHA_SCORE_THRESHOLD', '0.5'))


def verify_captcha(token: str, expected_action: str | None = None) -> dict:
    """
    Verify a reCAPTCHA token (v2 or v3) with Google.

    Args:
        token: The g-recaptcha-response token from the frontend.
        expected_action: (v3 only) Expected action string to verify.

    Returns:
        dict with keys:
            success (bool): Whether the captcha passed
            score (float|None): reCAPTCHA score (v3 only; 0.0 = bot, 1.0 = human)
            error (str|None): Error message if verification failed

    If RECAPTCHA_SECRET_KEY is not set, always returns success (dev mode).
    """
    # ── Dev mode: captcha disabled ──────────────────────────────────────
    if not RECAPTCHA_SECRET_KEY:
        logger.debug('reCAPTCHA disabled (no RECAPTCHA_SECRET_KEY)')
        return {'success': True, 'score': None, 'error': None}

    if not token:
        return {'success': False, 'score': None, 'error': 'Missing captcha token.'}

    # ── Call Google siteverify ──────────────────────────────────────────
    try:
        resp = requests.post(RECAPTCHA_VERIFY_URL, data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': token,
        }, timeout=5)
        data = resp.json()
    except Exception as exc:
        logger.error('reCAPTCHA verification request failed: %s', exc)
        # Fail closed — block request if Google is unreachable
        return {'success': False, 'score': None, 'error': 'Captcha service unavailable. Please try again.'}

    # ── Basic success check (both v2 and v3) ───────────────────────────
    if not data.get('success'):
        error_codes = data.get('error-codes', [])
        logger.info('reCAPTCHA failed: %s', error_codes)
        return {'success': False, 'score': None, 'error': f'Captcha verification failed: {error_codes}'}

    # ── v2 invisible / checkbox: no score field → success is enough ────
    score = data.get('score')
    if score is None:
        logger.debug('reCAPTCHA v2 passed (no score)')
        return {'success': True, 'score': None, 'error': None}

    # ── v3 score-based: verify action + threshold ──────────────────────
    action = data.get('action', '')
    if expected_action and action != expected_action:
        logger.warning('reCAPTCHA action mismatch: expected=%s got=%s', expected_action, action)
        return {'success': False, 'score': score, 'error': 'Captcha action mismatch.'}

    if score < RECAPTCHA_SCORE_THRESHOLD:
        logger.info('reCAPTCHA score too low: %.2f < %.2f', score, RECAPTCHA_SCORE_THRESHOLD)
        return {'success': False, 'score': score, 'error': 'Captcha score too low. Please try again.'}

    return {'success': True, 'score': score, 'error': None}
