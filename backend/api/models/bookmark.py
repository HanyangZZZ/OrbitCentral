from django.db import models


class Bookmark(models.Model):
    user = models.ForeignKey(
        'api.User', on_delete=models.CASCADE, related_name='bookmarks',
    )
    business = models.ForeignKey(
        'api.Business', on_delete=models.CASCADE, related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'business'],
                name='unique_user_business_bookmark',
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.business_id}"
