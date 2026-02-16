from django.contrib.gis.db import models as gis_models
from django.db import models
from pgvector.django import VectorField, HnswIndex


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        blank=True, null=True, related_name='children',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class Tag(models.Model):
    """
    Semantic tag for businesses (e.g. quiet, pet-friendly, wifi, cozy).
    Each tag has a vector embedding so we can deduplicate semantically —
    "pet-friendly" and "dog-friendly" resolve to the same tag.
    """
    name = models.CharField(max_length=100, unique=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']
        indexes = [
            HnswIndex(
                name='idx_tag_embedding',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self) -> str:
        return self.name


class SearchedArea(models.Model):
    """
    Tracks areas that have already been imported from Google Places.
    Before calling the Google API, we check if the user's location falls
    inside an existing SearchedArea circle — if so, skip the import.
    """
    center = gis_models.PointField(geography=True)
    radius_km = models.FloatField(default=5.0)
    business_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'searched_areas'

    def __str__(self) -> str:
        return f'({self.center.y:.4f}, {self.center.x:.4f}) r={self.radius_km}km'


class Business(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='businesses',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    google_place_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    # ── Google Places data ─────────────────────────────────────────────────────
    phone = models.CharField(max_length=30, blank=True, null=True)
    website_url = models.URLField(max_length=2000, blank=True, null=True)
    google_types = models.JSONField(
        blank=True, null=True,
        help_text='Google Places type array, e.g. ["restaurant","food","point_of_interest"]',
    )
    price_level = models.IntegerField(
        blank=True, null=True,
        help_text='Google price level: 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive',
    )
    photo_references = models.JSONField(
        blank=True, null=True,
        help_text='Google Places photo resource names for later retrieval',
    )
    business_status = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='Google Places business status, e.g. OPERATIONAL, CLOSED_TEMPORARILY',
    )

    # ── Tags (AI-generated, vector-deduplicated) ──────────────────────────────
    tags = models.ManyToManyField(Tag, blank=True, related_name='businesses')

    # ── Location (PostGIS geography point) ─────────────────────────────────────
    location = gis_models.PointField(geography=True, null=True, blank=True)

    # ── Vector embedding for semantic search (OpenAI text-embedding-3-small: 1536-dim) ──
    embedding = VectorField(dimensions=1536, null=True, blank=True)

    # ── Business status ────────────────────────────────────────────────────────
    onboarding_status = models.CharField(
        max_length=20,
        choices=(
            ('discovered', 'Discovered'),
            ('contacted', 'Contacted'),
            ('active', 'Active'),
        ),
        default='discovered',
    )

    # ── Aggregate fields ───────────────────────────────────────────────────────
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.IntegerField(default=0)
    user_rating_count = models.IntegerField(
        default=0,
        help_text='Total number of Google ratings (from Google Places)',
    )

    # ── Metadata ───────────────────────────────────────────────────────────────
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'businesses'
        verbose_name_plural = 'businesses'
        indexes = [
            models.Index(fields=['avg_rating'], name='idx_business_rating'),
            # HNSW index for fast approximate nearest-neighbor vector search
            HnswIndex(
                name='idx_business_embedding',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self) -> str:
        return self.name
