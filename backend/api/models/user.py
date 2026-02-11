from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class User(models.Model):
    ROLE_CUSTOMER = 'customer'
    ROLE_MERCHANT = 'merchant'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_MERCHANT, 'Merchant'),
        (ROLE_ADMIN, 'Admin'),
    )

    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    is_verified_human = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.email

    # ── Password helpers ───────────────────────────────────────────────────
    def set_password(self, raw_password: str) -> None:
        """Hash and store the password using Django's password hashing."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a raw password against the stored hash."""
        return check_password(raw_password, self.password_hash)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile',
    )
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)
    high_contrast = models.BooleanField(default=False)
    keyboard_only_nav = models.BooleanField(default=False)
    persona_vector = models.JSONField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self) -> str:
        return self.display_name or self.user.email
