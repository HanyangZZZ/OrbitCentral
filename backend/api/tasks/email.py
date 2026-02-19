"""
Email tasks — verification and password reset via Brevo (Sendinblue).
"""
import logging
from html import escape as html_escape

from celery import shared_task

logger = logging.getLogger('api')


# ── Email verification ─────────────────────────────────────────────────────────
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
    reject_on_worker_lost=True,
    ignore_result=True,
)
def send_verification_email_task(self, user_id: int, token: str):
    """
    Send an email-verification link to a user via Brevo (Sendinblue).

    Called after registration or when the user requests a new link:
        send_verification_email_task.delay(user.id, token_string)
    """
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException

    from django.conf import settings as django_settings
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("send_verification_email: user %d not found", user_id)
        return

    api_key = django_settings.BREVO_API_KEY
    if not api_key:
        logger.error("send_verification_email: BREVO_API_KEY not configured")
        return

    frontend_url = django_settings.FRONTEND_BASE_URL.rstrip('/')
    verify_url = f'{frontend_url}/verify-email?token={token}'

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    display_name = getattr(user, 'profile', None) and user.profile.display_name
    recipient_name = html_escape(display_name or user.username)

    html_content = f"""
    <div style="font-family: system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h2 style="color: #1e293b;">Welcome to Orbit!</h2>
        <p style="color: #475569; font-size: 15px;">
            Hi {recipient_name}, please verify your email address to unlock
            all features — including posting reviews and personalising your feed.
        </p>
        <a href="{verify_url}"
           style="display: inline-block; padding: 12px 28px; background: #6366f1;
                  color: #fff; text-decoration: none; border-radius: 8px;
                  font-weight: 600; font-size: 15px; margin: 16px 0;">
            Verify My Email
        </a>
        <p style="color: #94a3b8; font-size: 13px;">
            Or copy this link:<br>
            <a href="{verify_url}" style="color: #6366f1; word-break: break-all;">{verify_url}</a>
        </p>
        <p style="color: #94a3b8; font-size: 12px;">This link expires in 5 minutes.</p>
    </div>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{'email': user.email, 'name': recipient_name}],
        sender={
            'email': django_settings.BREVO_SENDER_EMAIL,
            'name': django_settings.BREVO_SENDER_NAME,
        },
        subject='Verify your Orbit email address',
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(
            "Verification email sent to %s (message_id=%s)",
            user.email, response.message_id,
        )
    except ApiException as exc:
        logger.warning(
            "Brevo send failed (attempt %d/3): %s",
            self.request.retries + 1, exc,
        )
        raise self.retry(exc=exc)


# ── Password reset ─────────────────────────────────────────────────────────────
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
    reject_on_worker_lost=True,
    ignore_result=True,
)
def send_password_reset_email_task(self, user_id: int, token: str):
    """
    Send a password-reset link to a user via Brevo (Sendinblue).

    Called from AuthViewSet.forgot_password:
        send_password_reset_email_task.delay(user.id, token_string)
    """
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException

    from django.conf import settings as django_settings
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("send_password_reset_email: user %d not found", user_id)
        return

    api_key = django_settings.BREVO_API_KEY
    if not api_key:
        logger.error("send_password_reset_email: BREVO_API_KEY not configured")
        return

    frontend_url = django_settings.FRONTEND_BASE_URL.rstrip('/')
    reset_url = f'{frontend_url}/reset-password?token={token}'

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    display_name = getattr(user, 'profile', None) and user.profile.display_name
    recipient_name = html_escape(display_name or user.username)

    html_content = f"""
    <div style="font-family: system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h2 style="color: #1e293b;">Reset Your Password</h2>
        <p style="color: #475569; font-size: 15px;">
            Hi {recipient_name}, we received a request to reset your Orbit password.
            Click the button below to choose a new password.
        </p>
        <a href="{reset_url}"
           style="display: inline-block; padding: 12px 28px; background: #6366f1;
                  color: #fff; text-decoration: none; border-radius: 8px;
                  font-weight: 600; font-size: 15px; margin: 16px 0;">
            Reset Password
        </a>
        <p style="color: #94a3b8; font-size: 13px;">
            Or copy this link:<br>
            <a href="{reset_url}" style="color: #6366f1; word-break: break-all;">{reset_url}</a>
        </p>
        <p style="color: #94a3b8; font-size: 12px;">
            This link expires in 1 hour. If you did not request a password reset,
            you can safely ignore this email.
        </p>
    </div>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{'email': user.email, 'name': recipient_name}],
        sender={
            'email': django_settings.BREVO_SENDER_EMAIL,
            'name': django_settings.BREVO_SENDER_NAME,
        },
        subject='Reset your Orbit password',
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(
            "Password reset email sent to %s (message_id=%s)",
            user.email, response.message_id,
        )
    except ApiException as exc:
        logger.warning(
            "Brevo send failed (attempt %d/3): %s",
            self.request.retries + 1, exc,
        )
        raise self.retry(exc=exc)
