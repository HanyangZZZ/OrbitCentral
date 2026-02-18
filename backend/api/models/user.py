"""
User-related models: UserProfile and EmailVerificationToken.

We use a OneToOneField to auth.User (rather than a custom User model) so we
can extend the schema freely without touching Django's auth tables.  A catch-all
``metadata`` JSONField is included for future fields that aren't worth a migration.
"""
import secrets

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended profile attached to every Django User.

    Core fields live as real columns for queryability; everything speculative
    goes into ``metadata`` so adding new data never needs a migration.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    # ── Display / identity ─────────────────────────────────────────────────────
    display_name = models.CharField(max_length=150, blank=True, default='')
    avatar_url = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    # ── Verification ───────────────────────────────────────────────────────────
    email_verified = models.BooleanField(
        default=False,
        help_text='Set to True after the user clicks the verification link.',
    )

    # ── Catch-all for future data ──────────────────────────────────────────────
    metadata = models.JSONField(
        blank=True, null=True,
        help_text='Arbitrary key-value data.  Use this for everything that '
                  'does not yet justify its own column.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self) -> str:
        return f'Profile({self.user.username})'


class EmailVerificationToken(models.Model):
    """
    One-time token sent to the user's email.

    Each token is valid for ``TOKEN_LIFETIME`` (default 5 min).  Once consumed
    the ``used`` flag is set so it cannot be replayed.
    """
    TOKEN_LIFETIME = timezone.timedelta(minutes=5)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_tokens',
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Token({self.user.username}, used={self.used})'

    @classmethod
    def create_for_user(cls, user):
        """Generate a fresh token and return the model instance (saved)."""
        token = secrets.token_urlsafe(48)
        now = timezone.now()
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=now + cls.TOKEN_LIFETIME,
        )

    @property
    def is_valid(self) -> bool:
        return not self.used and timezone.now() < self.expires_at


class PasswordResetToken(models.Model):
    """
    One-time token for password reset.  Same pattern as EmailVerificationToken.
    Valid for 1 hour.  Once consumed the ``used`` flag is set.
    """
    TOKEN_LIFETIME = timezone.timedelta(hours=1)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'PwReset({self.user.username}, used={self.used})'

    @classmethod
    def create_for_user(cls, user):
        token = secrets.token_urlsafe(48)
        now = timezone.now()
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=now + cls.TOKEN_LIFETIME,
        )

    @property
    def is_valid(self) -> bool:
        return not self.used and timezone.now() < self.expires_at


# ── Auto-create profile on User creation ──────────────────────────────────────
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Ensure every new User immediately gets a UserProfile."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
