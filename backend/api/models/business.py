from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.name


class Business(models.Model):
    owner = models.ForeignKey(
        'api.User', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='businesses',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='businesses',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=10, decimal_places=8)
    lng = models.DecimalField(max_digits=11, decimal_places=8)
    google_place_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    onboarding_status = models.CharField(
        max_length=20,
        choices=(
            ('discovered', 'Discovered'),
            ('contacted', 'Contacted'),
            ('active', 'Active'),
        ),
        default='discovered',
    )
    contact_email = models.EmailField(blank=True, null=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.IntegerField(default=0)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'businesses'
        verbose_name_plural = 'businesses'
        indexes = [
            models.Index(fields=['avg_rating'], name='idx_business_rating'),
            models.Index(fields=['lat', 'lng'], name='idx_business_geo'),
        ]

    def __str__(self) -> str:
        return self.name
