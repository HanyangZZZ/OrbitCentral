"""
Google reCAPTCHA v3 verification.

Validates a reCAPTCHA token server-side against Google's siteverify endpoint.
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
    Verify a reCAPTCHA v3 token with Google.

    Returns:
        dict with keys:
            success (bool): Whether the captcha passed
            score (float|None): reCAPTCHA score (0.0 = bot, 1.0 = human)
            error (str|None): Error message if verification failed

    If RECAPTCHA_SECRET_KEY is not set, always returns success (dev mode).
    """
    if not RECAPTCHA_SECRET_KEY:
        logger.debug('reCAPTCHA disabled (no RECAPTCHA_SECRET_KEY)')
        return {'success': True, 'score': None, 'error': None}

    if not token:
        return {'success': False, 'score': None, 'error': 'Missing captcha token.'}

    try:
        resp = requests.post(RECAPTCHA_VERIFY_URL, data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': token,
        }, timeout=5)
        data = resp.json()
    except Exception as exc:
        logger.warning('reCAPTCHA verification request failed: %s', exc)
        # Fail open — don't block users if Google is down
        return {'success': True, 'score': None, 'error': None}

    if not data.get('success'):
        error_codes = data.get('error-codes', [])
        logger.info('reCAPTCHA failed: %s', error_codes)
        return {'success': False, 'score': None, 'error': f'Captcha verification failed: {error_codes}'}

    score = data.get('score', 0.0)
    action = data.get('action', '')

    # Verify action matches if specified
    if expected_action and action != expected_action:
        logger.warning('reCAPTCHA action mismatch: expected=%s got=%s', expected_action, action)
        return {'success': False, 'score': score, 'error': 'Captcha action mismatch.'}

    # Check score threshold
    if score < RECAPTCHA_SCORE_THRESHOLD:
        logger.info('reCAPTCHA score too low: %.2f < %.2f', score, RECAPTCHA_SCORE_THRESHOLD)
        return {'success': False, 'score': score, 'error': 'Captcha score too low. Please try again.'}

    return {'success': True, 'score': score, 'error': None}
