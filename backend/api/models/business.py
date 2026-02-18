from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
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

    # ── Extended Google Places data (fetched once, stored forever) ─────────────
    opening_hours = models.JSONField(
        blank=True, null=True,
        help_text='Google Places opening hours object (periods + weekday text)',
    )
    google_maps_uri = models.URLField(max_length=2000, blank=True, null=True)
    reviews_data = models.JSONField(
        blank=True, null=True,
        help_text='Google Places reviews array (up to 5 reviews)',
    )
    accessibility = models.JSONField(
        blank=True, null=True,
        help_text='Wheelchair accessible entrance/parking/seating/restroom',
    )
    payment_options = models.JSONField(
        blank=True, null=True,
        help_text='Accepted payment methods (credit cards, debit, NFC, cash)',
    )
    parking = models.JSONField(
        blank=True, null=True,
        help_text='Parking options (free, paid, street, garage, valet)',
    )
    dine_in = models.BooleanField(null=True, blank=True)
    takeout = models.BooleanField(null=True, blank=True)
    delivery = models.BooleanField(null=True, blank=True)
    reservable = models.BooleanField(null=True, blank=True)
    serves_beer = models.BooleanField(null=True, blank=True)
    serves_wine = models.BooleanField(null=True, blank=True)
    serves_breakfast = models.BooleanField(null=True, blank=True)
    serves_lunch = models.BooleanField(null=True, blank=True)
    serves_dinner = models.BooleanField(null=True, blank=True)
    serves_brunch = models.BooleanField(null=True, blank=True)
    outdoor_seating = models.BooleanField(null=True, blank=True)
    live_music = models.BooleanField(null=True, blank=True)
    good_for_children = models.BooleanField(null=True, blank=True)
    good_for_groups = models.BooleanField(null=True, blank=True)
    allows_dogs = models.BooleanField(null=True, blank=True)
    restroom = models.BooleanField(null=True, blank=True)

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
    google_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text='Rating from Google Places API (stored once during import, never auto-changed)',
    )
    avg_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text='Display rating: Bayesian estimate when user reviews exist, else google_rating',
    )
    review_count = models.IntegerField(
        default=0,
        help_text='Number of user reviews on our platform',
    )
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


class Review(models.Model):
    """User-submitted review for a business."""
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='user_reviews',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='reviews',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    description = models.TextField(blank=True, default='')
    image_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'user'],
                name='unique_review_per_user_per_business',
                condition=models.Q(user__isnull=False),
            ),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Review by {self.user} for {self.business.name} ({self.rating}/5)'


class ReviewVote(models.Model):
    """Helpfulness vote on a review (useful / funny / cool)."""
    VOTE_TYPES = (
        ('useful', 'Useful'),
        ('funny', 'Funny'),
        ('cool', 'Cool'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_votes',
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='votes',
    )
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_votes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review', 'vote_type'],
                name='unique_vote_per_user_per_review_per_type',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} → {self.vote_type} on review #{self.review_id}'


class Bookmark(models.Model):
    """User bookmark for a business — simple toggle (save/unsave)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks',
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='bookmarks',
    )
    note = models.CharField(max_length=500, blank=True, default='',
                            help_text='Optional private note for the user')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'business'],
                name='unique_bookmark_per_user_per_business',
            ),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.user} → {self.business.name}'


# ── Bayesian rating config ─────────────────────────────────────────────────────
# m = confidence threshold: how many user reviews before our ratings "take over"
# from the Google prior.  With m=10, a business needs ~10 user reviews before
# its Bayesian avg is dominated by user scores rather than Google's score.
BAYESIAN_CONFIDENCE_THRESHOLD = 10


# ── Signals: keep Business.avg_rating / review_count in sync ───────────────────
@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_business_review_aggregates(sender, instance, **kwargs):
    """
    Recalculate avg_rating using a Bayesian estimate.

    Formula:  W = (v * R + m * C) / (v + m)
      v = number of user reviews on our platform
      R = average of our user reviews
      m = confidence threshold (BAYESIAN_CONFIDENCE_THRESHOLD)
      C = google_rating (the prior — Google's established rating)

    When v=0:  W = C  (pure Google rating)
    As v grows: W → R  (our user reviews dominate)
    """
    biz = instance.business
    agg = Review.objects.filter(business=biz).aggregate(
        avg=models.Avg('rating'),
        count=models.Count('id'),
    )
    v = agg['count']
    R = float(agg['avg'] or 0)
    m = BAYESIAN_CONFIDENCE_THRESHOLD
    C = float(biz.google_rating or 0)

    if v == 0:
        # No user reviews — fall back to Google rating
        bayesian_avg = C
    else:
        bayesian_avg = (v * R + m * C) / (v + m)

    biz.avg_rating = round(bayesian_avg, 2)
    biz.review_count = v
    biz.save(update_fields=['avg_rating', 'review_count'])
