from django.db import models


class Review(models.Model):
    user = models.ForeignKey(
        'api.User', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='reviews',
    )
    business = models.ForeignKey(
        'api.Business', on_delete=models.CASCADE, related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField()
    content = models.TextField(blank=True, null=True)
    ai_fraud_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_between_1_5',
            ),
        ]
        indexes = [
            models.Index(fields=['ai_fraud_score'], name='idx_review_fraud'),
        ]

    def __str__(self) -> str:
        return f"Review {self.id}"
